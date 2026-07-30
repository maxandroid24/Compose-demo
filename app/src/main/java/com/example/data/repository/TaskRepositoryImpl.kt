package com.example.data.repository

import com.example.data.local.TaskDao
import com.example.data.mapper.toDomain
import com.example.data.mapper.toDto
import com.example.data.mapper.toEntity
import com.example.data.remote.SyncRequestDto
import com.example.data.remote.TaskApiService
import com.example.data.worker.WorkManagerScheduler
import com.example.domain.model.Category
import com.example.domain.model.Priority
import com.example.domain.model.SyncStatus
import com.example.domain.model.Task
import com.example.domain.model.TaskStats
import com.example.domain.repository.TaskRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Concrete implementation of [TaskRepository] in the Data Layer.
 *
 * Architectural Pattern & Decision Rationale:
 * - Offline-First Strategy: Reads always target Room local database first via [Flow] queries.
 *   This guarantees instant UI rendering without waiting for network responses or suffering
 *   from connection drops.
 * - Writes occur locally immediately with a flag (`PENDING_INSERT`, `PENDING_UPDATE`, or `PENDING_DELETE`).
 *   After local commit, [WorkManagerScheduler] triggers a background sync to send changes to Retrofit [TaskApiService].
 * - Why preferred over Network-First: Offline-first prevents app freezes, reduces cell data usage,
 *   and provides a reliable user experience regardless of signal quality.
 */
@Singleton
class TaskRepositoryImpl @Inject constructor(
    private val taskDao: TaskDao,
    private val apiService: TaskApiService,
    private val workManagerScheduler: WorkManagerScheduler
) : TaskRepository {

    override fun getTasks(): Flow<List<Task>> {
        return taskDao.getAllTasks().map { entities ->
            entities.map { it.toDomain() }
        }
    }

    override fun getTaskById(taskId: String): Flow<Task?> {
        return taskDao.getTaskById(taskId).map { entity ->
            entity?.toDomain()
        }
    }

    override fun getFilteredTasks(
        query: String,
        category: Category?,
        priority: Priority?,
        showCompletedOnly: Boolean?
    ): Flow<List<Task>> {
        return taskDao.getAllTasks().map { entities ->
            entities.map { it.toDomain() }
                .filter { task ->
                    val matchesQuery = query.isBlank() ||
                            task.title.contains(query, ignoreCase = true) ||
                            task.description.contains(query, ignoreCase = true)

                    val matchesCategory = category == null || task.category == category
                    val matchesPriority = priority == null || task.priority == priority
                    val matchesCompletion = showCompletedOnly == null || task.isCompleted == showCompletedOnly

                    matchesQuery && matchesCategory && matchesPriority && matchesCompletion
                }
        }
    }

    override fun getTaskStats(): Flow<TaskStats> {
        return taskDao.getAllTasks().map { entities ->
            val tasks = entities.map { it.toDomain() }
            val total = tasks.size
            val completed = tasks.count { it.isCompleted }
            val pending = total - completed
            val percentage = if (total > 0) (completed.toFloat() / total) * 100f else 0f
            val urgentPending = tasks.count { !it.isCompleted && it.priority == Priority.URGENT }

            TaskStats(
                totalCount = total,
                completedCount = completed,
                pendingCount = pending,
                completionPercentage = percentage,
                urgentPendingCount = urgentPending
            )
        }
    }

    override suspend fun addTask(task: Task) {
        val now = System.currentTimeMillis()
        val newTask = task.copy(
            updatedAtMillis = now,
            syncStatus = SyncStatus.PENDING_INSERT
        )
        taskDao.insertTask(newTask.toEntity())
        workManagerScheduler.scheduleOneTimeSync()
        workManagerScheduler.scheduleTaskReminder(newTask)
    }

    override suspend fun updateTask(task: Task) {
        val now = System.currentTimeMillis()
        val updatedTask = task.copy(
            updatedAtMillis = now,
            syncStatus = if (task.syncStatus == SyncStatus.PENDING_INSERT) SyncStatus.PENDING_INSERT else SyncStatus.PENDING_UPDATE
        )
        taskDao.updateTask(updatedTask.toEntity())
        workManagerScheduler.scheduleOneTimeSync()
        if (updatedTask.isCompleted) {
            workManagerScheduler.cancelTaskReminder(updatedTask.id)
        } else {
            workManagerScheduler.scheduleTaskReminder(updatedTask)
        }
    }

    override suspend fun deleteTask(taskId: String) {
        val existingEntity = taskDao.getTaskByIdSync(taskId)
        if (existingEntity != null) {
            workManagerScheduler.cancelTaskReminder(taskId)
            if (existingEntity.syncStatus == SyncStatus.PENDING_INSERT.name) {
                // If it was never sent to server, delete locally immediately
                taskDao.deleteTaskById(taskId)
            } else {
                // Mark for remote deletion during next sync run
                val markForDelete = existingEntity.toDomain().copy(syncStatus = SyncStatus.PENDING_DELETE)
                taskDao.updateTask(markForDelete.toEntity())
                workManagerScheduler.scheduleOneTimeSync()
            }
        }
    }

    override suspend fun syncTasks(): Result<Unit> {
        return try {
            // 1. Send unsynced local pending changes to Retrofit API
            val unsyncedEntities = taskDao.getUnsyncedTasks()
            val pendingUploads = unsyncedEntities
                .filter { it.syncStatus != SyncStatus.PENDING_DELETE.name }
                .map { it.toDomain().toDto() }

            if (pendingUploads.isNotEmpty()) {
                val syncResponse = apiService.syncBatch(SyncRequestDto(pendingUploads))
                if (syncResponse.isSuccessful) {
                    // Mark as synced locally
                    unsyncedEntities.forEach { entity ->
                        if (entity.syncStatus != SyncStatus.PENDING_DELETE.name) {
                            val syncedEntity = entity.toDomain().copy(syncStatus = SyncStatus.SYNCED).toEntity()
                            taskDao.updateTask(syncedEntity)
                        }
                    }
                }
            }

            // Execute deletes
            val pendingDeletes = unsyncedEntities.filter { it.syncStatus == SyncStatus.PENDING_DELETE.name }
            pendingDeletes.forEach { entity ->
                val deleteResponse = apiService.deleteRemoteTask(entity.id)
                if (deleteResponse.isSuccessful) {
                    taskDao.deleteTaskById(entity.id)
                }
            }

            // 2. Fetch latest remote tasks from Retrofit server
            val remoteResponse = apiService.getRemoteTasks()
            if (remoteResponse.isSuccessful) {
                val remoteDtos = remoteResponse.body() ?: emptyList()
                remoteDtos.forEach { dto ->
                    val local = taskDao.getTaskByIdSync(dto.id)
                    // If local does not exist, insert remote version
                    if (local == null) {
                        taskDao.insertTask(dto.toEntity(SyncStatus.SYNCED))
                    } else {
                        // If local exists, compare updatedAtMillis
                        // Only update if remote is newer AND local is already SYNCED
                        // OR if remote is newer than local (conflict resolution: latest wins)
                        if (dto.updatedAtMillis > local.updatedAtMillis) {
                            taskDao.insertTask(dto.toEntity(SyncStatus.SYNCED))
                        }
                    }
                }
            }

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

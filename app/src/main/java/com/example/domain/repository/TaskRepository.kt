package com.example.domain.repository

import com.example.domain.model.Category
import com.example.domain.model.Priority
import com.example.domain.model.Task
import com.example.domain.model.TaskStats
import kotlinx.coroutines.flow.Flow

/**
 * Clean Architecture Domain Repository contract for Task management.
 *
 * Architectural Pattern & Decision Rationale:
 * - Dependency Inversion Principle (DIP): High-level domain Use Cases depend on this abstract
 *   interface rather than concrete data layer implementations (`TaskRepositoryImpl`).
 * - Why preferred: Allows seamless unit testing by mocking this interface without requiring
 *   real database or network setup. Enables offline-first architectures where data sources can
 *   be swapped or augmented easily.
 */
interface TaskRepository {
    /**
     * Observes all tasks reactively as a [Flow].
     */
    fun getTasks(): Flow<List<Task>>

    /**
     * Observes a single task by ID.
     */
    fun getTaskById(taskId: String): Flow<Task?>

    /**
     * Filters tasks by search query, category, priority, and completion status.
     */
    fun getFilteredTasks(
        query: String = "",
        category: Category? = null,
        priority: Priority? = null,
        showCompletedOnly: Boolean? = null
    ): Flow<List<Task>>

    /**
     * Obtains statistical metrics for analytics.
     */
    fun getTaskStats(): Flow<TaskStats>

    /**
     * Inserts a new task locally and queues background sync.
     */
    suspend fun addTask(task: Task)

    /**
     * Updates an existing task locally and queues sync.
     */
    suspend fun updateTask(task: Task)

    /**
     * Deletes a task locally and marks for remote removal.
     */
    suspend fun deleteTask(taskId: String)

    /**
     * Synchronizes local database with remote API service via Retrofit.
     * Called manually or via WorkManager background worker.
     */
    suspend fun syncTasks(): Result<Unit>
}

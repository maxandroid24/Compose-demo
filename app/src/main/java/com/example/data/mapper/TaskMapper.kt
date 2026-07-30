package com.example.data.mapper

import com.example.data.local.TaskEntity
import com.example.data.remote.TaskDto
import com.example.domain.model.Category
import com.example.domain.model.Priority
import com.example.domain.model.SyncStatus
import com.example.domain.model.Task

/**
 * Mapper extension functions converting data layers in Clean Architecture.
 *
 * Architectural Pattern & Decision Rationale:
 * - Mappers convert representations between layers: Domain <-> Entity (Database) and Domain <-> DTO (API).
 * - Why preferred: Isolates data source changes (like API rename or DB column change) to a single mapper file.
 */

// Domain <-> Room Entity
fun TaskEntity.toDomain(): Task {
    return Task(
        id = id,
        title = title,
        description = description,
        isCompleted = isCompleted,
        priority = try { Priority.valueOf(priority) } catch (_: Exception) { Priority.MEDIUM },
        category = try { Category.valueOf(category) } catch (_: Exception) { Category.PERSONAL },
        dueDateMillis = dueDateMillis,
        assignedContactName = assignedContactName,
        assignedContactPhone = assignedContactPhone,
        createdAtMillis = createdAtMillis,
        updatedAtMillis = updatedAtMillis,
        syncStatus = try { SyncStatus.valueOf(syncStatus) } catch (_: Exception) { SyncStatus.SYNCED }
    )
}

fun Task.toEntity(): TaskEntity {
    return TaskEntity(
        id = id,
        title = title,
        description = description,
        isCompleted = isCompleted,
        priority = priority.name,
        category = category.name,
        dueDateMillis = dueDateMillis,
        assignedContactName = assignedContactName,
        assignedContactPhone = assignedContactPhone,
        createdAtMillis = createdAtMillis,
        updatedAtMillis = updatedAtMillis,
        syncStatus = syncStatus.name
    )
}

// Domain <-> Remote DTO
fun TaskDto.toDomain(): Task {
    return Task(
        id = id,
        title = title,
        description = description,
        isCompleted = completed,
        priority = try { Priority.valueOf(priority.uppercase()) } catch (_: Exception) { Priority.MEDIUM },
        category = try { Category.valueOf(category.uppercase()) } catch (_: Exception) { Category.PERSONAL },
        dueDateMillis = dueDateMillis,
        assignedContactName = assignedContactName,
        assignedContactPhone = assignedContactPhone,
        createdAtMillis = createdAtMillis,
        updatedAtMillis = updatedAtMillis,
        syncStatus = SyncStatus.SYNCED
    )
}

fun Task.toDto(): TaskDto {
    return TaskDto(
        id = id,
        title = title,
        description = description,
        completed = isCompleted,
        priority = priority.name,
        category = category.name,
        dueDateMillis = dueDateMillis,
        assignedContactName = assignedContactName,
        assignedContactPhone = assignedContactPhone,
        createdAtMillis = createdAtMillis,
        updatedAtMillis = updatedAtMillis
    )
}

fun TaskDto.toEntity(syncStatus: SyncStatus = SyncStatus.SYNCED): TaskEntity {
    return TaskEntity(
        id = id,
        title = title,
        description = description,
        isCompleted = completed,
        priority = priority.uppercase(),
        category = category.uppercase(),
        dueDateMillis = dueDateMillis,
        assignedContactName = assignedContactName,
        assignedContactPhone = assignedContactPhone,
        createdAtMillis = createdAtMillis,
        updatedAtMillis = updatedAtMillis,
        syncStatus = syncStatus.name
    )
}

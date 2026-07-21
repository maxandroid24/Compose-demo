package com.example.domain.usecase

import com.example.domain.repository.TaskRepository
import javax.inject.Inject

/**
 * UseCase for deleting a task by ID.
 */
class DeleteTaskUseCase @Inject constructor(
    private val repository: TaskRepository
) {
    suspend operator fun invoke(taskId: String): Result<Unit> {
        return try {
            repository.deleteTask(taskId)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

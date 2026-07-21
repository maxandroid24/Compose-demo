package com.example.domain.usecase

import com.example.domain.repository.TaskRepository
import javax.inject.Inject

/**
 * UseCase to trigger manual or background network synchronization with Retrofit remote API.
 */
class SyncTasksUseCase @Inject constructor(
    private val repository: TaskRepository
) {
    suspend operator fun invoke(): Result<Unit> {
        return repository.syncTasks()
    }
}

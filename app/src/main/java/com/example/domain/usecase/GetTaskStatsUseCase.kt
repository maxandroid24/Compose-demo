package com.example.domain.usecase

import com.example.domain.model.TaskStats
import com.example.domain.repository.TaskRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

/**
 * UseCase to compute and observe statistical metrics for task completion analytics.
 */
class GetTaskStatsUseCase @Inject constructor(
    private val repository: TaskRepository
) {
    operator fun invoke(): Flow<TaskStats> {
        return repository.getTaskStats()
    }
}

package com.example.domain.usecase

import com.example.domain.model.Category
import com.example.domain.model.Priority
import com.example.domain.model.Task
import com.example.domain.repository.TaskRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

/**
 * UseCase for retrieving and filtering tasks in Clean Architecture.
 *
 * Architectural Pattern & Decision Rationale:
 * - Single Responsibility Principle (SRP): Encapsulates a single user workflow operation.
 * - Why preferred: ViewModel calls UseCases rather than directly interacting with repositories.
 *   This enforces clear business rule isolation, reusability across multiple ViewModels or Fragments,
 *   and simplified unit testing.
 */
class GetTasksUseCase @Inject constructor(
    private val repository: TaskRepository
) {
    operator fun invoke(
        query: String = "",
        category: Category? = null,
        priority: Priority? = null,
        showCompletedOnly: Boolean? = null
    ): Flow<List<Task>> {
        return repository.getFilteredTasks(
            query = query,
            category = category,
            priority = priority,
            showCompletedOnly = showCompletedOnly
        )
    }
}

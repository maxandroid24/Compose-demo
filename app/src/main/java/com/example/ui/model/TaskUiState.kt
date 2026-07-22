package com.example.ui.model

import com.example.domain.model.Category
import com.example.domain.model.Priority
import com.example.domain.model.Task
import com.example.domain.model.TaskStats

/**
 * Sealed interface / Data state classes for Task UI screens in MVVM.
 *
 * Architectural Pattern & Decision Rationale:
 * - Unidirectional Data Flow (UDF) & Immutable UI State: The ViewModel exposes a single
 *   [StateFlow] containing [TaskListUiState], [TaskDetailUiState], and [SyncUiState].
 * - Why preferred: Prevents inconsistent states (e.g. showing both loading spinner and error screen).
 *   Makes UI rendering pure and fully deterministic.
 */
data class TaskListUiState(
    val tasks: List<Task> = emptyList(),
    val searchQuery: String = "",
    val selectedCategory: Category? = null,
    val selectedPriority: Priority? = null,
    val showCompletedOnly: Boolean? = null,
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

data class TaskDetailUiState(
    val id: String = "",
    val title: String = "",
    val description: String = "",
    val isCompleted: Boolean = false,
    val priority: Priority = Priority.MEDIUM,
    val category: Category = Category.PERSONAL,
    val dueDateMillis: Long? = null,
    val assignedContactName: String? = null,
    val assignedContactPhone: String? = null,
    val isSaving: Boolean = false,
    val saveSuccess: Boolean = false,
    val errorMessage: String? = null
)

data class SyncUiState(
    val isSyncing: Boolean = false,
    val lastSyncMessage: String? = "System up to date",
    val syncSuccess: Boolean = true
)

data class TaskAnalyticsUiState(
    val stats: TaskStats = TaskStats(),
    val categoryBreakdown: Map<Category, Int> = emptyMap(),
    val priorityBreakdown: Map<Priority, Int> = emptyMap()
)

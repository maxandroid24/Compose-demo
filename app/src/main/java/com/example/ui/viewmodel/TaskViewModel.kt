package com.example.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.domain.model.Category
import com.example.domain.model.Priority
import com.example.domain.model.Task
import com.example.domain.usecase.AddTaskUseCase
import com.example.domain.usecase.DeleteTaskUseCase
import com.example.domain.usecase.GetTaskStatsUseCase
import com.example.domain.usecase.GetTasksUseCase
import com.example.domain.usecase.SyncTasksUseCase
import com.example.domain.usecase.UpdateTaskUseCase
import com.example.ui.model.SyncUiState
import com.example.ui.model.TaskAnalyticsUiState
import com.example.ui.model.TaskDetailUiState
import com.example.ui.model.TaskListUiState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel in MVVM architecture managing UI states for Personal Tasks.
 *
 * Architectural Pattern & Decision Rationale:
 * - Annotated with [@HiltViewModel] to allow Hilt to construct and inject domain UseCases automatically.
 * - MVVM Pattern: Holds and manages UI state in a lifecycle-aware manner. ViewModel survives
 *   configuration changes (e.g., screen rotations) without re-fetching or losing user state.
 * - Reactive [StateFlow]: Exposes immutable state flows observed by Composables inside Fragments
 *   using `collectAsStateWithLifecycle()`.
 */
@OptIn(FlowPreview::class)
@HiltViewModel
class TaskViewModel @Inject constructor(
    private val getTasksUseCase: GetTasksUseCase,
    private val addTaskUseCase: AddTaskUseCase,
    private val updateTaskUseCase: UpdateTaskUseCase,
    private val deleteTaskUseCase: DeleteTaskUseCase,
    private val syncTasksUseCase: SyncTasksUseCase,
    private val getTaskStatsUseCase: GetTaskStatsUseCase
) : ViewModel() {

    // Filter states
    private val _searchQuery = MutableStateFlow("")
    private val _selectedCategory = MutableStateFlow<Category?>(null)
    private val _selectedPriority = MutableStateFlow<Priority?>(null)
    private val _showCompletedOnly = MutableStateFlow<Boolean?>(null)

    // UI States
    private val _listUiState = MutableStateFlow(TaskListUiState(isLoading = true))
    val listUiState: StateFlow<TaskListUiState> = _listUiState.asStateFlow()

    private val _detailUiState = MutableStateFlow(TaskDetailUiState())
    val detailUiState: StateFlow<TaskDetailUiState> = _detailUiState.asStateFlow()

    private val _syncUiState = MutableStateFlow(SyncUiState())
    val syncUiState: StateFlow<SyncUiState> = _syncUiState.asStateFlow()

    private val _analyticsUiState = MutableStateFlow(TaskAnalyticsUiState())
    val analyticsUiState: StateFlow<TaskAnalyticsUiState> = _analyticsUiState.asStateFlow()

    init {
        observeTasks()
        observeStats()
    }

    private fun observeTasks() {
        combine(
            _searchQuery.debounce(200),
            _selectedCategory,
            _selectedPriority,
            _showCompletedOnly
        ) { query, category, priority, completedOnly ->
            FilterParams(query, category, priority, completedOnly)
        }.onEach { params ->
            getTasksUseCase(
                query = params.query,
                category = params.category,
                priority = params.priority,
                showCompletedOnly = params.completedOnly
            ).collect { tasks ->
                _listUiState.update { currentState ->
                    currentState.copy(
                        tasks = tasks,
                        searchQuery = params.query,
                        selectedCategory = params.category,
                        selectedPriority = params.priority,
                        showCompletedOnly = params.completedOnly,
                        isLoading = false,
                        errorMessage = null
                    )
                }
            }
        }.launchIn(viewModelScope)
    }

    private fun observeStats() {
        viewModelScope.launch {
            getTaskStatsUseCase().collect { stats ->
                getTasksUseCase().collect { allTasks ->
                    val catMap = allTasks.groupBy { it.category }.mapValues { it.value.size }
                    val priMap = allTasks.groupBy { it.priority }.mapValues { it.value.size }
                    _analyticsUiState.update {
                        TaskAnalyticsUiState(
                            stats = stats,
                            categoryBreakdown = catMap,
                            priorityBreakdown = priMap
                        )
                    }
                }
            }
        }
    }

    // User Actions
    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }

    fun onCategoryFilterSelected(category: Category?) {
        _selectedCategory.value = category
    }

    fun onPriorityFilterSelected(priority: Priority?) {
        _selectedPriority.value = priority
    }

    fun onToggleCompletionFilter(completedOnly: Boolean?) {
        _showCompletedOnly.value = completedOnly
    }

    fun onToggleTaskCompletion(task: Task) {
        viewModelScope.launch {
            val updated = task.copy(isCompleted = !task.isCompleted)
            updateTaskUseCase(updated)
        }
    }

    fun onDeleteTask(taskId: String) {
        viewModelScope.launch {
            deleteTaskUseCase(taskId)
        }
    }

    fun prepareNewTask() {
        _detailUiState.value = TaskDetailUiState()
    }

    fun prepareEditTask(task: Task) {
        _detailUiState.value = TaskDetailUiState(
            id = task.id,
            title = task.title,
            description = task.description,
            isCompleted = task.isCompleted,
            priority = task.priority,
            category = task.category,
            dueDateMillis = task.dueDateMillis
        )
    }

    fun onDetailTitleChanged(title: String) {
        _detailUiState.update { it.copy(title = title, errorMessage = null) }
    }

    fun onDetailDescriptionChanged(description: String) {
        _detailUiState.update { it.copy(description = description) }
    }

    fun onDetailPriorityChanged(priority: Priority) {
        _detailUiState.update { it.copy(priority = priority) }
    }

    fun onDetailCategoryChanged(category: Category) {
        _detailUiState.update { it.copy(category = category) }
    }

    fun onDetailDueDateChanged(dueDateMillis: Long?) {
        _detailUiState.update { it.copy(dueDateMillis = dueDateMillis) }
    }

    fun saveTask() {
        val currentState = _detailUiState.value
        if (currentState.title.isBlank()) {
            _detailUiState.update { it.copy(errorMessage = "Title cannot be empty") }
            return
        }

        viewModelScope.launch {
            _detailUiState.update { it.copy(isSaving = true) }
            val task = Task(
                id = if (currentState.id.isBlank()) java.util.UUID.randomUUID().toString() else currentState.id,
                title = currentState.title.trim(),
                description = currentState.description.trim(),
                isCompleted = currentState.isCompleted,
                priority = currentState.priority,
                category = currentState.category,
                dueDateMillis = currentState.dueDateMillis
            )

            val result = if (currentState.id.isBlank()) {
                addTaskUseCase(task)
            } else {
                updateTaskUseCase(task)
            }

            if (result.isSuccess) {
                _detailUiState.update { it.copy(isSaving = false, saveSuccess = true) }
            } else {
                _detailUiState.update {
                    it.copy(
                        isSaving = false,
                        errorMessage = result.exceptionOrNull()?.message ?: "Failed to save task"
                    )
                }
            }
        }
    }

    fun triggerManualSync() {
        viewModelScope.launch {
            _syncUiState.update { it.copy(isSyncing = true) }
            val result = syncTasksUseCase()
            if (result.isSuccess) {
                _syncUiState.update {
                    SyncUiState(
                        isSyncing = false,
                        lastSyncMessage = "Sync completed successfully via Retrofit REST API",
                        syncSuccess = true
                    )
                }
            } else {
                _syncUiState.update {
                    SyncUiState(
                        isSyncing = false,
                        lastSyncMessage = "Sync error: ${result.exceptionOrNull()?.message}",
                        syncSuccess = false
                    )
                }
            }
        }
    }

    private data class FilterParams(
        val query: String,
        val category: Category?,
        val priority: Priority?,
        val completedOnly: Boolean?
    )
}

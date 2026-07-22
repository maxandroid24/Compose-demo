package com.example.ui.fragment

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.compose.runtime.getValue
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.platform.ViewCompositionStrategy
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.appcompat.app.AlertDialog
import com.example.TaskApplication
import com.example.ui.screens.TaskListScreen
import com.example.ui.theme.TaskManagerTheme
import com.example.ui.viewmodel.TaskViewModel
import dagger.hilt.android.AndroidEntryPoint

/**
 * Fragment hosting [TaskListScreen] in a modular Fragment navigation flow.
 *
 * Architectural Pattern & Decision Rationale:
 * - Annotated with [@AndroidEntryPoint] to support Hilt Fragment injection.
 * - Modular Fragment Architecture: Encapsulates individual screens into distinct [Fragment] components.
 * - Demonstrates Fragment native [AlertDialog] handling for critical user actions (such as task deletion).
 */
@AndroidEntryPoint
class TaskListFragment : Fragment() {

    private val viewModel: TaskViewModel by activityViewModels {
        (requireActivity().application as TaskApplication).appContainer.provideTaskViewModelFactory()
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return ComposeView(requireContext()).apply {
            setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed)

            setContent {
                TaskManagerTheme {
                    val listUiState by viewModel.listUiState.collectAsStateWithLifecycle()

                    TaskListScreen(
                        uiState = listUiState,
                        onSearchQueryChanged = viewModel::onSearchQueryChanged,
                        onCategoryFilterSelected = viewModel::onCategoryFilterSelected,
                        onPriorityFilterSelected = viewModel::onPriorityFilterSelected,
                        onToggleCompletionFilter = viewModel::onToggleCompletionFilter,
                        onToggleTaskCompletion = viewModel::onToggleTaskCompletion,
                        onDeleteTask = { taskId ->
                            showDeleteConfirmationDialog(taskId)
                        },
                        onTaskClick = { task ->
                            viewModel.prepareEditTask(task)
                            (activity as? NavigationHandler)?.navigateToDetail()
                        },
                        onAddNewTaskClick = {
                            viewModel.prepareNewTask()
                            (activity as? NavigationHandler)?.navigateToDetail()
                        },
                        onNavigateToAnalytics = {
                            (activity as? NavigationHandler)?.navigateToAnalytics()
                        },
                        onNavigateToSettings = {
                            (activity as? NavigationHandler)?.navigateToSettings()
                        }
                    )
                }
            }
        }
    }

    /**
     * Displays a native Android [AlertDialog] within the Fragment context
     * to confirm task deletion before proceeding.
     */
    private fun showDeleteConfirmationDialog(taskId: String) {
        AlertDialog.Builder(requireContext())
            .setTitle("Delete Task")
            .setMessage("Are you sure you want to permanently delete this task?")
            .setPositiveButton("Delete") { _, _ ->
                viewModel.onDeleteTask(taskId)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}

/**
 * Navigation interface implemented by MainActivity to handle Fragment transitions.
 */
interface NavigationHandler {
    fun navigateToDetail()
    fun navigateToAnalytics()
    fun navigateToSettings()
    fun navigateBack()
}

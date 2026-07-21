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
import com.example.TaskApplication
import com.example.ui.screens.TaskDetailScreen
import com.example.ui.theme.TaskManagerTheme
import com.example.ui.viewmodel.TaskViewModel
import dagger.hilt.android.AndroidEntryPoint

/**
 * Fragment hosting [TaskDetailScreen] for creating or editing personal tasks.
 *
 * Architectural Pattern & Decision Rationale:
 * - Annotated with [@AndroidEntryPoint] for Hilt field injection.
 * - Modular Fragment Navigation: Wraps Jetpack Compose UI inside an isolated Fragment module.
 */
@AndroidEntryPoint
class TaskDetailFragment : Fragment() {

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
                    val detailUiState by viewModel.detailUiState.collectAsStateWithLifecycle()

                    TaskDetailScreen(
                        uiState = detailUiState,
                        onTitleChanged = viewModel::onDetailTitleChanged,
                        onDescriptionChanged = viewModel::onDetailDescriptionChanged,
                        onPriorityChanged = viewModel::onDetailPriorityChanged,
                        onCategoryChanged = viewModel::onDetailCategoryChanged,
                        onDueDateChanged = viewModel::onDetailDueDateChanged,
                        onSaveClick = viewModel::saveTask,
                        onBackClick = {
                            (activity as? NavigationHandler)?.navigateBack()
                        }
                    )
                }
            }
        }
    }
}

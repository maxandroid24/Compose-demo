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
import com.example.ui.screens.TaskAnalyticsScreen
import com.example.ui.theme.TaskManagerTheme
import com.example.ui.viewmodel.TaskViewModel
import dagger.hilt.android.AndroidEntryPoint

/**
 * Fragment hosting [TaskAnalyticsScreen] for productivity metrics.
 */
@AndroidEntryPoint
class TaskAnalyticsFragment : Fragment() {

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
                    val analyticsUiState by viewModel.analyticsUiState.collectAsStateWithLifecycle()

                    TaskAnalyticsScreen(
                        uiState = analyticsUiState,
                        onBackClick = {
                            (activity as? NavigationHandler)?.navigateBack()
                        }
                    )
                }
            }
        }
    }
}

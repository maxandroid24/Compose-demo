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
import com.example.ui.screens.SettingsScreen
import com.example.ui.theme.TaskManagerTheme
import com.example.ui.viewmodel.TaskViewModel
import dagger.hilt.android.AndroidEntryPoint

/**
 * Fragment hosting [SettingsScreen] for WorkManager background sync preferences.
 * Demonstrates native [AlertDialog] prompt handling inside Fragment lifecycle.
 */
@AndroidEntryPoint
class SettingsFragment : Fragment() {

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
                    val syncUiState by viewModel.syncUiState.collectAsStateWithLifecycle()

                    SettingsScreen(
                        syncUiState = syncUiState,
                        onTriggerSyncClick = {
                            showSyncConfirmationDialog()
                        },
                        onBackClick = {
                            (activity as? NavigationHandler)?.navigateBack()
                        }
                    )
                }
            }
        }
    }

    /**
     * Displays an AlertDialog inside the Fragment to confirm triggering manual network sync.
     */
    private fun showSyncConfirmationDialog() {
        AlertDialog.Builder(requireContext())
            .setTitle("Start Manual Sync")
            .setMessage("Do you want to force an immediate synchronization with the remote REST server?")
            .setPositiveButton("Sync Now") { _, _ ->
                viewModel.triggerManualSync()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}

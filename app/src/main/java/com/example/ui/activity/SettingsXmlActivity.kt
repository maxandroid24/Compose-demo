package com.example.ui.activity

import android.content.Intent
import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.example.databinding.ActivitySettingsBinding
import com.example.ui.viewmodel.TaskViewModel
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

/**
 * Settings & Sync Activity implemented strictly using **Traditional Android XML Layouts** + ViewBinding.
 *
 * Comparative Rationale:
 * - Direct View Access: Uses `binding.btnTriggerSync` and `binding.tvLastSyncStatus` to update button
 *   enabled states and sync status text upon WorkManager events.
 */
@AndroidEntryPoint
class SettingsXmlActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySettingsBinding
    private val viewModel: TaskViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySettingsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupToolbar()
        setupListeners()
        observeViewModel()
    }

    private fun setupToolbar() {
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.btnSwitchToCompose.setOnClickListener {
            startActivity(Intent(this, SettingsComposeActivity::class.java))
            finish()
        }
    }

    private fun setupListeners() {
        binding.btnTriggerSync.setOnClickListener {
            showSyncConfirmationDialog()
        }
    }

    private fun observeViewModel() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.syncUiState.collect { state ->
                    if (state.isSyncing) {
                        binding.btnTriggerSync.isEnabled = false
                        binding.btnTriggerSync.text = "Syncing..."
                        binding.tvLastSyncStatus.text = "Status: Performing remote REST API sync via WorkManager..."
                    } else {
                        binding.btnTriggerSync.isEnabled = true
                        binding.btnTriggerSync.text = "Sync Now with REST API"
                        binding.tvLastSyncStatus.text = "Status: ${state.lastSyncMessage}"
                    }
                }
            }
        }
    }

    private fun showSyncConfirmationDialog() {
        AlertDialog.Builder(this)
            .setTitle("Start Manual Sync")
            .setMessage("Do you want to force an immediate synchronization with the remote REST server?")
            .setPositiveButton("Sync Now") { _, _ -> viewModel.triggerManualSync() }
            .setNegativeButton("Cancel", null)
            .show()
    }
}

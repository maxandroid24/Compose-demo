package com.example.ui.activity

import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.example.data.provider.ContactsProviderManager
import com.example.databinding.ActivityTaskDetailBinding
import com.example.domain.model.Category
import com.example.domain.model.Priority
import com.example.ui.viewmodel.TaskViewModel
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Task Detail Activity implemented strictly using **Traditional Android XML Layouts** + ViewBinding.
 *
 * Comparative Rationale:
 * - Imperative Form Handling: Uses [TextWatcher] for TextInputEditTexts, [ChipGroup.OnCheckedStateChangeListener]
 *   for option selectors, and manual view updates from ViewModel flows.
 */
@AndroidEntryPoint
class TaskDetailXmlActivity : AppCompatActivity() {

    private lateinit var binding: ActivityTaskDetailBinding
    private val viewModel: TaskViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityTaskDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupToolbar()
        setupListeners()
        observeViewModel()
    }

    private fun setupToolbar() {
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.btnSwitchToCompose.setOnClickListener {
            startActivity(Intent(this, TaskDetailComposeActivity::class.java))
            finish()
        }
    }

    private fun setupListeners() {
        binding.etTitle.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                viewModel.onDetailTitleChanged(s?.toString().orEmpty())
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        binding.etDescription.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                viewModel.onDetailDescriptionChanged(s?.toString().orEmpty())
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        binding.chipGroupPriority.setOnCheckedStateChangeListener { _, checkedIds ->
            val priority = when (checkedIds.firstOrNull()) {
                binding.chipLow.id -> Priority.LOW
                binding.chipHigh.id -> Priority.HIGH
                else -> Priority.MEDIUM
            }
            viewModel.onDetailPriorityChanged(priority)
        }

        binding.chipGroupCategoryDetail.setOnCheckedStateChangeListener { _, checkedIds ->
            val category = when (checkedIds.firstOrNull()) {
                binding.chipCatDetWork.id -> Category.WORK
                binding.chipCatDetHealth.id -> Category.HEALTH
                binding.chipCatDetFinance.id -> Category.FINANCE
                binding.chipCatDetEducation.id -> Category.SHOPPING
                else -> Category.PERSONAL
            }
            viewModel.onDetailCategoryChanged(category)
        }

        binding.cardDueDate.setOnClickListener {
            val currentDueDate = viewModel.detailUiState.value.dueDateMillis
            if (currentDueDate == null) {
                viewModel.onDetailDueDateChanged(System.currentTimeMillis() + 86400000L)
            } else {
                viewModel.onDetailDueDateChanged(null)
            }
        }

        binding.cardAssignContact.setOnClickListener {
            showContactPickerDialog()
        }

        binding.fabSaveTask.setOnClickListener {
            viewModel.saveTask()
        }
    }

    private fun observeViewModel() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.detailUiState.collect { state ->
                    if (state.saveSuccess) {
                        Toast.makeText(this@TaskDetailXmlActivity, "Task saved successfully!", Toast.LENGTH_SHORT).show()
                        finish()
                        return@collect
                    }

                    if (binding.etTitle.text.toString() != state.title) {
                        binding.etTitle.setText(state.title)
                    }

                    if (binding.etDescription.text.toString() != state.description) {
                        binding.etDescription.setText(state.description)
                    }

                    state.errorMessage?.let {
                        binding.tilTitle.error = it
                    } ?: run {
                        binding.tilTitle.error = null
                    }

                    // Due Date UI
                    if (state.dueDateMillis != null) {
                        val formattedDate = SimpleDateFormat("EEEE, MMM dd, yyyy", Locale.getDefault()).format(Date(state.dueDateMillis))
                        binding.tvDueDateText.text = "Due: $formattedDate (Reminder set)"
                    } else {
                        binding.tvDueDateText.text = "No due date set (Tap to toggle)"
                    }

                    // Contact UI
                    if (!state.assignedContactName.isNull_or_blank()) {
                        binding.tvContactText.text = "Assigned to: ${state.assignedContactName}"
                    } else {
                        binding.tvContactText.text = "Tap to pick contact via ContentProvider"
                    }
                }
            }
        }
    }

    private fun showContactPickerDialog() {
        val provider = ContactsProviderManager(this)
        val contacts = provider.fetchContacts()
        val contactNames = contacts.map { "${it.name} (${it.phoneNumber})" }.toTypedArray()

        AlertDialog.Builder(this)
            .setTitle("Select Contact (ContentProvider)")
            .setItems(contactNames) { _, which ->
                val selected = contacts[which]
                viewModel.onDetailContactSelected(selected.name, selected.phoneNumber)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}

private fun String?.isNull_or_blank(): Boolean {
    return this == null || this.isBlank()
}

package com.example.ui.activity

import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.databinding.ActivityTaskListBinding
import com.example.domain.model.Category
import com.example.ui.adapter.TaskAdapter
import com.example.ui.viewmodel.TaskViewModel
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

/**
 * Task List Activity implemented strictly using **Traditional Android XML Layouts** + ViewBinding.
 *
 * Comparative Rationale:
 * - Imperative UI Paradigm: Explicitly inflates XML layout `activity_task_list.xml`, binds views with
 *   ViewBinding, manages RecyclerView via [TaskAdapter] and LayoutManager, and updates views manually.
 */
@AndroidEntryPoint
class TaskListXmlActivity : AppCompatActivity() {

    private lateinit var binding: ActivityTaskListBinding
    private val viewModel: TaskViewModel by viewModels()
    private lateinit var taskAdapter: TaskAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityTaskListBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupToolbar()
        setupRecyclerView()
        setupListeners()
        observeViewModel()
    }

    private fun setupToolbar() {
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.btnSwitchToCompose.setOnClickListener {
            startActivity(Intent(this, TaskListComposeActivity::class.java))
            finish()
        }
        binding.btnNavAnalytics.setOnClickListener {
            startActivity(Intent(this, TaskAnalyticsXmlActivity::class.java))
        }
        binding.btnNavSettings.setOnClickListener {
            startActivity(Intent(this, SettingsXmlActivity::class.java))
        }
    }

    private fun setupRecyclerView() {
        taskAdapter = TaskAdapter(
            onTaskClick = { task ->
                viewModel.prepareEditTask(task)
                startActivity(Intent(this, TaskDetailXmlActivity::class.java))
            },
            onToggleCompletion = { task ->
                viewModel.onToggleTaskCompletion(task)
            },
            onDeleteClick = { taskId ->
                showDeleteConfirmationDialog(taskId)
            }
        )
        binding.recyclerViewTasks.apply {
            layoutManager = LinearLayoutManager(this@TaskListXmlActivity)
            adapter = taskAdapter
        }
    }

    private fun setupListeners() {
        binding.fabAddTask.setOnClickListener {
            viewModel.prepareNewTask()
            startActivity(Intent(this, TaskDetailXmlActivity::class.java))
        }

        binding.etSearchQuery.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                viewModel.onSearchQueryChanged(s?.toString().orEmpty())
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        binding.chipGroupCategory.setOnCheckedStateChangeListener { _, checkedIds ->
            val selectedCategory = when (checkedIds.firstOrNull()) {
                binding.chipCatPersonal.id -> Category.PERSONAL
                binding.chipCatWork.id -> Category.WORK
                binding.chipCatHealth.id -> Category.HEALTH
                binding.chipCatFinance.id -> Category.FINANCE
                binding.chipCatEducation.id -> Category.SHOPPING
                else -> null
            }
            viewModel.onCategoryFilterSelected(selectedCategory)
        }
    }

    private fun observeViewModel() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.listUiState.collect { state ->
                    binding.progressBar.visibility = if (state.isLoading) View.VISIBLE else View.GONE
                    taskAdapter.submitList(state.tasks)

                    binding.tvTaskCount.text = "${state.tasks.size} Tasks"
                    if (state.tasks.isEmpty() && !state.isLoading) {
                        binding.layoutEmpty.visibility = View.VISIBLE
                        binding.recyclerViewTasks.visibility = View.GONE
                    } else {
                        binding.layoutEmpty.visibility = View.GONE
                        binding.recyclerViewTasks.visibility = View.VISIBLE
                    }
                }
            }
        }
    }

    private fun showDeleteConfirmationDialog(taskId: String) {
        AlertDialog.Builder(this)
            .setTitle("Delete Task")
            .setMessage("Are you sure you want to delete this task?")
            .setPositiveButton("Delete") { _, _ -> viewModel.onDeleteTask(taskId) }
            .setNegativeButton("Cancel", null)
            .show()
    }
}

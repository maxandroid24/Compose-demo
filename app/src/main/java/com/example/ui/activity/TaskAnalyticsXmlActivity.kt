package com.example.ui.activity

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.example.databinding.ActivityTaskAnalyticsBinding
import com.example.ui.viewmodel.TaskViewModel
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

/**
 * Task Analytics Activity implemented strictly using **Traditional Android XML Layouts** + ViewBinding.
 *
 * Comparative Rationale:
 * - Imperative View Building: Dynamically creates and injects [TextView] and [ProgressBar] items into
 *   a vertical [LinearLayout] container as domain stats arrive.
 */
@AndroidEntryPoint
class TaskAnalyticsXmlActivity : AppCompatActivity() {

    private lateinit var binding: ActivityTaskAnalyticsBinding
    private val viewModel: TaskViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityTaskAnalyticsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupToolbar()
        observeViewModel()
    }

    private fun setupToolbar() {
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.btnSwitchToCompose.setOnClickListener {
            startActivity(Intent(this, TaskAnalyticsComposeActivity::class.java))
            finish()
        }
    }

    private fun observeViewModel() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.analyticsUiState.collect { state ->
                    val stats = state.stats
                    binding.tvTotalTasks.text = stats.totalCount.toString()
                    binding.tvCompletedTasks.text = stats.completedCount.toString()
                    binding.tvPendingTasks.text = stats.pendingCount.toString()

                    val rate = if (stats.totalCount > 0) (stats.completedCount * 100) / stats.totalCount else 0
                    binding.progressCompletion.progress = rate

                    // Populate category distribution dynamically
                    binding.layoutCategories.removeAllViews()
                    state.categoryBreakdown.forEach { (category, count) ->
                        val rowView = createStatRowView(category.name, count, stats.totalCount)
                        binding.layoutCategories.addView(rowView)
                    }

                    // Populate priority distribution dynamically
                    binding.layoutPriorities.removeAllViews()
                    state.priorityBreakdown.forEach { (priority, count) ->
                        val rowView = createStatRowView(priority.name, count, stats.totalCount)
                        binding.layoutPriorities.addView(rowView)
                    }
                }
            }
        }
    }

    private fun createStatRowView(label: String, count: Int, total: Int): LinearLayout {
        val container = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 8, 0, 8) }
        }

        val textHeader = TextView(this).apply {
            text = "$label: $count task(s)"
            textSize = 13f
            setTextColor(Color.DKGRAY)
        }

        val bar = ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal).apply {
            max = if (total > 0) total else 1
            progress = count
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                16
            ).apply { setMargins(0, 4, 0, 0) }
        }

        container.addView(textHeader)
        container.addView(bar)
        return container
    }
}

package com.example.ui.activity

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.ui.screens.TaskListScreen
import com.example.ui.theme.TaskManagerTheme
import com.example.ui.viewmodel.TaskViewModel
import dagger.hilt.android.AndroidEntryPoint

/**
 * Task List Activity implemented strictly using **Jetpack Compose**.
 *
 * Comparative Rationale:
 * - Declarative UI Paradigm: UI automatically updates whenever state changes.
 * - Minimal boilerplate: No findViewById, XML files, or ViewHolders needed.
 */
@AndroidEntryPoint
class TaskListComposeActivity : ComponentActivity() {

    private val viewModel: TaskViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            TaskManagerTheme {
                val listUiState by viewModel.listUiState.collectAsStateWithLifecycle()

                Scaffold(
                    topBar = {
                        // Comparison Banner header
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(Color(0xFFE8F0FE))
                                .statusBarsPadding()
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 16.dp, vertical = 6.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "⚡ Jetpack Compose Paradigm",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFF1A73E8),
                                    modifier = Modifier.weight(1f)
                                )
                                TextButton(
                                    onClick = {
                                        startActivity(Intent(this@TaskListComposeActivity, TaskListXmlActivity::class.java))
                                        finish()
                                    }
                                ) {
                                    Text("Switch to XML 📄", fontSize = 11.sp, color = Color(0xFF1A73E8))
                                }
                            }
                        }
                    }
                ) { innerPadding ->
                    Box(modifier = Modifier.padding(innerPadding)) {
                        TaskListScreen(
                            uiState = listUiState,
                            onSearchQueryChanged = viewModel::onSearchQueryChanged,
                            onCategoryFilterSelected = viewModel::onCategoryFilterSelected,
                            onPriorityFilterSelected = viewModel::onPriorityFilterSelected,
                            onToggleCompletionFilter = viewModel::onToggleCompletionFilter,
                            onToggleTaskCompletion = viewModel::onToggleTaskCompletion,
                            onDeleteTask = viewModel::onDeleteTask,
                            onTaskClick = { task ->
                                viewModel.prepareEditTask(task)
                                startActivity(Intent(this@TaskListComposeActivity, TaskDetailComposeActivity::class.java))
                            },
                            onAddNewTaskClick = {
                                viewModel.prepareNewTask()
                                startActivity(Intent(this@TaskListComposeActivity, TaskDetailComposeActivity::class.java))
                            },
                            onNavigateToAnalytics = {
                                startActivity(Intent(this@TaskListComposeActivity, TaskAnalyticsComposeActivity::class.java))
                            },
                            onNavigateToSettings = {
                                startActivity(Intent(this@TaskListComposeActivity, SettingsComposeActivity::class.java))
                            }
                        )
                    }
                }
            }
        }
    }
}

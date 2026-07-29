package com.example

import android.content.Intent
import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import com.example.databinding.ActivityMainBinding
import com.example.ui.activity.ManualStoreOwnerActivity
import com.example.ui.activity.SettingsComposeActivity
import com.example.ui.activity.SettingsXmlActivity
import com.example.ui.activity.TaskAnalyticsComposeActivity
import com.example.ui.activity.TaskAnalyticsXmlActivity
import com.example.ui.activity.TaskDetailComposeActivity
import com.example.ui.activity.TaskDetailXmlActivity
import com.example.ui.activity.TaskListComposeActivity
import com.example.ui.activity.TaskListXmlActivity
import dagger.hilt.android.AndroidEntryPoint

/**
 * MainActivity serving as the central **Compose vs XML Comparison Hub**.
 *
 * Architectural Pattern & Decision Rationale:
 * - Direct Side-by-Side Comparison: Launches every screen in either **Jetpack Compose** (declarative)
 *   or **Traditional XML Layout** (imperative layout + ViewBinding) format to compare architectural paradigms.
 */
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Schedule periodic background sync with WorkManager
        val appContainer = (application as TaskApplication).appContainer
        appContainer.workManagerScheduler.schedulePeriodicSync()

        setupButtons()
    }

    private fun setupButtons() {
        // 1. Task List Activity Pair
        binding.btnOpenTaskListCompose.setOnClickListener {
            startActivity(Intent(this, TaskListComposeActivity::class.java))
        }
        binding.btnOpenTaskListXml.setOnClickListener {
            startActivity(Intent(this, TaskListXmlActivity::class.java))
        }

        // 2. Task Detail Activity Pair
        binding.btnOpenTaskDetailCompose.setOnClickListener {
            startActivity(Intent(this, TaskDetailComposeActivity::class.java))
        }
        binding.btnOpenTaskDetailXml.setOnClickListener {
            startActivity(Intent(this, TaskDetailXmlActivity::class.java))
        }

        // 3. Task Analytics Activity Pair
        binding.btnOpenAnalyticsCompose.setOnClickListener {
            startActivity(Intent(this, TaskAnalyticsComposeActivity::class.java))
        }
        binding.btnOpenAnalyticsXml.setOnClickListener {
            startActivity(Intent(this, TaskAnalyticsXmlActivity::class.java))
        }

        // 4. Settings Activity Pair
        binding.btnOpenSettingsCompose.setOnClickListener {
            startActivity(Intent(this, SettingsComposeActivity::class.java))
        }
        binding.btnOpenSettingsXml.setOnClickListener {
            startActivity(Intent(this, SettingsXmlActivity::class.java))
        }

        // 5. ViewModel Creation Paradigms Pair
        binding.btnOpenStandardViewModel.setOnClickListener {
            // Demonstrates standard Android 'by viewModels()' delegate on Activity
            startActivity(Intent(this, TaskListComposeActivity::class.java))
        }
        binding.btnOpenManualViewModel.setOnClickListener {
            // Demonstrates manual ViewModelStoreOwner implementation from scratch
            startActivity(Intent(this, ManualStoreOwnerActivity::class.java))
        }
    }
}

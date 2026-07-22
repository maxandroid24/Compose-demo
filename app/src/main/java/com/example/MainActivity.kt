package com.example

import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.commit
import com.example.ui.fragment.NavigationHandler
import com.example.ui.fragment.SettingsFragment
import com.example.ui.fragment.TaskAnalyticsFragment
import com.example.ui.fragment.TaskDetailFragment
import com.example.ui.fragment.TaskListFragment
import dagger.hilt.android.AndroidEntryPoint

/**
 * MainActivity serving as the single-activity entry point hosting a modular Fragment navigation flow.
 *
 * Architectural Pattern & Decision Rationale:
 * - Single-Activity Architecture: Recommendations from Android Architecture Guidelines favor a single
 *   main Activity that manages view containers and navigation components.
 * - Annotated with [@AndroidEntryPoint] to attach the Hilt dependency graph to Activity lifecycle.
 * - Implements [NavigationHandler] to manage Fragment transitions ([TaskListFragment], [TaskDetailFragment],
 *   [TaskAnalyticsFragment], [SettingsFragment]) cleanly on the support fragment manager backstack.
 */
@AndroidEntryPoint
class MainActivity : AppCompatActivity(), NavigationHandler {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // Create container view dynamically
        val containerId = android.R.id.content
        setContentView(
            android.widget.FrameLayout(this).apply {
                id = containerId
            }
        )

        // Schedule periodic background sync with WorkManager via AppContainer
        val appContainer = (application as TaskApplication).appContainer
        appContainer.workManagerScheduler.schedulePeriodicSync()

        // Display root TaskListFragment on initial launch
        if (savedInstanceState == null) {
            supportFragmentManager.commit {
                replace(containerId, TaskListFragment())
            }
        }
    }

    override fun navigateToDetail() {
        supportFragmentManager.commit {
            replace(android.R.id.content, TaskDetailFragment())
            addToBackStack("detail")
        }
    }

    override fun navigateToAnalytics() {
        supportFragmentManager.commit {
            replace(android.R.id.content, TaskAnalyticsFragment())
            addToBackStack("analytics")
        }
    }

    override fun navigateToSettings() {
        supportFragmentManager.commit {
            replace(android.R.id.content, SettingsFragment())
            addToBackStack("settings")
        }
    }

    override fun navigateBack() {
        if (supportFragmentManager.backStackEntryCount > 0) {
            supportFragmentManager.popBackStack()
        }
    }
}

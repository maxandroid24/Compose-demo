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
@AndroidEntryPoint // Marks this activity as a Hilt component container for dependency injection
class MainActivity : AppCompatActivity(), NavigationHandler {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Enables edge-to-edge display, allowing content to utilize the full screen behind system bars
        enableEdgeToEdge()

        // android.R.id.content is a built-in Android framework ID. 
        // It refers to the root content FrameLayout that exists in every Activity window.
        // By assigning this ID to our dynamically created FrameLayout, we define it as the 
        // primary container for our UI/Fragments without requiring an XML layout file (like activity_main.xml).
        val containerId = android.R.id.content
        setContentView(
            android.widget.FrameLayout(this).apply {
                id = containerId
            }
        )

        // Schedule periodic background sync with WorkManager via the AppContainer.
        // This ensures data is synchronized even when the app is not in the foreground.
        val appContainer = (application as TaskApplication).appContainer
        appContainer.workManagerScheduler.schedulePeriodicSync()

        // Display root TaskListFragment on initial launch.
        // Only trigger this if savedInstanceState is null to avoid double-loading on configuration changes.
        if (savedInstanceState == null) {
            supportFragmentManager.commit {
                replace(containerId, TaskListFragment())
            }
        }
    }

    /**
     * Navigates to the Task Detail screen.
     * Uses supportFragmentManager to replace the current fragment and adds the transaction to the back stack.
     */
    override fun navigateToDetail() {
        supportFragmentManager.commit {
            replace(android.R.id.content, TaskDetailFragment())
            addToBackStack("detail") // Allows the user to navigate back to the list
        }
    }

    /**
     * Navigates to the Task Analytics screen.
     */
    override fun navigateToAnalytics() {
        supportFragmentManager.commit {
            replace(android.R.id.content, TaskAnalyticsFragment())
            addToBackStack("analytics")
        }
    }

    /**
     * Navigates to the Settings screen.
     */
    override fun navigateToSettings() {
        supportFragmentManager.commit {
            replace(android.R.id.content, SettingsFragment())
            addToBackStack("settings")
        }
    }

    /**
     * Handles the back navigation by popping the fragment manager's back stack.
     */
    override fun navigateBack() {
        if (supportFragmentManager.backStackEntryCount > 0) {
            supportFragmentManager.popBackStack()
        }
    }
}

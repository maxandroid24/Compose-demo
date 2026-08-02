package com.example

import android.app.Application
import com.example.di.AppContainer
import dagger.hilt.android.HiltAndroidApp

/**
 * TaskApplication is the custom [Application] entry point for the Task Manager app.
 *
 * Architectural Pattern & Decision rationale:
 * - Annotated with [@HiltAndroidApp] to trigger Hilt's code generation container.
 * - Exposes [AppContainer] to provide clean dependency injection across the Application lifecycle.
 */
@HiltAndroidApp
class TaskApplication : Application() {

    val appContainer: AppContainer by lazy {
        AppContainer(this)
    }

    override fun onCreate() {
        super.onCreate()
        registerNetworkCallback()
    }

    private fun registerNetworkCallback() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.N) {
            val connectivityManager =
                getSystemService(android.content.Context.CONNECTIVITY_SERVICE) as? android.net.ConnectivityManager
            connectivityManager?.registerDefaultNetworkCallback(object : android.net.ConnectivityManager.NetworkCallback() {
                override fun onAvailable(network: android.net.Network) {
                    android.util.Log.d("TaskApplication", "Network connection restored. Enqueuing sync task.")
                    appContainer.workManagerScheduler.scheduleOneTimeSync()
                }
            })
        }
    }
}

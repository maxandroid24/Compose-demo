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
}

package com.example.data.worker

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.domain.usecase.SyncTasksUseCase
import dagger.hilt.EntryPoint
import dagger.hilt.InstallIn
import dagger.hilt.android.EntryPointAccessors
import dagger.hilt.components.SingletonComponent

/**
 * Background WorkManager Worker performing automated sync with Retrofit REST API.
 *
 * Architectural Pattern & Decision Rationale:
 * - Extends [CoroutineWorker] to run background task synchronization asynchronously in Coroutines.
 * - Uses Hilt [@EntryPoint] and [EntryPointAccessors] to inject [SyncTasksUseCase] from the
 *   application-level SingletonComponent container into WorkManager's Worker lifecycle.
 * - Why preferred: Allows WorkManager to instantiate the worker via standard reflection without requiring
 *   a custom WorkerFactory, while keeping full access to Hilt dependency injection.
 */
class SyncWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    @EntryPoint
    @InstallIn(SingletonComponent::class)
    interface SyncWorkerEntryPoint {
        fun syncTasksUseCase(): SyncTasksUseCase
    }

    override suspend fun doWork(): Result {
        return try {
            val entryPoint = EntryPointAccessors.fromApplication(
                applicationContext,
                SyncWorkerEntryPoint::class.java
            )
            val syncTasksUseCase = entryPoint.syncTasksUseCase()
            val result = syncTasksUseCase()
            if (result.isSuccess) {
                Result.success()
            } else {
                Result.retry()
            }
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

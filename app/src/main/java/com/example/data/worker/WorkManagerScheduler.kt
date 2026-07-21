package com.example.data.worker

import android.content.Context
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.ExistingWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import dagger.hilt.android.qualifiers.ApplicationContext
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manages background task scheduling via Android WorkManager.
 *
 * Architectural Pattern & Decision Rationale:
 * - WorkManager is Android's recommended solution for persistent, deferrable background work that must
 *   guarantee execution even if the user exits the application or restarts the device.
 * - Why preferred over AlarmManager or JobScheduler: WorkManager automatically chooses the optimal API
 *   depending on OS version, respects system battery optimization constraints (like Doze mode),
 *   and supports constraints (e.g., executing sync only when network connectivity is available).
 */
@Singleton
class WorkManagerScheduler @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val workManager = WorkManager.getInstance(context)

    companion object {
        const val PERIODIC_SYNC_WORK_NAME = "periodic_task_sync_work"
        const val ONE_TIME_SYNC_WORK_NAME = "one_time_task_sync_work"
    }

    /**
     * Schedules periodic background sync every 15 minutes when network is connected.
     */
    fun schedulePeriodicSync() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val periodicRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
            .setConstraints(constraints)
            .build()

        workManager.enqueueUniquePeriodicWork(
            PERIODIC_SYNC_WORK_NAME,
            ExistingPeriodicWorkPolicy.KEEP,
            periodicRequest
        )
    }

    /**
     * Enqueues an immediate one-time sync request whenever tasks are created or modified locally.
     */
    fun scheduleOneTimeSync() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val oneTimeRequest = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(constraints)
            .build()

        workManager.enqueueUniqueWork(
            ONE_TIME_SYNC_WORK_NAME,
            ExistingWorkPolicy.REPLACE,
            oneTimeRequest
        )
    }
}

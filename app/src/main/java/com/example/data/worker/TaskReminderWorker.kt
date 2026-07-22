package com.example.data.worker

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.MainActivity

/**
 * WorkManager CoroutineWorker responsible for delivering push notifications for scheduled task reminders.
 *
 * Architectural Pattern & Decision Rationale:
 * - Decouples notification posting from the main UI thread. WorkManager guarantees execution
 *   even if the application process is inactive when the task reminder due time arrives.
 */
class TaskReminderWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val CHANNEL_ID = "task_reminders_channel"
        const val CHANNEL_NAME = "Task Reminders"
        const val KEY_TASK_ID = "key_task_id"
        const val KEY_TASK_TITLE = "key_task_title"
        const val KEY_TASK_DESCRIPTION = "key_task_description"
    }

    override suspend fun doWork(): Result {
        val taskId = inputData.getString(KEY_TASK_ID) ?: return Result.failure()
        val taskTitle = inputData.getString(KEY_TASK_TITLE) ?: "Task Reminder"
        val taskDescription = inputData.getString(KEY_TASK_DESCRIPTION) ?: ""

        createNotificationChannel()
        showNotification(taskId, taskTitle, taskDescription)

        return Result.success()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Notifications for upcoming task due date reminders"
                enableVibration(true)
            }

            val notificationManager =
                applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun showNotification(taskId: String, title: String, description: String) {
        val intent = Intent(applicationContext, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("EXTRA_TASK_ID", taskId)
        }

        val pendingIntent = PendingIntent.getActivity(
            applicationContext,
            taskId.hashCode(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notificationBuilder = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("Task Reminder: $title")
            .setContentText(if (description.isNotBlank()) description else "Your task is due now!")
            .setStyle(
                NotificationCompat.BigTextStyle()
                    .bigText(if (description.isNotBlank()) description else "Your scheduled task is due now.")
            )
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)

        try {
            val notificationManager = NotificationManagerCompat.from(applicationContext)
            notificationManager.notify(taskId.hashCode(), notificationBuilder.build())
        } catch (_: SecurityException) {
            // Permission POST_NOTIFICATIONS missing or denied
        }
    }
}

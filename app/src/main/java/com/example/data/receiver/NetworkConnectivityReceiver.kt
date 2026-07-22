package com.example.data.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build
import android.util.Log
import com.example.TaskApplication
import com.example.data.worker.WorkManagerScheduler

/**
 * BroadcastReceiver listening for system network connectivity state change events.
 *
 * Architectural Pattern & Decision Rationale:
 * - BroadcastReceiver responds to system-wide network events (`android.net.conn.CONNECTIVITY_CHANGE`).
 * - When an internet connection is established or reconnected, it triggers an immediate remote sync
 *   via [WorkManagerScheduler] to push local offline changes and pull updated remote tasks.
 */
class NetworkConnectivityReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context?, intent: Intent?) {
        if (context == null || intent == null) return

        if (intent.action == ConnectivityManager.CONNECTIVITY_ACTION ||
            intent.action == "android.net.conn.CONNECTIVITY_CHANGE"
        ) {
            if (isNetworkAvailable(context)) {
                Log.d("NetworkReceiver", "Internet connection restored. Triggering remote sync.")
                val appContainer = (context.applicationContext as? TaskApplication)?.appContainer
                appContainer?.workManagerScheduler?.scheduleOneTimeSync()
            }
        }
    }

    private fun isNetworkAvailable(context: Context): Boolean {
        val connectivityManager =
            context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val network = connectivityManager.activeNetwork ?: return false
            val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
            capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
                    capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
        } else {
            @Suppress("DEPRECATION")
            val networkInfo = connectivityManager.activeNetworkInfo
            @Suppress("DEPRECATION")
            networkInfo != null && networkInfo.isConnected
        }
    }
}

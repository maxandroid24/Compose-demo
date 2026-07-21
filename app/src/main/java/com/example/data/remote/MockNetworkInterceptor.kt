package com.example.data.remote

import okhttp3.Interceptor
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.Protocol
import okhttp3.Response
import okhttp3.ResponseBody.Companion.toResponseBody
import java.io.IOException

/**
 * OkHttp Interceptor simulating a remote backend REST API for Task Management.
 *
 * Architectural Pattern & Decision Rationale:
 * - Mock Interceptor allows full end-to-end Retrofit network testing without depending on external
 *   cloud servers that could fail or require complex authentication tokens during local evaluation.
 * - Simulates network latency (200ms) and returns valid JSON payloads for GET, POST, PUT, DELETE,
 *   and batch synchronization requests.
 */
class MockNetworkInterceptor : Interceptor {

    private val jsonMediaType = "application/json".toMediaType()

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val url = request.url.toString()
        val method = request.method

        // Simulate network latency
        try {
            Thread.sleep(200)
        } catch (_: InterruptedException) {}

        val responseJson = when {
            url.contains("api/v1/tasks/sync") -> {
                """
                {
                  "success": true,
                  "synced_count": 1,
                  "remote_tasks": [
                    {
                      "id": "remote-sample-1",
                      "title": "Review Q3 Project Milestones",
                      "description": "Examine team progress reports and finalize roadmap for next sprint.",
                      "completed": false,
                      "priority": "HIGH",
                      "category": "WORK",
                      "due_date": ${System.currentTimeMillis() + 86400000L * 2},
                      "created_at": ${System.currentTimeMillis() - 86400000L}
                    },
                    {
                      "id": "remote-sample-2",
                      "title": "Weekly Grocery Shopping",
                      "description": "Buy fresh produce, oat milk, and protein snacks.",
                      "completed": true,
                      "priority": "MEDIUM",
                      "category": "SHOPPING",
                      "due_date": ${System.currentTimeMillis() - 3600000L},
                      "created_at": ${System.currentTimeMillis() - 172800000L}
                    }
                  ]
                }
                """.trimIndent()
            }
            url.contains("api/v1/tasks") && method == "GET" -> {
                """
                [
                  {
                    "id": "remote-sample-1",
                    "title": "Review Q3 Project Milestones",
                    "description": "Examine team progress reports and finalize roadmap for next sprint.",
                    "completed": false,
                    "priority": "HIGH",
                    "category": "WORK",
                    "due_date": ${System.currentTimeMillis() + 86400000L * 2},
                    "created_at": ${System.currentTimeMillis() - 86400000L}
                  },
                  {
                    "id": "remote-sample-2",
                    "title": "Weekly Grocery Shopping",
                    "description": "Buy fresh produce, oat milk, and protein snacks.",
                    "completed": true,
                    "priority": "MEDIUM",
                    "category": "SHOPPING",
                    "due_date": ${System.currentTimeMillis() - 3600000L},
                    "created_at": ${System.currentTimeMillis() - 172800000L}
                  }
                ]
                """.trimIndent()
            }
            method == "POST" || method == "PUT" -> {
                """
                {
                  "id": "server-task-${System.currentTimeMillis()}",
                  "title": "Task Synced with Cloud API",
                  "description": "Successfully synchronized with Retrofit remote backend.",
                  "completed": false,
                  "priority": "MEDIUM",
                  "category": "PERSONAL",
                  "due_date": null,
                  "created_at": ${System.currentTimeMillis()}
                }
                """.trimIndent()
            }
            method == "DELETE" -> ""
            else -> "{}"
        }

        return Response.Builder()
            .request(request)
            .protocol(Protocol.HTTP_1_1)
            .code(200)
            .message("OK")
            .body(responseJson.toResponseBody(jsonMediaType))
            .build()
    }
}

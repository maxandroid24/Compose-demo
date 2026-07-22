package com.example.data.remote

import com.squareup.moshi.Json

/**
 * Data Transfer Object (DTO) for Retrofit remote API serializations.
 */
data class TaskDto(
    @Json(name = "id") val id: String,
    @Json(name = "title") val title: String,
    @Json(name = "description") val description: String = "",
    @Json(name = "completed") val completed: Boolean = false,
    @Json(name = "priority") val priority: String = "MEDIUM",
    @Json(name = "category") val category: String = "PERSONAL",
    @Json(name = "due_date") val dueDateMillis: Long? = null,
    @Json(name = "assigned_contact_name") val assignedContactName: String? = null,
    @Json(name = "assigned_contact_phone") val assignedContactPhone: String? = null,
    @Json(name = "created_at") val createdAtMillis: Long = System.currentTimeMillis()
)

/**
 * Request payload wrapper for batch sync operations.
 */
data class SyncRequestDto(
    @Json(name = "tasks") val tasks: List<TaskDto>
)

/**
 * Response payload from remote API endpoint.
 */
data class SyncResponseDto(
    @Json(name = "success") val success: Boolean,
    @Json(name = "synced_count") val syncedCount: Int,
    @Json(name = "remote_tasks") val remoteTasks: List<TaskDto>
)

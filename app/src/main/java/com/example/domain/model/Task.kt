package com.example.domain.model

import java.util.UUID

/**
 * Domain representation of a Personal Task in Clean Architecture.
 *
 * Architectural Pattern & Decision Rationale:
 * - Clean Architecture Principle: Domain models are pure Kotlin data objects decoupled from
 *   framework details (like Room `@Entity` or Retrofit `@Json` annotations).
 * - Why preferred: Decoupling domain objects prevents data persistence or network API schemas
 *   from leaking into core business logic. If the backend API format changes or the local DB
 *   schema migrates, domain code and UI remain unaffected.
 */
data class Task(
    val id: String = UUID.randomUUID().toString(),
    val title: String,
    val description: String = "",
    val isCompleted: Boolean = false,
    val priority: Priority = Priority.MEDIUM,
    val category: Category = Category.PERSONAL,
    val dueDateMillis: Long? = null,
    val assignedContactName: String? = null,
    val assignedContactPhone: String? = null,
    val createdAtMillis: Long = System.currentTimeMillis(),
    val updatedAtMillis: Long = System.currentTimeMillis(),
    val syncStatus: SyncStatus = SyncStatus.SYNCED
)

/**
 * Represents priority levels for tasks.
 */
enum class Priority {
    LOW, MEDIUM, HIGH, URGENT
}

/**
 * Categories to group personal tasks effectively.
 */
enum class Category {
    WORK, PERSONAL, HEALTH, FINANCE, SHOPPING, OTHER
}

/**
 * Sync status indicating synchronization state with remote Retrofit server.
 */
enum class SyncStatus {
    SYNCED, PENDING_INSERT, PENDING_UPDATE, PENDING_DELETE
}

/**
 * Value object summarizing task statistics for analytics.
 */
data class TaskStats(
    val totalCount: Int = 0,
    val completedCount: Int = 0,
    val pendingCount: Int = 0,
    val completionPercentage: Float = 0f,
    val urgentPendingCount: Int = 0
)

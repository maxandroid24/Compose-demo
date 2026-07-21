package com.example.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Room SQLite Database Entity representing a task table row.
 *
 * Architectural Pattern & Decision Rationale:
 * - Room Entity annotation maps this Kotlin class directly to the `tasks` SQLite table.
 * - Why preferred over raw SQLite SQL queries or standard Shared Preferences: Room provides
 *   compile-time checking of SQL queries, type safety, reactive Kotlin Flow streaming, and automatic
 *   threading handling via coroutines.
 */
@Entity(tableName = "tasks")
data class TaskEntity(
    @PrimaryKey
    val id: String,
    val title: String,
    val description: String,
    val isCompleted: Boolean,
    val priority: String, // Stored as String name of Priority enum
    val category: String, // Stored as String name of Category enum
    val dueDateMillis: Long?,
    val createdAtMillis: Long,
    val syncStatus: String // Stored as String name of SyncStatus enum
)

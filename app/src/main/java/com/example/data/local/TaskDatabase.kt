package com.example.data.local

import androidx.room.Database
import androidx.room.RoomDatabase

/**
 * Main Room Database configuration class.
 *
 * Architectural Pattern & Decision Rationale:
 * - Serves as the main database access point for local relational data persistence.
 * - Managed by Hilt DI container as a `@Singleton` to prevent multiple costly database instances.
 */
@Database(
    entities = [TaskEntity::class],
    version = 3,
    exportSchema = false
)
abstract class TaskDatabase : RoomDatabase() {
    abstract fun taskDao(): TaskDao
}

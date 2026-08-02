package com.example.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object (DAO) interface defining SQLite database operations for tasks.
 *
 * Architectural Pattern & Decision Rationale:
 * - Room DAO abstracts SQL statements into Kotlin interface methods.
 * - Reactive Streams with [Flow]: Returning [Flow] ensures the UI automatically updates whenever
 *   tasks change in the database without needing manual refresh callbacks.
 * - Suspend functions: All mutating operations ([Insert], [Update], SQL DELETE) run asynchronously on
 *   Room's background thread pool, preventing UI thread blocking.
 */
@Dao
interface TaskDao {

    @Query("SELECT * FROM tasks ORDER BY createdAtMillis DESC")
    fun getAllTasks(): Flow<List<TaskEntity>>

    @Query("SELECT * FROM tasks WHERE id = :taskId")
    fun getTaskById(taskId: String): Flow<TaskEntity?>

    @Query("SELECT * FROM tasks WHERE id = :taskId")
    suspend fun getTaskByIdSync(taskId: String): TaskEntity?

    @Query("SELECT * FROM tasks WHERE syncStatus != 'SYNCED'")
    suspend fun getUnsyncedTasks(): List<TaskEntity>

    @Query("SELECT * FROM tasks")
    suspend fun getAllTasksListSync(): List<TaskEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTask(task: TaskEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTasks(tasks: List<TaskEntity>)

    @Update
    suspend fun updateTask(task: TaskEntity)

    @Query("DELETE FROM tasks WHERE id = :taskId")
    suspend fun deleteTaskById(taskId: String)

    @Query("DELETE FROM tasks")
    suspend fun clearAllTasks()
}

package com.example.di

import android.content.Context
import androidx.room.Room
import com.example.data.local.TaskDao
import com.example.data.local.TaskDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Hilt Dependency Injection module providing Room Database instances.
 *
 * Architectural Pattern & Decision Rationale:
 * - Installed in [SingletonComponent] to ensure a single, application-wide instance of Room Database.
 * - Why preferred: Managing database instances via DI prevents expensive re-creation of database connections
 *   and thread pool instances across Fragments or Activities.
 */
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideTaskDatabase(
        @ApplicationContext context: Context
    ): TaskDatabase {
        return Room.databaseBuilder(
            context,
            TaskDatabase::class.java,
            "task_manager_db"
        )
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    fun provideTaskDao(database: TaskDatabase): TaskDao {
        return database.taskDao()
    }
}

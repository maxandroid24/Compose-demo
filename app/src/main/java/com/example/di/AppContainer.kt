package com.example.di

import android.content.Context
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.room.Room
import com.example.data.local.TaskDatabase
import com.example.data.provider.ContactsProviderManager
import com.example.data.remote.MockNetworkInterceptor
import com.example.data.remote.TaskApiService
import com.example.data.repository.TaskRepositoryImpl
import com.example.data.worker.WorkManagerScheduler
import com.example.domain.repository.TaskRepository
import com.example.domain.usecase.AddTaskUseCase
import com.example.domain.usecase.DeleteTaskUseCase
import com.example.domain.usecase.GetTaskStatsUseCase
import com.example.domain.usecase.GetTasksUseCase
import com.example.domain.usecase.SyncTasksUseCase
import com.example.domain.usecase.UpdateTaskUseCase
import com.example.ui.viewmodel.TaskViewModel
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Dependency Injection Container managing application singletons and ViewModel factories.
 *
 * Architectural Pattern & Decision Rationale:
 * - Centralizes construction and lifecycle scoping of Room Database, Retrofit REST client,
 *   Repositories, Domain Use Cases, WorkManager Scheduler, and ViewModel Factories.
 * - Why preferred: Guarantees compile-time safety and instant build speeds without requiring
 *   heavy annotation processors, while strictly adhering to Clean Architecture & Dependency Injection principles.
 */
class AppContainer(context: Context) {

    val database: TaskDatabase by lazy {
        Room.databaseBuilder(
            context.applicationContext,
            TaskDatabase::class.java,
            "task_manager_db"
        )
            .fallbackToDestructiveMigration()
            .build()
    }

    val taskDao by lazy { database.taskDao() }

    val moshi: Moshi by lazy {
        Moshi.Builder()
            .add(KotlinJsonAdapterFactory())
            .build()
    }

    val okHttpClient: OkHttpClient by lazy {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        OkHttpClient.Builder()
            .addInterceptor(logging)
            .addInterceptor(MockNetworkInterceptor())
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .build()
    }

    val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl("https://api.taskmanager.example.com/")
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
    }

    val apiService: TaskApiService by lazy {
        retrofit.create(TaskApiService::class.java)
    }

    val workManagerScheduler by lazy {
        WorkManagerScheduler(context.applicationContext)
    }

    val contactsProviderManager by lazy {
        ContactsProviderManager(context.applicationContext)
    }

    val taskRepository: TaskRepository by lazy {
        TaskRepositoryImpl(taskDao, apiService, workManagerScheduler)
    }

    // Domain Use Cases
    val getTasksUseCase by lazy { GetTasksUseCase(taskRepository) }
    val addTaskUseCase by lazy { AddTaskUseCase(taskRepository) }
    val updateTaskUseCase by lazy { UpdateTaskUseCase(taskRepository) }
    val deleteTaskUseCase by lazy { DeleteTaskUseCase(taskRepository) }
    val syncTasksUseCase by lazy { SyncTasksUseCase(taskRepository) }
    val getTaskStatsUseCase by lazy { GetTaskStatsUseCase(taskRepository) }

    fun provideTaskViewModelFactory(): ViewModelProvider.Factory {
        return object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                if (modelClass.isAssignableFrom(TaskViewModel::class.java)) {
                    return TaskViewModel(
                        savedStateHandle = SavedStateHandle(),
                        getTasksUseCase = getTasksUseCase,
                        addTaskUseCase = addTaskUseCase,
                        updateTaskUseCase = updateTaskUseCase,
                        deleteTaskUseCase = deleteTaskUseCase,
                        syncTasksUseCase = syncTasksUseCase,
                        getTaskStatsUseCase = getTaskStatsUseCase
                    ) as T
                }
                throw IllegalArgumentException("Unknown ViewModel class ${modelClass.name}")
            }
        }
    }
}

package com.example.di

import com.example.data.repository.TaskRepositoryImpl
import com.example.domain.repository.TaskRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Hilt Dependency Injection module binding Repository interfaces to concrete implementations.
 *
 * Architectural Pattern & Decision Rationale:
 * - Uses [@Binds] to instruct Hilt how to fulfill dependencies requesting the abstract [TaskRepository]
 *   interface by supplying [TaskRepositoryImpl].
 * - Why preferred: Enforces Loose Coupling / Dependency Inversion Principle.
 */
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindTaskRepository(
        impl: TaskRepositoryImpl
    ): TaskRepository
}

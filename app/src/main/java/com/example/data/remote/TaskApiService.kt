package com.example.data.remote

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path

/**
 * Retrofit interface defining REST API HTTP endpoints for remote task synchronization.
 *
 * Architectural Pattern & Decision Rationale:
 * - Retrofit turns HTTP APIs into clean Kotlin interfaces using standard annotations.
 * - Why preferred: Retrofit handles connection pooling, OkHttp interceptors, serialization,
 *   and coroutines support seamlessly out of the box.
 */
interface TaskApiService {

    @GET("api/v1/tasks")
    suspend fun getRemoteTasks(): Response<List<TaskDto>>

    @POST("api/v1/tasks")
    suspend fun createRemoteTask(@Body taskDto: TaskDto): Response<TaskDto>

    @PUT("api/v1/tasks/{id}")
    suspend fun updateRemoteTask(@Path("id") id: String, @Body taskDto: TaskDto): Response<TaskDto>

    @DELETE("api/v1/tasks/{id}")
    suspend fun deleteRemoteTask(@Path("id") id: String): Response<Unit>

    @POST("api/v1/tasks/sync")
    suspend fun syncBatch(@Body request: SyncRequestDto): Response<SyncResponseDto>
}

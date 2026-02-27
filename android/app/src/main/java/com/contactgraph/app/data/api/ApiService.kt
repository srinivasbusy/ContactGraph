package com.contactgraph.app.data.api

import com.contactgraph.app.data.model.ContactSyncRequest
import com.contactgraph.app.data.model.DirectContact
import com.contactgraph.app.data.model.NetworkStats
import com.contactgraph.app.data.model.SearchResponse
import com.contactgraph.app.data.model.UserResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {

    @POST("api/v1/auth/google")
    suspend fun authenticateWithGoogle(
        @Body body: Map<String, String>
    ): Response<UserResponse>

    @POST("api/v1/contacts/sync")
    suspend fun syncContacts(
        @Body request: ContactSyncRequest
    ): Response<Unit>

    @PUT("api/v1/contacts/update")
    suspend fun updateContact(
        @Body body: Map<String, String>
    ): Response<Unit>

    @DELETE("api/v1/contacts/{phone}")
    suspend fun removeContact(
        @Path("phone") phone: String
    ): Response<Unit>

    @GET("api/v1/search")
    suspend fun search(
        @Query("q") query: String,
        @Query("max_depth") maxDepth: Int = 6
    ): Response<SearchResponse>

    @GET("api/v1/network/stats")
    suspend fun getNetworkStats(): Response<NetworkStats>

    @GET("api/v1/network/direct")
    suspend fun getDirectContacts(): Response<List<DirectContact>>
}

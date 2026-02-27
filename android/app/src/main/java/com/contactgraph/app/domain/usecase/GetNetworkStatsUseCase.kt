package com.contactgraph.app.domain.usecase

import com.contactgraph.app.data.api.ApiService
import com.contactgraph.app.data.model.DirectContact
import com.contactgraph.app.data.model.NetworkStats
import javax.inject.Inject

data class NetworkData(
    val stats: NetworkStats,
    val directContacts: List<DirectContact>
)

class GetNetworkStatsUseCase @Inject constructor(
    private val apiService: ApiService
) {
    suspend operator fun invoke(): Result<NetworkData> {
        return try {
            val statsResponse = apiService.getNetworkStats()
            val contactsResponse = apiService.getDirectContacts()

            val stats = statsResponse.body()
            val contacts = contactsResponse.body()
            if (statsResponse.isSuccessful && contactsResponse.isSuccessful
                && stats != null && contacts != null) {
                Result.success(
                    NetworkData(
                        stats = stats,
                        directContacts = contacts
                    )
                )
            } else {
                Result.failure(Exception("Failed to load network data"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

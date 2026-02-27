package com.contactgraph.app.data.model

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class ChainNode(
    val id: String,
    val name: String,
    @Json(name = "phone_number") val phoneNumber: String? = null
)

@JsonClass(generateAdapter = true)
data class ConnectionChain(
    val degree: Int,
    val path: List<ChainNode>,
    @Json(name = "target_name") val targetName: String? = null,
    @Json(name = "target_phone") val targetPhone: String? = null
)

@JsonClass(generateAdapter = true)
data class SearchResponse(
    val found: Boolean,
    val chain: ConnectionChain?
)

@JsonClass(generateAdapter = true)
data class NetworkStats(
    @Json(name = "total_contacts") val totalContacts: Int,
    @Json(name = "app_users") val appUsers: Int,
    @Json(name = "non_app_users") val nonAppUsers: Int
)

@JsonClass(generateAdapter = true)
data class DirectContact(
    val id: String,
    val name: String,
    @Json(name = "phone_number") val phoneNumber: String,
    @Json(name = "is_app_user") val isAppUser: Boolean = false
)

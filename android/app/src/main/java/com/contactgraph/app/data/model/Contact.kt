package com.contactgraph.app.data.model

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class Contact(
    val name: String,
    @Json(name = "phone_number") val phoneNumber: String,
    val email: String? = null
)

@JsonClass(generateAdapter = true)
data class ContactData(
    val name: String,
    @Json(name = "phone_number") val phoneNumber: String,
    val email: String? = null
)

@JsonClass(generateAdapter = true)
data class ContactSyncRequest(
    val contacts: List<ContactData>
)

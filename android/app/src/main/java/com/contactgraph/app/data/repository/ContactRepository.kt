package com.contactgraph.app.data.repository

import android.content.ContentResolver
import android.database.Cursor
import android.provider.ContactsContract
import com.contactgraph.app.data.api.ApiService
import com.contactgraph.app.data.model.ContactData
import com.contactgraph.app.data.model.ContactSyncRequest
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ContactRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun syncContacts(contacts: List<ContactData>): Result<Unit> {
        return try {
            val response = apiService.syncContacts(ContactSyncRequest(contacts))
            if (response.isSuccessful) Result.success(Unit)
            else Result.failure(Exception("Sync failed: ${response.code()}"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateContact(name: String, phoneNumber: String, action: String): Result<Unit> {
        return try {
            val response = apiService.updateContact(
                mapOf(
                    "name" to name,
                    "phone_number" to phoneNumber,
                    "action" to action
                )
            )
            if (response.isSuccessful) Result.success(Unit)
            else Result.failure(Exception("Update failed: ${response.code()}"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun removeContact(phone: String): Result<Unit> {
        return try {
            val response = apiService.removeContact(phone)
            if (response.isSuccessful) Result.success(Unit)
            else Result.failure(Exception("Remove failed: ${response.code()}"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun readDeviceContacts(contentResolver: ContentResolver): List<ContactData> {
        val contacts = mutableListOf<ContactData>()
        val seen = mutableSetOf<String>()

        val cursor: Cursor? = contentResolver.query(
            ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
            arrayOf(
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
                ContactsContract.CommonDataKinds.Phone.NUMBER
            ),
            null,
            null,
            ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME + " ASC"
        )

        cursor?.use {
            val nameIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
            val numberIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)

            while (it.moveToNext()) {
                val name = it.getString(nameIndex) ?: continue
                val rawNumber = it.getString(numberIndex) ?: continue
                // Normalize phone number by removing non-digit chars except leading +
                val phone = normalizePhone(rawNumber)
                if (phone.isNotBlank() && seen.add(phone)) {
                    contacts.add(ContactData(name = name, phoneNumber = phone))
                }
            }
        }

        return contacts
    }

    private fun normalizePhone(raw: String): String {
        val digits = raw.filter { it.isDigit() || it == '+' }
        return if (digits.startsWith("+")) digits
        else digits.filter { it.isDigit() }
    }
}

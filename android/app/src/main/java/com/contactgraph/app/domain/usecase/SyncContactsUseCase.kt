package com.contactgraph.app.domain.usecase

import android.content.ContentResolver
import com.contactgraph.app.data.repository.ContactRepository
import javax.inject.Inject

class SyncContactsUseCase @Inject constructor(
    private val contactRepository: ContactRepository
) {
    suspend operator fun invoke(contentResolver: ContentResolver): Result<Unit> {
        return try {
            val contacts = contactRepository.readDeviceContacts(contentResolver)
            if (contacts.isEmpty()) {
                return Result.success(Unit)
            }
            contactRepository.syncContacts(contacts)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

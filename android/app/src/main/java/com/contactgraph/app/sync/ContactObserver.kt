package com.contactgraph.app.sync

import android.content.ContentResolver
import android.database.ContentObserver
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.provider.ContactsContract
import com.contactgraph.app.domain.usecase.SyncContactsUseCase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ContactObserver @Inject constructor(
    private val syncContactsUseCase: SyncContactsUseCase
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var observer: ContentObserver? = null

    fun register(contentResolver: ContentResolver) {
        if (observer != null) return

        observer = object : ContentObserver(Handler(Looper.getMainLooper())) {
            override fun onChange(selfChange: Boolean, uri: Uri?) {
                super.onChange(selfChange, uri)
                // Debounce: trigger sync on contact changes
                scope.launch {
                    syncContactsUseCase(contentResolver)
                }
            }
        }

        contentResolver.registerContentObserver(
            ContactsContract.Contacts.CONTENT_URI,
            true,
            observer!!
        )
    }

    fun unregister(contentResolver: ContentResolver) {
        observer?.let {
            contentResolver.unregisterContentObserver(it)
            observer = null
        }
    }
}

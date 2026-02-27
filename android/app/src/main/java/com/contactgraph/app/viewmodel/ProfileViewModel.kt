package com.contactgraph.app.viewmodel

import android.content.SharedPreferences
import androidx.core.content.edit
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.contactgraph.app.data.model.User
import com.contactgraph.app.data.repository.AuthRepository
import com.google.firebase.auth.FirebaseUser
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject
import javax.inject.Named

data class ProfileUser(
    val displayName: String?,
    val email: String?,
    val photoUrl: String?
)

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    @Named("default_prefs") private val prefs: SharedPreferences
) : ViewModel() {

    companion object {
        private const val KEY_SYNC_ENABLED = "sync_enabled"
    }

    private val _currentUser = MutableStateFlow<ProfileUser?>(null)
    val currentUser: StateFlow<ProfileUser?> = _currentUser.asStateFlow()

    private val _syncEnabled = MutableStateFlow(prefs.getBoolean(KEY_SYNC_ENABLED, true))
    val syncEnabled: StateFlow<Boolean> = _syncEnabled.asStateFlow()

    fun loadUser() {
        val firebaseUser: FirebaseUser? = authRepository.getCurrentUser()
        _currentUser.value = firebaseUser?.let {
            ProfileUser(
                displayName = it.displayName,
                email = it.email,
                photoUrl = it.photoUrl?.toString()
            )
        }
    }

    fun signOut() {
        authRepository.signOut()
        _currentUser.value = null
    }

    fun updateSyncSettings(enabled: Boolean) {
        _syncEnabled.value = enabled
        prefs.edit { putBoolean(KEY_SYNC_ENABLED, enabled) }
    }
}

package com.contactgraph.app.data.repository

import android.content.SharedPreferences
import com.contactgraph.app.data.api.ApiService
import com.contactgraph.app.data.model.User
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.GoogleAuthProvider
import kotlinx.coroutines.tasks.await
import javax.inject.Inject
import javax.inject.Named
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val apiService: ApiService,
    private val firebaseAuth: FirebaseAuth,
    @Named("encrypted_prefs") private val encryptedPrefs: SharedPreferences
) {
    companion object {
        private const val KEY_AUTH_TOKEN = "auth_token"
        private const val KEY_USER_ID = "user_id"
    }

    suspend fun signInWithGoogle(idToken: String): Result<User> {
        return try {
            // Authenticate with Firebase
            val credential = GoogleAuthProvider.getCredential(idToken, null)
            val firebaseResult = firebaseAuth.signInWithCredential(credential).await()
            val firebaseUser = firebaseResult.user
                ?: return Result.failure(Exception("Firebase auth failed"))

            val firebaseIdToken = firebaseUser.getIdToken(false).await().token
                ?: return Result.failure(Exception("Failed to get Firebase ID token"))

            // Authenticate with backend
            val response = apiService.authenticateWithGoogle(
                mapOf("id_token" to firebaseIdToken)
            )

            if (response.isSuccessful) {
                val userResponse = response.body()!!
                encryptedPrefs.edit()
                    .putString(KEY_AUTH_TOKEN, userResponse.token)
                    .putString(KEY_USER_ID, userResponse.user.id)
                    .commit()
                Result.success(userResponse.user)
            } else {
                Result.failure(Exception("Backend auth failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun getCurrentUser(): com.google.firebase.auth.FirebaseUser? {
        return firebaseAuth.currentUser
    }

    fun getAuthToken(): String? {
        return encryptedPrefs.getString(KEY_AUTH_TOKEN, null)
    }

    fun signOut() {
        firebaseAuth.signOut()
        encryptedPrefs.edit()
            .remove(KEY_AUTH_TOKEN)
            .remove(KEY_USER_ID)
            .apply()
    }

    fun isLoggedIn(): Boolean {
        return firebaseAuth.currentUser != null && getAuthToken() != null
    }
}

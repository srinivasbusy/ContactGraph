package com.contactgraph.app.data.repository

import android.content.SharedPreferences
import androidx.core.content.edit
import com.contactgraph.app.data.api.ApiService
import com.contactgraph.app.data.model.ConnectionChain
import com.contactgraph.app.data.model.SearchResponse
import com.squareup.moshi.Moshi
import com.squareup.moshi.Types
import javax.inject.Inject
import javax.inject.Named
import javax.inject.Singleton

@Singleton
class SearchRepository @Inject constructor(
    private val apiService: ApiService,
    @Named("default_prefs") private val prefs: SharedPreferences,
    private val moshi: Moshi
) {
    companion object {
        private const val KEY_RECENT_SEARCHES = "recent_searches"
        private const val MAX_RECENT_SEARCHES = 10
    }

    suspend fun search(query: String, maxDepth: Int = 6): Result<SearchResponse> {
        return try {
            val response = apiService.search(query, maxDepth)
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Search failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun getRecentSearches(): List<String> {
        val json = prefs.getString(KEY_RECENT_SEARCHES, null) ?: return emptyList()
        return try {
            val type = Types.newParameterizedType(List::class.java, String::class.java)
            val adapter = moshi.adapter<List<String>>(type)
            adapter.fromJson(json) ?: emptyList()
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun saveRecentSearch(query: String) {
        val current = getRecentSearches().toMutableList()
        current.remove(query) // avoid duplicates, move to top
        current.add(0, query)
        val trimmed = current.take(MAX_RECENT_SEARCHES)
        val type = Types.newParameterizedType(List::class.java, String::class.java)
        val adapter = moshi.adapter<List<String>>(type)
        prefs.edit { putString(KEY_RECENT_SEARCHES, adapter.toJson(trimmed)) }
    }

    fun removeRecentSearch(query: String) {
        val current = getRecentSearches().toMutableList()
        current.remove(query)
        val type = Types.newParameterizedType(List::class.java, String::class.java)
        val adapter = moshi.adapter<List<String>>(type)
        prefs.edit { putString(KEY_RECENT_SEARCHES, adapter.toJson(current)) }
    }
}

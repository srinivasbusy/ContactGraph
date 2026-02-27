package com.contactgraph.app.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.contactgraph.app.data.model.ConnectionChain
import com.contactgraph.app.data.repository.SearchRepository
import com.contactgraph.app.domain.usecase.SearchConnectionUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class HomeUiState {
    object Idle : HomeUiState()
    object Loading : HomeUiState()
    data class SearchResult(val connectionChain: ConnectionChain?) : HomeUiState()
    data class Error(val message: String) : HomeUiState()
}

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val searchConnectionUseCase: SearchConnectionUseCase,
    private val searchRepository: SearchRepository
) : ViewModel() {

    private val _searchUiState = MutableStateFlow<HomeUiState>(HomeUiState.Idle)
    val searchUiState: StateFlow<HomeUiState> = _searchUiState.asStateFlow()

    private val _recentSearches = MutableStateFlow<List<String>>(emptyList())
    val recentSearches: StateFlow<List<String>> = _recentSearches.asStateFlow()

    fun loadRecentSearches() {
        _recentSearches.value = searchRepository.getRecentSearches()
    }

    fun search(query: String) {
        viewModelScope.launch {
            _searchUiState.value = HomeUiState.Loading
            val result = searchConnectionUseCase(query)
            _searchUiState.value = if (result.isSuccess) {
                val response = result.getOrNull()
                HomeUiState.SearchResult(response?.chain)
            } else {
                HomeUiState.Error(result.exceptionOrNull()?.message ?: "Search failed")
            }
        }
    }

    fun saveRecentSearch(query: String) {
        searchRepository.saveRecentSearch(query)
        _recentSearches.value = searchRepository.getRecentSearches()
    }

    fun removeRecentSearch(query: String) {
        searchRepository.removeRecentSearch(query)
        _recentSearches.value = searchRepository.getRecentSearches()
    }

    fun clearSearch() {
        _searchUiState.value = HomeUiState.Idle
    }
}

package com.contactgraph.app.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.contactgraph.app.data.model.DirectContact
import com.contactgraph.app.data.model.NetworkStats
import com.contactgraph.app.domain.usecase.GetNetworkStatsUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class NetworkUiState {
    object Loading : NetworkUiState()
    data class Success(
        val stats: NetworkStats,
        val contacts: List<DirectContact>
    ) : NetworkUiState()
    data class Error(val message: String) : NetworkUiState()
}

@HiltViewModel
class NetworkViewModel @Inject constructor(
    private val getNetworkStatsUseCase: GetNetworkStatsUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<NetworkUiState>(NetworkUiState.Loading)
    val uiState: StateFlow<NetworkUiState> = _uiState.asStateFlow()

    private val _isRefreshing = MutableStateFlow(false)
    val isRefreshing: StateFlow<Boolean> = _isRefreshing.asStateFlow()

    fun load() {
        viewModelScope.launch {
            _uiState.value = NetworkUiState.Loading
            fetchData()
        }
    }

    fun refresh() {
        viewModelScope.launch {
            _isRefreshing.value = true
            fetchData()
            _isRefreshing.value = false
        }
    }

    private suspend fun fetchData() {
        val result = getNetworkStatsUseCase()
        _uiState.value = if (result.isSuccess) {
            val data = result.getOrNull()!!
            NetworkUiState.Success(data.stats, data.directContacts)
        } else {
            NetworkUiState.Error(result.exceptionOrNull()?.message ?: "Failed to load network")
        }
    }
}

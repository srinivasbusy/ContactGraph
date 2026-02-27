package com.contactgraph.app.domain.usecase

import com.contactgraph.app.data.model.SearchResponse
import com.contactgraph.app.data.repository.SearchRepository
import javax.inject.Inject

class SearchConnectionUseCase @Inject constructor(
    private val searchRepository: SearchRepository
) {
    suspend operator fun invoke(query: String, maxDepth: Int = 6): Result<SearchResponse> {
        if (query.isBlank()) {
            return Result.failure(IllegalArgumentException("Query cannot be blank"))
        }
        return searchRepository.search(query.trim(), maxDepth)
    }
}

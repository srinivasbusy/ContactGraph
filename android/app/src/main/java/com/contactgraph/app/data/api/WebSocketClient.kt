package com.contactgraph.app.data.api

import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.receiveAsFlow
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import javax.inject.Inject
import javax.inject.Singleton

sealed class WsEvent {
    data class Message(val text: String) : WsEvent()
    data class Error(val throwable: Throwable) : WsEvent()
    object Closed : WsEvent()
}

@Singleton
class WebSocketClient @Inject constructor(
    private val okHttpClient: OkHttpClient
) {
    private var webSocket: WebSocket? = null
    private val eventChannel = Channel<WsEvent>(Channel.BUFFERED)

    val events: Flow<WsEvent> = eventChannel.receiveAsFlow()

    fun connect(url: String, token: String) {
        val request = Request.Builder()
            .url(url)
            .addHeader("Authorization", "Bearer $token")
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                eventChannel.trySend(WsEvent.Message(text))
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                eventChannel.trySend(WsEvent.Error(t))
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                eventChannel.trySend(WsEvent.Closed)
            }
        })
    }

    fun send(message: String): Boolean {
        return webSocket?.send(message) ?: false
    }

    fun disconnect() {
        webSocket?.close(1000, "Client disconnect")
        webSocket = null
    }
}

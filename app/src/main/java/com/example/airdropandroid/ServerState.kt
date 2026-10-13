package com.example.airdropandroid

import android.os.Handler
import android.os.Looper

object ServerState {
    const val IDLE_STATUS = "⚪ الحالة: متوقف"

    var running = false
    var starting = false
    var status = IDLE_STATUS
    var ssid = ""
    var pass = ""
    var url = ""
    var wifiPayload = ""
    val receivedLog = ArrayDeque<String>()

    var listener: (() -> Unit)? = null
    private val main = Handler(Looper.getMainLooper())

    fun changed() {
        main.post { listener?.invoke() }
    }

    fun reset() {
        running = false
        starting = false
        status = IDLE_STATUS
        ssid = ""
        pass = ""
        url = ""
        wifiPayload = ""
        receivedLog.clear()
        changed()
    }
}

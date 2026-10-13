package com.example.airdropandroid

import android.net.Uri
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.atomic.AtomicInteger

data class SharedItem(
    val id: Int,
    val name: String,
    val size: Long,
    val mime: String,
    val uri: Uri
)

object FileStore {
    private val counter = AtomicInteger(0)
    val shared = CopyOnWriteArrayList<SharedItem>()

    fun add(name: String, size: Long, mime: String, uri: Uri): SharedItem {
        shared.firstOrNull { it.uri == uri }?.let { return it }
        val item = SharedItem(counter.incrementAndGet(), name, size, mime, uri)
        shared.add(item)
        return item
    }

    fun find(id: Int): SharedItem? = shared.firstOrNull { it.id == id }

    fun clear() {
        shared.clear()
    }
}

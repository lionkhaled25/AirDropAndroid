package com.example.airdropandroid

import android.content.ContentValues
import android.content.Context
import android.provider.MediaStore
import fi.iki.elonen.NanoHTTPD
import fi.iki.elonen.NanoHTTPD.IHTTPSession
import fi.iki.elonen.NanoHTTPD.Method
import fi.iki.elonen.NanoHTTPD.Response
import org.json.JSONArray
import org.json.JSONObject
import java.net.URLConnection
import java.net.URLEncoder

class LocalServer(
    private val ctx: Context,
    port: Int,
    private val onReceived: (String, Long) -> Unit
) : NanoHTTPD(port) {

    override fun serve(session: IHTTPSession): Response {
        return try {
            val uri = session.uri
            when {
                session.method == Method.GET && (uri == "/" || uri == "/index.html") -> page()
                session.method == Method.GET && uri == "/api/files" -> listFiles()
                session.method == Method.GET && uri.startsWith("/download/") -> download(uri)
                session.method == Method.POST && uri == "/upload" -> upload(session)
                else -> text(Response.Status.NOT_FOUND, "Not found")
            }
        } catch (e: Exception) {
            text(Response.Status.INTERNAL_ERROR, "Error: " + e.message)
        }
    }

    private fun text(status: Response.IStatus, body: String): Response =
        NanoHTTPD.newFixedLengthResponse(status, "text/plain; charset=utf-8", body)

    private fun page(): Response {
        val html = ctx.assets.open("index.html").use { String(it.readBytes(), Charsets.UTF_8) }
        val res = NanoHTTPD.newFixedLengthResponse(Response.Status.OK, "text/html; charset=utf-8", html)
        res.addHeader("Cache-Control", "no-cache")
        return res
    }

    private fun listFiles(): Response {
        val arr = JSONArray()
        for (f in FileStore.shared) {
            arr.put(
                JSONObject()
                    .put("id", f.id)
                    .put("name", f.name)
                    .put("size", f.size)
            )
        }
        val res = NanoHTTPD.newFixedLengthResponse(
            Response.Status.OK, "application/json; charset=utf-8", arr.toString()
        )
        res.addHeader("Cache-Control", "no-store")
        return res
    }

    // تحميل ملف من الموبايل إلى الأيباد
    private fun download(uri: String): Response {
        val id = uri.removePrefix("/download/").toIntOrNull()
            ?: return text(Response.Status.BAD_REQUEST, "Bad id")
        val item = FileStore.find(id) ?: return text(Response.Status.NOT_FOUND, "Not found")
        val input = ctx.contentResolver.openInputStream(item.uri)
            ?: return text(Response.Status.NOT_FOUND, "Cannot open file")

        val res = if (item.size >= 0) {
            NanoHTTPD.newFixedLengthResponse(Response.Status.OK, item.mime, input, item.size)
        } else {
            NanoHTTPD.newChunkedResponse(Response.Status.OK, item.mime, input)
        }
        val encoded = URLEncoder.encode(item.name, "UTF-8").replace("+", "%20")
        res.addHeader("Content-Disposition", "attachment; filename*=UTF-8''" + encoded)
        return res
    }

    // رفع ملف من الأيباد إلى الموبايل (streaming مباشر بدون ملفات مؤقتة)
    private fun upload(session: IHTTPSession): Response {
        val length = session.headers["content-length"]?.toLongOrNull()
            ?: return text(Response.Status.BAD_REQUEST, "Missing Content-Length")
        val rawName = session.parms["name"] ?: ("file_" + System.currentTimeMillis())
        val name = rawName.replace(Regex("[\\\\/:*?\"<>|]"), "_").trim().ifEmpty { "file" }
        val mime = URLConnection.guessContentTypeFromName(name) ?: "application/octet-stream"

        val resolver = ctx.contentResolver
        val values = ContentValues().apply {
            put(MediaStore.Downloads.DISPLAY_NAME, name)
            put(MediaStore.Downloads.MIME_TYPE, mime)
            put(MediaStore.Downloads.RELATIVE_PATH, "Download/AirDrop")
            put(MediaStore.Downloads.IS_PENDING, 1)
        }
        val target = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
            ?: return text(Response.Status.INTERNAL_ERROR, "Cannot create file")

        var total = 0L
        try {
            val out = resolver.openOutputStream(target)
                ?: throw IllegalStateException("Cannot open output")
            out.use {
                val buf = ByteArray(64 * 1024)
                val input = session.inputStream
                while (total < length) {
                    val want = minOf(buf.size.toLong(), length - total).toInt()
                    val r = input.read(buf, 0, want)
                    if (r < 0) break
                    it.write(buf, 0, r)
                    total += r
                }
            }
            if (total != length) {
                resolver.delete(target, null, null)
                return text(Response.Status.INTERNAL_ERROR, "Incomplete upload")
            }
        } catch (e: Exception) {
            resolver.delete(target, null, null)
            throw e
        }

        val done = ContentValues().apply { put(MediaStore.Downloads.IS_PENDING, 0) }
        resolver.update(target, done, null, null)
        onReceived(name, total)

        return NanoHTTPD.newFixedLengthResponse(
            Response.Status.OK, "application/json; charset=utf-8", "{\"ok\":true}"
        )
    }
}

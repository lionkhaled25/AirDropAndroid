package com.example.airdropandroid

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.graphics.drawable.Icon
import android.net.wifi.WifiManager
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.PowerManager
import java.io.IOException
import java.net.Inet4Address
import java.net.NetworkInterface

class ServerService : Service() {

    companion object {
        const val ACTION_START = "com.example.airdropandroid.START"
        const val ACTION_STOP = "com.example.airdropandroid.STOP"
        const val CHANNEL_ID = "airdrop_server"
        const val NOTIF_ID = 1
        const val PORT = 8080
    }

    private var server: LocalServer? = null
    private var reservation: WifiManager.LocalOnlyHotspotReservation? = null
    private var wakeLock: PowerManager.WakeLock? = null
    private val handler = Handler(Looper.getMainLooper())

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            shutdown()
            return START_NOT_STICKY
        }

        // لازم نستدعي startForeground فوراً بعد startForegroundService
        createChannel()
        val text = if (ServerState.running) "شغال على ${ServerState.url}" else "جاري تشغيل الشبكة..."
        startForeground(
            NOTIF_ID,
            buildNotification(text),
            ServiceInfo.FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE
        )

        if (!ServerState.running && !ServerState.starting) startAll()
        return START_NOT_STICKY
    }

    // ───────── Start ─────────

    private fun startAll() {
        ServerState.starting = true
        ServerState.status = "🟡 جاري تشغيل الشبكة..."
        ServerState.changed()
        acquireWakeLock()

        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            fail("يرجى منح إذن الموقع أولاً")
            return
        }

        val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
        try {
            wifiManager.startLocalOnlyHotspot(object : WifiManager.LocalOnlyHotspotCallback() {
                override fun onStarted(res: WifiManager.LocalOnlyHotspotReservation?) {
                    super.onStarted(res)
                    reservation = res
                    val (ssid, pass) = readCredentials(res)
                    handler.postDelayed({ onHotspotReady(ssid, pass) }, 700)
                }

                override fun onStopped() {
                    super.onStopped()
                    if (ServerState.running) shutdown()
                }

                override fun onFailed(reason: Int) {
                    super.onFailed(reason)
                    val msg = when (reason) {
                        ERROR_INCOMPATIBLE_MODE -> "اقفل الهوتسبوت العادي أو الـ Wi-Fi Direct وجرب تاني"
                        ERROR_TETHERING_DISALLOWED -> "الهوتسبوت ممنوع على الجهاز ده"
                        ERROR_NO_CHANNEL -> "مفيش قناة واي فاي متاحة"
                        else -> "خطأ غير معروف ($reason). تأكد إن الـ GPS شغال"
                    }
                    fail("فشل تشغيل الشبكة: $msg")
                }
            }, null)
        } catch (e: SecurityException) {
            fail("الإذن مرفوض - فعّل الموقع وامنح الأذونات")
        }
    }

    private fun onHotspotReady(ssid: String, pass: String) {
        if (reservation == null || !ServerState.starting) return

        val cleanSsid = ssid.trim('"')
        val ip = findHotspotIp()
        val url = "http://$ip:$PORT"

        try {
            server = LocalServer(applicationContext, PORT) { name, size ->
                handler.post {
                    ServerState.receivedLog.addFirst("✅ $name (${fmtSize(size)})")
                    while (ServerState.receivedLog.size > 5) ServerState.receivedLog.removeLast()
                    ServerState.changed()
                }
            }.also { it.start(60000, true) }
        } catch (e: IOException) {
            fail("فشل تشغيل السيرفر: ${e.message}")
            return
        }

        ServerState.ssid = cleanSsid
        ServerState.pass = pass
        ServerState.url = url
        ServerState.wifiPayload = "WIFI:T:WPA;S:${esc(cleanSsid)};P:${esc(pass)};;"
        ServerState.starting = false
        ServerState.running = true
        ServerState.status = "🟢 شغال بنجاح"
        ServerState.changed()

        getSystemService(NotificationManager::class.java)
            .notify(NOTIF_ID, buildNotification("شغال على $url"))
    }

    private fun fail(msg: String) {
        cleanup()
        ServerState.reset()
        ServerState.status = "🔴 $msg"
        ServerState.changed()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    // ───────── Stop ─────────

    private fun cleanup() {
        try { server?.stop() } catch (_: Exception) {}
        server = null
        try { reservation?.close() } catch (_: Exception) {}
        reservation = null
        releaseWakeLock()
        FileStore.clear()
    }

    private fun shutdown() {
        cleanup()
        ServerState.reset()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    override fun onDestroy() {
        cleanup()
        if (ServerState.running || ServerState.starting) ServerState.reset()
        super.onDestroy()
    }

    // ───────── Wake lock ─────────

    private fun acquireWakeLock() {
        if (wakeLock?.isHeld == true) return
        val pm = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "AirDrop:server").apply {
            setReferenceCounted(false)
            acquire()
        }
    }

    private fun releaseWakeLock() {
        try {
            if (wakeLock?.isHeld == true) wakeLock?.release()
        } catch (_: Exception) {}
        wakeLock = null
    }

    // ───────── Notification ─────────

    private fun createChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID, "AirDrop Local", NotificationManager.IMPORTANCE_LOW
        )
        channel.description = "السيرفر شغال في الخلفية"
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
    }

    private fun buildNotification(text: String): Notification {
        val openIntent = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        val stopIntent = PendingIntent.getService(
            this, 1,
            Intent(this, ServerService::class.java).setAction(ACTION_STOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        val stopAction = Notification.Action.Builder(
            Icon.createWithResource(this, R.drawable.ic_launcher_foreground),
            "إيقاف وخروج",
            stopIntent
        ).build()

        return Notification.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentTitle("AirDrop Local")
            .setContentText(text)
            .setContentIntent(openIntent)
            .setOngoing(true)
            .addAction(stopAction)
            .build()
    }

    // ───────── Helpers ─────────

    @Suppress("DEPRECATION")
    private fun readCredentials(r: WifiManager.LocalOnlyHotspotReservation?): Pair<String, String> {
        if (r == null) return Pair("Unknown", "Unknown")
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            val c = r.softApConfiguration
            Pair(c.ssid ?: "Unknown", c.passphrase ?: "Unknown")
        } else {
            val c = r.wifiConfiguration
            Pair(c?.SSID ?: "Unknown", c?.preSharedKey ?: "Unknown")
        }
    }

    private fun findHotspotIp(): String {
        val candidates = mutableListOf<Pair<String, String>>()
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            if (interfaces != null) {
                for (ni in interfaces) {
                    if (!ni.isUp || ni.isLoopback) continue
                    for (addr in ni.inetAddresses) {
                        if (addr is Inet4Address && !addr.isLoopbackAddress) {
                            addr.hostAddress?.let { candidates.add(Pair(ni.name, it)) }
                        }
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        val preferred = candidates.firstOrNull {
            it.first.startsWith("ap") || it.first.startsWith("swlan") ||
                    Regex("wlan[1-9].*").matches(it.first)
        }
        val fallback = candidates.firstOrNull {
            it.first != "wlan0" && !it.first.startsWith("rmnet") && !it.first.startsWith("ccmni")
        }
        return (preferred ?: fallback ?: candidates.firstOrNull())?.second ?: "192.168.43.1"
    }

    private fun esc(s: String): String =
        s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace(":", "\\:").replace("\"", "\\\"")

    private fun fmtSize(b: Long): String = when {
        b < 1024 -> "$b B"
        b < 1024 * 1024 -> String.format("%.1f KB", b / 1024.0)
        b < 1024L * 1024 * 1024 -> String.format("%.1f MB", b / 1048576.0)
        else -> String.format("%.2f GB", b / 1073741824.0)
    }
}

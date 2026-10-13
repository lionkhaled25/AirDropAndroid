import os

# شغّل السكريبت ده من أول فولدر الـ repo (بعد ما تكون شغلت setup_project_v2.py)
# بيعدّل 4 ملفات وبيضيف 2 جداد، وباقي الملفات زي ما هي.

files = {}

# ───────────────────────── Manifest ─────────────────────────

files["app/src/main/AndroidManifest.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <uses-permission android:name="android.permission.CHANGE_WIFI_STATE" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission
        android:name="android.permission.NEARBY_WIFI_DEVICES"
        android:usesPermissionFlags="neverForLocation" />

    <!-- تشغيل في الخلفية -->
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_CONNECTED_DEVICE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:label="AirDrop Local"
        android:supportsRtl="true"
        android:theme="@style/Theme.AirDrop">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:screenOrientation="portrait">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".ServerService"
            android:exported="false"
            android:foregroundServiceType="connectedDevice" />
    </application>

</manifest>
"""

# ───────────────────────── ServerState (حالة مشتركة بين السيرفس والواجهة) ─────────────────────────

files["app/src/main/java/com/example/airdropandroid/ServerState.kt"] = r'''package com.example.airdropandroid

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
'''

# ───────────────────────── ServerService (Foreground Service) ─────────────────────────

files["app/src/main/java/com/example/airdropandroid/ServerService.kt"] = r'''package com.example.airdropandroid

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
'''

# ───────────────────────── MainActivity (واجهة فقط، السيرفر في الـ Service) ─────────────────────────

files["app/src/main/java/com/example/airdropandroid/MainActivity.kt"] = r'''package com.example.airdropandroid

import android.Manifest
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import android.provider.OpenableColumns
import android.provider.Settings
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.google.android.material.button.MaterialButton
import com.google.android.material.button.MaterialButtonToggleGroup
import com.google.zxing.BarcodeFormat
import com.google.zxing.EncodeHintType
import com.google.zxing.qrcode.QRCodeWriter

class MainActivity : AppCompatActivity() {

    private lateinit var tvStatus: TextView
    private lateinit var btnStart: MaterialButton
    private lateinit var cardQr: View
    private lateinit var cardInfo: View
    private lateinit var cardFiles: View
    private lateinit var toggleGroup: MaterialButtonToggleGroup
    private lateinit var ivQr: ImageView
    private lateinit var tvQrHint: TextView
    private lateinit var tvInfo: TextView
    private lateinit var tvShared: TextView
    private lateinit var tvReceived: TextView
    private lateinit var btnPick: MaterialButton
    private lateinit var btnCopyUrl: MaterialButton
    private lateinit var btnCopyPass: MaterialButton
    private lateinit var btnBattery: MaterialButton

    private var wifiQr: Bitmap? = null
    private var urlQr: Bitmap? = null
    private var lastWifiPayload = ""
    private var lastUrl = ""

    private val defaultReceivedText = "الملفات المستلمة من الأيباد بتتحفظ في: Download/AirDrop"

    private val pickFiles =
        registerForActivityResult(ActivityResultContracts.OpenMultipleDocuments()) { uris ->
            addShared(uris)
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvStatus = findViewById(R.id.tvStatus)
        btnStart = findViewById(R.id.btnStart)
        cardQr = findViewById(R.id.cardQr)
        cardInfo = findViewById(R.id.cardInfo)
        cardFiles = findViewById(R.id.cardFiles)
        toggleGroup = findViewById(R.id.toggleGroup)
        ivQr = findViewById(R.id.ivQr)
        tvQrHint = findViewById(R.id.tvQrHint)
        tvInfo = findViewById(R.id.tvInfo)
        tvShared = findViewById(R.id.tvShared)
        tvReceived = findViewById(R.id.tvReceived)
        btnPick = findViewById(R.id.btnPick)
        btnCopyUrl = findViewById(R.id.btnCopyUrl)
        btnCopyPass = findViewById(R.id.btnCopyPass)
        btnBattery = createBatteryButton()

        checkPermissions()

        btnStart.setOnClickListener {
            if (ServerState.running) {
                startService(Intent(this, ServerService::class.java).setAction(ServerService.ACTION_STOP))
            } else if (!ServerState.starting) {
                if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                    tvStatus.text = "🔴 يرجى منح إذن الموقع أولاً"
                    checkPermissions()
                } else {
                    startForegroundService(
                        Intent(this, ServerService::class.java).setAction(ServerService.ACTION_START)
                    )
                }
            }
        }
        toggleGroup.addOnButtonCheckedListener { _, checkedId, isChecked ->
            if (isChecked) showQr(checkedId == R.id.btnTabWifi)
        }
        btnPick.setOnClickListener { pickFiles.launch(arrayOf("*/*")) }
        btnCopyUrl.setOnClickListener { copy("AirDrop URL", ServerState.url) }
        btnCopyPass.setOnClickListener { copy("Wi-Fi password", ServerState.pass) }
    }

    override fun onStart() {
        super.onStart()
        ServerState.listener = { refreshUi() }
        refreshUi()
    }

    override fun onStop() {
        ServerState.listener = null
        super.onStop()
    }

    // ───────── UI من حالة السيرفس ─────────

    private fun refreshUi() {
        val s = ServerState
        tvStatus.text = s.status
        btnStart.text = if (s.running) "إيقاف وخروج" else "تشغيل الشبكة والسيرفر"
        btnStart.isEnabled = !s.starting

        val vis = if (s.running) View.VISIBLE else View.GONE
        cardQr.visibility = vis
        cardInfo.visibility = vis
        cardFiles.visibility = vis

        if (!s.running) {
            lastWifiPayload = ""
            lastUrl = ""
            return
        }

        if (s.wifiPayload != lastWifiPayload || s.url != lastUrl) {
            wifiQr = makeQr(s.wifiPayload)
            urlQr = makeQr(s.url)
            lastWifiPayload = s.wifiPayload
            lastUrl = s.url
            showQr(toggleGroup.checkedButtonId != R.id.btnTabUrl)
        }

        tvInfo.text = "📶 اسم الشبكة: ${s.ssid}\n" +
                "🔑 كلمة السر: ${s.pass}\n" +
                "🌐 الرابط: ${s.url}"
        tvShared.text = "ملفات جاهزة للتحميل من الأيباد: ${FileStore.shared.size}"
        tvReceived.text = if (s.receivedLog.isEmpty()) defaultReceivedText
        else "وصل من الأيباد (محفوظ في Download/AirDrop):\n" + s.receivedLog.joinToString("\n")

        val pm = getSystemService(Context.POWER_SERVICE) as PowerManager
        btnBattery.visibility =
            if (pm.isIgnoringBatteryOptimizations(packageName)) View.GONE else View.VISIBLE
    }

    private fun createBatteryButton(): MaterialButton {
        val container = (cardInfo as ViewGroup).getChildAt(0) as LinearLayout
        val btn = MaterialButton(
            this, null, com.google.android.material.R.attr.materialButtonOutlinedStyle
        ).apply {
            text = "السماح بالعمل في الخلفية (البطارية)"
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
            ).apply { topMargin = (10 * resources.displayMetrics.density).toInt() }
            setOnClickListener {
                try {
                    startActivity(
                        Intent(
                            Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                            Uri.parse("package:$packageName")
                        )
                    )
                } catch (e: Exception) {
                    startActivity(Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS))
                }
            }
        }
        container.addView(btn)
        return btn
    }

    // ───────── Permissions ─────────

    private fun checkPermissions() {
        val permissions = mutableListOf(Manifest.permission.ACCESS_FINE_LOCATION)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.NEARBY_WIFI_DEVICES)
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        val missing = permissions.filter {
            checkSelfPermission(it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missing.toTypedArray(), 101)
        }
    }

    // ───────── QR ─────────

    private fun makeQr(content: String, size: Int = 720): Bitmap {
        val hints = mapOf<EncodeHintType, Any>(
            EncodeHintType.MARGIN to 1,
            EncodeHintType.CHARACTER_SET to "UTF-8"
        )
        val matrix = QRCodeWriter().encode(content, BarcodeFormat.QR_CODE, size, size, hints)
        val pixels = IntArray(size * size)
        for (y in 0 until size) {
            for (x in 0 until size) {
                pixels[y * size + x] = if (matrix.get(x, y)) Color.BLACK else Color.WHITE
            }
        }
        val bmp = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        bmp.setPixels(pixels, 0, size, 0, 0, size, size)
        return bmp
    }

    private fun showQr(wifi: Boolean) {
        if (wifi) {
            ivQr.setImageBitmap(wifiQr)
            tvQrHint.text = "١) افتح كاميرا الأيباد وامسح الكود وانضم للشبكة\n(لو ظهر \"لا يوجد إنترنت\" كمّل الاتصال عادي)"
        } else {
            ivQr.setImageBitmap(urlQr)
            tvQrHint.text = "٢) بعد الاتصال بالشبكة امسح الكود ده عشان تفتح صفحة نقل الملفات في Safari"
        }
    }

    // ───────── Files ─────────

    private fun addShared(uris: List<Uri>) {
        for (uri in uris) {
            var name = "file"
            var size = -1L
            contentResolver.query(uri, null, null, null, null)?.use { c ->
                if (c.moveToFirst()) {
                    val ni = c.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                    val si = c.getColumnIndex(OpenableColumns.SIZE)
                    if (ni >= 0) name = c.getString(ni) ?: name
                    if (si >= 0 && !c.isNull(si)) size = c.getLong(si)
                }
            }
            val mime = contentResolver.getType(uri) ?: "application/octet-stream"
            try {
                contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION)
            } catch (_: Exception) {
            }
            FileStore.add(name, size, mime, uri)
        }
        tvShared.text = "ملفات جاهزة للتحميل من الأيباد: ${FileStore.shared.size}"
    }

    private fun copy(label: String, value: String) {
        val cm = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        cm.setPrimaryClip(ClipData.newPlainText(label, value))
        Toast.makeText(this, "تم النسخ", Toast.LENGTH_SHORT).show()
    }
}
'''

for path, content in files.items():
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

print("✅ تم تحديث المشروع (%d ملف)" % len(files))

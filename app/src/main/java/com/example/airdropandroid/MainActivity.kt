package com.example.airdropandroid

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.wifi.WifiManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import fi.iki.elonen.NanoHTTPD
import java.io.IOException
import java.net.Inet4Address
import java.net.NetworkInterface

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView
    private lateinit var infoText: TextView
    private lateinit var btnStart: Button
    private var webServer: LocalServer? = null
    private var hotspotReservation: WifiManager.LocalOnlyHotspotReservation? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(60, 60, 60, 60)
        }

        statusText = TextView(this).apply {
            text = "الحالة: متوقف"
            textSize = 20f
        }
        infoText = TextView(this).apply {
            text = "اضغط على الزر لإنشاء شبكة الواي فاي المحلية للسيرفر.\n(لازم تكون خدمة الموقع GPS شغالة)"
            textSize = 16f
            setPadding(0, 30, 0, 30)
        }
        btnStart = Button(this).apply {
            text = "تشغيل الشبكة والسيرفر"
        }

        layout.addView(statusText)
        layout.addView(infoText)
        layout.addView(btnStart)
        setContentView(layout)

        checkPermissions()

        btnStart.setOnClickListener {
            startHotspotAndServer()
        }
    }

    private fun checkPermissions() {
        val permissions = mutableListOf(Manifest.permission.ACCESS_FINE_LOCATION)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.NEARBY_WIFI_DEVICES)
        }
        val missing = permissions.filter {
            checkSelfPermission(it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missing.toTypedArray(), 101)
        }
    }

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

    // عنوان الـ IP الحقيقي للهوتسبوت مش دايماً 192.168.43.1
    private fun getLocalIps(): List<String> {
        val result = mutableListOf<String>()
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces() ?: return result
            for (ni in interfaces) {
                if (!ni.isUp || ni.isLoopback) continue
                for (addr in ni.inetAddresses) {
                    if (addr is Inet4Address && !addr.isLoopbackAddress) {
                        addr.hostAddress?.let { result.add(it) }
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return result
    }

    private fun startHotspotAndServer() {
        val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager

        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            statusText.text = "الحالة: يرجى منح إذن الموقع أولاً"
            checkPermissions()
            return
        }

        try {
            wifiManager.startLocalOnlyHotspot(object : WifiManager.LocalOnlyHotspotCallback() {
                override fun onStarted(reservation: WifiManager.LocalOnlyHotspotReservation?) {
                    super.onStarted(reservation)
                    hotspotReservation = reservation
                    val (ssid, password) = readCredentials(reservation)

                    startWebServer()

                    val ips = getLocalIps().joinToString("\n") { "http://$it:8080" }

                    statusText.text = "الحالة: شغال بنجاح! 🚀"
                    infoText.text = "قم بالتوصيل من الأيباد:\n" +
                            "اسم الشبكة: $ssid\n" +
                            "كلمة السر: $password\n\n" +
                            "افتح Safari واكتب أحد العناوين:\n$ips"
                }

                override fun onFailed(reason: Int) {
                    super.onFailed(reason)
                    statusText.text = "فشل تشغيل الشبكة: $reason"
                }
            }, null)
        } catch (e: SecurityException) {
            statusText.text = "الحالة: الإذن مرفوض - فعّل الموقع وامنح الأذونات"
        }
    }

    private fun startWebServer() {
        try {
            if (webServer == null) {
                webServer = LocalServer(8080)
                webServer?.start()
            }
        } catch (e: IOException) {
            e.printStackTrace()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        webServer?.stop()
        hotspotReservation?.close()
    }

    class LocalServer(port: Int) : NanoHTTPD(port) {
        override fun serve(session: IHTTPSession?): Response {
            val html = """
                <!DOCTYPE html>
                <html lang="ar" dir="rtl">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>AirDrop Android</title>
                    <style>
                        body { font-family: -apple-system, sans-serif; text-align: center; padding: 40px; background: #f2f2f7; }
                        .card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); display: inline-block; max-width: 90%; }
                        h1 { color: #007aff; margin-bottom: 10px; }
                        p { font-size: 18px; color: #333; }
                    </style>
                </head>
                <body>
                    <div class="card">
                        <h1>🚀 تم الاتصال بنجاح!</h1>
                        <p>مرحباً بك في صفحة نقل الملفات السريعة بين الأندرويد والأيباد.</p>
                        <p>جاهز لنقل الملفات بدون إنترنت وبأقصى سرعة.</p>
                    </div>
                </body>
                </html>
            """.trimIndent()
            return newFixedLengthResponse(Response.Status.OK, "text/html; charset=utf-8", html)
        }
    }
}

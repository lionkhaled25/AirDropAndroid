package com.example.airdropandroid

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.wifi.WifiManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import fi.iki.elonen.NanoHTTPD
import java.io.IOException

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView
    private lateinit var infoText: TextView
    private lateinit var btnStart: Button
    private var webServer: LocalServer? = null
    private var hotspotReservation: WifiManager.LocalOnlyHotspotReservation? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = android.widget.LinearLayout(this).apply {
            orientation = android.widget.LinearLayout.VERTICAL
            setPadding(60, 60, 60, 60)
        }

        statusText = TextView(this).apply {
            text = "الحالة: متوقف"
            textSize = 20f
        }
        infoText = TextView(this).apply {
            text = "اضغط على الزر لإنشاء شبكة الواي فاي المحلية للسيرفر."
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
        val missing = permissions.filter { checkSelfPermission(it) != PackageManager.PERMISSION_GRANTED }
        if (missing.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missing.toTypedArray(), 101)
        }
    }

    private fun startHotspotAndServer() {
        val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager

        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            statusText.text = "الحالة: يرجى منح إذن الموقع أولاً"
            return
        }

        wifiManager.startLocalOnlyHotspot(object : WifiManager.LocalOnlyHotspotCallback() {
            override fun onStarted(reservation: WifiManager.LocalOnlyHotspotReservation?) {
                super.onStarted(reservation)
                hotspotReservation = reservation
                val ssid = reservation?.wifiConfiguration?.SSID ?: "Unknown"
                val password = reservation?.wifiConfiguration?.preSharedKey ?: "Unknown"

                startWebServer()

                statusText.text = "الحالة: شغال بنجاح! 🚀"
                infoText.text = """
                    قم بالتوصيل من الأيباد:
                    اسم الشبكة: $ssid
                    كلمة السر: $password
                    
                    افتح Safari واكتب العنوان:
                    http://192.168.43.1:8080
                """.trimIndent()
            }

            override fun onFailed(reason: Int) {
                super.onFailed(reason)
                statusText.text = "فشل تشغيل الشبكة: $reason"
            }
        }, null)
    }

    private fun startWebServer() {
        try {
            webServer = LocalServer(8080)
            webServer?.start()
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
        override fun serve(session: NanoHTTPD.IHTTPSession?): NanoHTTPD.Response {
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
            return newFixedLengthResponse(NanoHTTPD.Response.Status.OK, "text/html; charset=utf-8", html)
        }
    }
}
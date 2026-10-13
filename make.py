import os

files = {}

files["build.gradle"] = """buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.2.2'
        classpath 'org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.22'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
"""

files["settings.gradle"] = """rootProject.name = "AirDropAndroid"
include ':app'
"""

# FIX: هذا الملف كان ناقص - من غيره يفشل البناء بسبب AndroidX
files["gradle.properties"] = """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
"""

files["app/build.gradle"] = """plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.example.airdropandroid'
    compileSdk 34

    defaultConfig {
        applicationId "com.example.airdropandroid"
        minSdk 26
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = '17'
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'org.nanohttpd:nanohttpd:2.3.1'
}
"""

# FIX: الـ namespace كان غلط (manifest/android بدل apk/res/android)
files["app/src/main/AndroidManifest.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <uses-permission android:name="android.permission.CHANGE_WIFI_STATE" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission
        android:name="android.permission.NEARBY_WIFI_DEVICES"
        android:usesPermissionFlags="neverForLocation" />

    <application
        android:allowBackup="true"
        android:label="AirDrop Local"
        android:supportsRtl="true"
        android:theme="@style/Theme.MaterialComponents.DayNight.DarkActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
"""

files["app/src/main/java/com/example/airdropandroid/MainActivity.kt"] = r'''package com.example.airdropandroid

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
'''

# FIX: المشروع مفيهوش gradle wrapper، فنحدد نسخة Gradle متوافقة مع AGP 8.2.2
files[".github/workflows/build.yml"] = """name: Build Android APK

on:
  push:
    branches: [ "main", "master" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4

    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'

    - name: Setup Gradle 8.5
      uses: gradle/actions/setup-gradle@v4
      with:
        gradle-version: '8.5'

    - name: Build Debug APK
      run: gradle assembleDebug --stacktrace

    - name: Upload APK Artifact
      uses: actions/upload-artifact@v4
      with:
        name: AirDrop-Android-APK
        path: app/build/outputs/apk/debug/app-debug.apk
"""

for path, content in files.items():
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

print("✅ تم تعديل الكود بنجاح!")

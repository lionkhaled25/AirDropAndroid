# شغّل السكريبت ده مرة واحدة من أول فولدر الـ repo - بيعمل المشروع كامل (آخر نسخة بتشتغل في الخلفية)
import os

files = {}

# ───────────────────────── Gradle ─────────────────────────

files["build.gradle"] = r"""buildscript {
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

files["settings.gradle"] = r"""rootProject.name = "AirDropAndroid"
include ':app'
"""

files["gradle.properties"] = r"""org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
"""

files[".gitignore"] = r"""build/
.gradle/
local.properties
*.iml
.idea/
"""

files["app/build.gradle"] = r"""plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.example.airdropandroid'
    compileSdk 34

    defaultConfig {
        applicationId "com.example.airdropandroid"
        minSdk 29
        targetSdk 34
        versionCode 2
        versionName "2.0"
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
    implementation 'com.google.zxing:core:3.5.2'
}
"""

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
    </application>

</manifest>
"""

# ───────────────────────── Resources: colors / theme ─────────────────────────

files["app/src/main/res/values/colors.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="primary">#0A84FF</color>
    <color name="primary_dark">#5E5CE6</color>
    <color name="bg_top">#0B1020</color>
    <color name="bg_bottom">#1B2A4A</color>
    <color name="card">#1B2236</color>
    <color name="text_secondary">#9AA7BD</color>
    <color name="ok">#30D158</color>
    <color name="white">#FFFFFF</color>
</resources>
"""

files["app/src/main/res/values/themes.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.AirDrop" parent="Theme.MaterialComponents.NoActionBar">
        <item name="colorPrimary">@color/primary</item>
        <item name="colorPrimaryVariant">@color/primary_dark</item>
        <item name="colorOnPrimary">@color/white</item>
        <item name="colorSurface">@color/card</item>
        <item name="android:statusBarColor">@color/bg_top</item>
        <item name="android:navigationBarColor">@color/bg_bottom</item>
        <item name="android:windowBackground">@drawable/bg_gradient</item>
    </style>
</resources>
"""

files["app/src/main/res/drawable/bg_gradient.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient
        android:angle="270"
        android:startColor="@color/bg_top"
        android:endColor="@color/bg_bottom" />
</shape>
"""

# ───────────────────────── Logo / launcher icon ─────────────────────────

files["app/src/main/res/drawable/ic_launcher_background.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient
        android:angle="45"
        android:startColor="#0A84FF"
        android:endColor="#5E5CE6" />
</shape>
"""

files["app/src/main/res/drawable/ic_launcher_foreground.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <group
        android:scaleX="1.9"
        android:scaleY="1.9"
        android:translateX="31.2"
        android:translateY="31.2">
        <path
            android:fillColor="#FFFFFF"
            android:pathData="M2.01,21L23,12 2.01,3 2,10l15,2 -15,2z" />
    </group>
</vector>
"""

files["app/src/main/res/drawable/ic_logo.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="64dp"
    android:height="64dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#0A84FF"
        android:pathData="M54,4 A50,50 0 1,1 54,104 A50,50 0 1,1 54,4 Z" />
    <group
        android:scaleX="1.9"
        android:scaleY="1.9"
        android:translateX="31.2"
        android:translateY="31.2">
        <path
            android:fillColor="#FFFFFF"
            android:pathData="M2.01,21L23,12 2.01,3 2,10l15,2 -15,2z" />
    </group>
</vector>
"""

files["app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
    <monochrome android:drawable="@drawable/ic_launcher_foreground" />
</adaptive-icon>
"""

files["app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
    <monochrome android:drawable="@drawable/ic_launcher_foreground" />
</adaptive-icon>
"""

# ───────────────────────── App layout ─────────────────────────

files["app/src/main/res/layout/activity_main.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:fillViewport="true"
    android:fitsSystemWindows="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="20dp">

        <!-- Header -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:gravity="center_vertical"
            android:orientation="horizontal">

            <ImageView
                android:layout_width="64dp"
                android:layout_height="64dp"
                android:contentDescription="logo"
                android:src="@drawable/ic_logo" />

            <LinearLayout
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_marginStart="14dp"
                android:layout_weight="1"
                android:orientation="vertical">

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="AirDrop Local"
                    android:textColor="@color/white"
                    android:textSize="26sp"
                    android:textStyle="bold" />

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="نقل الملفات بين الأندرويد والأيباد بدون إنترنت"
                    android:textColor="@color/text_secondary"
                    android:textSize="13sp" />
            </LinearLayout>
        </LinearLayout>

        <!-- Status -->
        <com.google.android.material.card.MaterialCardView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="22dp"
            app:cardBackgroundColor="@color/card"
            app:cardCornerRadius="22dp"
            app:cardElevation="0dp"
            app:strokeWidth="0dp">

            <TextView
                android:id="@+id/tvStatus"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:padding="18dp"
                android:text="⚪ الحالة: متوقف"
                android:textColor="@color/white"
                android:textSize="17sp"
                android:textStyle="bold" />
        </com.google.android.material.card.MaterialCardView>

        <com.google.android.material.button.MaterialButton
            android:id="@+id/btnStart"
            android:layout_width="match_parent"
            android:layout_height="60dp"
            android:layout_marginTop="14dp"
            android:text="تشغيل الشبكة والسيرفر"
            android:textSize="17sp"
            app:cornerRadius="18dp" />

        <!-- QR card -->
        <com.google.android.material.card.MaterialCardView
            android:id="@+id/cardQr"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="16dp"
            android:visibility="gone"
            app:cardBackgroundColor="@color/card"
            app:cardCornerRadius="22dp"
            app:cardElevation="0dp"
            app:strokeWidth="0dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:gravity="center_horizontal"
                android:orientation="vertical"
                android:padding="16dp">

                <com.google.android.material.button.MaterialButtonToggleGroup
                    android:id="@+id/toggleGroup"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    app:checkedButton="@+id/btnTabWifi"
                    app:selectionRequired="true"
                    app:singleSelection="true">

                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/btnTabWifi"
                        style="?attr/materialButtonOutlinedStyle"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="١) الشبكة" />

                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/btnTabUrl"
                        style="?attr/materialButtonOutlinedStyle"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:text="٢) فتح الرابط" />
                </com.google.android.material.button.MaterialButtonToggleGroup>

                <com.google.android.material.card.MaterialCardView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="16dp"
                    app:cardBackgroundColor="@color/white"
                    app:cardCornerRadius="16dp"
                    app:cardElevation="0dp"
                    app:strokeWidth="0dp">

                    <ImageView
                        android:id="@+id/ivQr"
                        android:layout_width="250dp"
                        android:layout_height="250dp"
                        android:layout_margin="12dp"
                        android:contentDescription="QR"
                        android:scaleType="fitCenter" />
                </com.google.android.material.card.MaterialCardView>

                <TextView
                    android:id="@+id/tvQrHint"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="14dp"
                    android:gravity="center"
                    android:textColor="@color/text_secondary"
                    android:textSize="14sp" />
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- Info card -->
        <com.google.android.material.card.MaterialCardView
            android:id="@+id/cardInfo"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="16dp"
            android:visibility="gone"
            app:cardBackgroundColor="@color/card"
            app:cardCornerRadius="22dp"
            app:cardElevation="0dp"
            app:strokeWidth="0dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="18dp">

                <TextView
                    android:id="@+id/tvInfo"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:lineSpacingExtra="4dp"
                    android:textColor="@color/white"
                    android:textIsSelectable="true"
                    android:textSize="15sp" />

                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="12dp"
                    android:orientation="horizontal">

                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/btnCopyUrl"
                        style="?attr/materialButtonOutlinedStyle"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_marginEnd="6dp"
                        android:layout_weight="1"
                        android:text="نسخ الرابط" />

                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/btnCopyPass"
                        style="?attr/materialButtonOutlinedStyle"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_marginStart="6dp"
                        android:layout_weight="1"
                        android:text="نسخ كلمة السر" />
                </LinearLayout>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- Files card -->
        <com.google.android.material.card.MaterialCardView
            android:id="@+id/cardFiles"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="16dp"
            android:layout_marginBottom="12dp"
            android:visibility="gone"
            app:cardBackgroundColor="@color/card"
            app:cardCornerRadius="22dp"
            app:cardElevation="0dp"
            app:strokeWidth="0dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="18dp">

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="📁 الملفات"
                    android:textColor="@color/white"
                    android:textSize="17sp"
                    android:textStyle="bold" />

                <com.google.android.material.button.MaterialButton
                    android:id="@+id/btnPick"
                    android:layout_width="match_parent"
                    android:layout_height="54dp"
                    android:layout_marginTop="12dp"
                    android:text="اختيار ملفات لإرسالها للأيباد"
                    app:cornerRadius="16dp" />

                <TextView
                    android:id="@+id/tvShared"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="12dp"
                    android:text="ملفات جاهزة للتحميل من الأيباد: 0"
                    android:textColor="@color/text_secondary"
                    android:textSize="14sp" />

                <TextView
                    android:id="@+id/tvReceived"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="10dp"
                    android:lineSpacingExtra="3dp"
                    android:text="الملفات المستلمة من الأيباد بتتحفظ في: Download/AirDrop"
                    android:textColor="@color/text_secondary"
                    android:textSize="14sp" />
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

    </LinearLayout>
</ScrollView>
"""

# ───────────────────────── Kotlin: FileStore ─────────────────────────

files["app/src/main/java/com/example/airdropandroid/FileStore.kt"] = r'''package com.example.airdropandroid

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
'''

# ───────────────────────── Kotlin: LocalServer ─────────────────────────

files["app/src/main/java/com/example/airdropandroid/LocalServer.kt"] = r'''package com.example.airdropandroid

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
'''

# ───────────────────────── Kotlin: MainActivity ─────────────────────────

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
import android.net.wifi.WifiManager
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.OpenableColumns
import android.view.View
import android.view.WindowManager
import android.widget.ImageView
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
import java.io.IOException
import java.net.Inet4Address
import java.net.NetworkInterface

class MainActivity : AppCompatActivity() {

    private val port = 8080

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

    private var server: LocalServer? = null
    private var reservation: WifiManager.LocalOnlyHotspotReservation? = null
    private var running = false
    private var starting = false

    private var wifiQr: Bitmap? = null
    private var urlQr: Bitmap? = null
    private var currentUrl = ""
    private var currentPass = ""
    private val receivedLog = ArrayDeque<String>()
    private val handler = Handler(Looper.getMainLooper())

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

        checkPermissions()

        btnStart.setOnClickListener {
            if (running) stopAll() else if (!starting) startHotspotAndServer()
        }
        toggleGroup.addOnButtonCheckedListener { _, checkedId, isChecked ->
            if (isChecked) showQr(checkedId == R.id.btnTabWifi)
        }
        btnPick.setOnClickListener { pickFiles.launch(arrayOf("*/*")) }
        btnCopyUrl.setOnClickListener { copy("AirDrop URL", currentUrl) }
        btnCopyPass.setOnClickListener { copy("Wi-Fi password", currentPass) }
    }

    // ───────── Permissions ─────────

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

    // ───────── Hotspot + server ─────────

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

    private fun startHotspotAndServer() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            tvStatus.text = "🔴 يرجى منح إذن الموقع أولاً"
            checkPermissions()
            return
        }
        val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager

        starting = true
        tvStatus.text = "🟡 جاري تشغيل الشبكة..."

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
                    runOnUiThread { if (running) stopAll() }
                }

                override fun onFailed(reason: Int) {
                    super.onFailed(reason)
                    starting = false
                    val msg = when (reason) {
                        ERROR_INCOMPATIBLE_MODE -> "اقفل الهوتسبوت العادي أو الـ Wi-Fi Direct وجرب تاني"
                        ERROR_TETHERING_DISALLOWED -> "الهوتسبوت ممنوع على الجهاز ده"
                        ERROR_NO_CHANNEL -> "مفيش قناة واي فاي متاحة"
                        else -> "خطأ غير معروف ($reason). تأكد إن الـ GPS شغال"
                    }
                    runOnUiThread { tvStatus.text = "🔴 فشل تشغيل الشبكة: $msg" }
                }
            }, null)
        } catch (e: SecurityException) {
            starting = false
            tvStatus.text = "🔴 الإذن مرفوض - فعّل الموقع وامنح الأذونات"
        }
    }

    private fun onHotspotReady(ssid: String, pass: String) {
        val cleanSsid = ssid.trim('"')
        val ip = findHotspotIp()
        currentUrl = "http://$ip:$port"
        currentPass = pass

        try {
            server = LocalServer(applicationContext, port) { name, size ->
                runOnUiThread { onFileReceived(name, size) }
            }.also { it.start(60000, true) }
        } catch (e: IOException) {
            starting = false
            tvStatus.text = "🔴 فشل تشغيل السيرفر: ${e.message}"
            reservation?.close()
            reservation = null
            return
        }

        val wifiPayload = "WIFI:T:WPA;S:${esc(cleanSsid)};P:${esc(pass)};;"
        wifiQr = makeQr(wifiPayload)
        urlQr = makeQr(currentUrl)

        tvInfo.text = "📶 اسم الشبكة: $cleanSsid\n" +
                "🔑 كلمة السر: $pass\n" +
                "🌐 الرابط: $currentUrl"

        cardQr.visibility = View.VISIBLE
        cardInfo.visibility = View.VISIBLE
        cardFiles.visibility = View.VISIBLE
        toggleGroup.check(R.id.btnTabWifi)
        showQr(true)

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        running = true
        starting = false
        btnStart.text = "إيقاف السيرفر"
        tvStatus.text = "🟢 شغال بنجاح"
    }

    private fun stopAll() {
        try { server?.stop() } catch (_: Exception) {}
        server = null
        try { reservation?.close() } catch (_: Exception) {}
        reservation = null
        FileStore.clear()
        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        running = false
        starting = false
        receivedLog.clear()
        cardQr.visibility = View.GONE
        cardInfo.visibility = View.GONE
        cardFiles.visibility = View.GONE
        btnStart.text = "تشغيل الشبكة والسيرفر"
        tvStatus.text = "⚪ الحالة: متوقف"
        tvShared.text = "ملفات جاهزة للتحميل من الأيباد: 0"
        tvReceived.text = "الملفات المستلمة من الأيباد بتتحفظ في: Download/AirDrop"
    }

    // ───────── QR ─────────

    private fun esc(s: String): String =
        s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace(":", "\\:").replace("\"", "\\\"")

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

    private fun onFileReceived(name: String, size: Long) {
        receivedLog.addFirst("✅ $name (${fmtSize(size)})")
        while (receivedLog.size > 5) receivedLog.removeLast()
        tvReceived.text = "وصل من الأيباد (محفوظ في Download/AirDrop):\n" + receivedLog.joinToString("\n")
    }

    private fun fmtSize(b: Long): String = when {
        b < 1024 -> "$b B"
        b < 1024 * 1024 -> String.format("%.1f KB", b / 1024.0)
        b < 1024L * 1024 * 1024 -> String.format("%.1f MB", b / 1048576.0)
        else -> String.format("%.2f GB", b / 1073741824.0)
    }

    private fun copy(label: String, value: String) {
        val cm = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        cm.setPrimaryClip(ClipData.newPlainText(label, value))
        Toast.makeText(this, "تم النسخ", Toast.LENGTH_SHORT).show()
    }

    override fun onDestroy() {
        super.onDestroy()
        try { server?.stop() } catch (_: Exception) {}
        try { reservation?.close() } catch (_: Exception) {}
    }
}
'''

# ───────────────────────── Web page served to the iPad ─────────────────────────

files["app/src/main/assets/index.html"] = r'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>AirDrop Local</title>
<style>
:root{--bg:#f2f2f7;--card:#ffffff;--text:#111827;--sub:#6b7280;--primary:#0a84ff;--ok:#30d158;--bad:#ff453a;--line:#e5e7eb}
@media (prefers-color-scheme:dark){:root{--bg:#0b1020;--card:#1b2236;--text:#f3f4f6;--sub:#9aa7bd;--line:#2a3350}}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Tahoma,sans-serif;background:var(--bg);color:var(--text);padding:20px 16px 48px}
.wrap{max-width:640px;margin:0 auto}
header{display:flex;align-items:center;gap:14px;margin-bottom:22px}
.logo{width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#0a84ff,#5e5ce6);display:flex;align-items:center;justify-content:center}
.logo svg{width:30px;height:30px;fill:#fff}
h1{font-size:24px;margin:0}
header p{margin:2px 0 0;color:var(--sub);font-size:13px}
.card{background:var(--card);border-radius:22px;padding:18px;margin-bottom:16px;box-shadow:0 4px 20px rgba(0,0,0,.06)}
.card h2{font-size:17px;margin:0 0 12px}
.drop{border:2px dashed var(--primary);border-radius:18px;padding:30px 16px;text-align:center;color:var(--primary);cursor:pointer;display:block}
.drop.over{background:rgba(10,132,255,.1)}
.drop b{display:block;font-size:17px;margin-bottom:4px}
.drop span{font-size:13px;color:var(--sub)}
input[type=file]{display:none}
.row{padding:10px 0;border-bottom:1px solid var(--line)}
.row:last-child{border-bottom:0}
.meta{display:flex;justify-content:space-between;gap:10px;font-size:14px}
.name{word-break:break-all}
.st{color:var(--sub);white-space:nowrap}
.bar{height:6px;background:var(--line);border-radius:3px;margin-top:8px;overflow:hidden}
.bar i{display:block;height:100%;width:0;background:var(--primary);transition:width .15s}
.bar i.ok{background:var(--ok)}
.bar i.bad{background:var(--bad)}
.file{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 0;border-bottom:1px solid var(--line)}
.file:last-child{border-bottom:0}
.fi{min-width:0;font-size:15px;word-break:break-all}
.fi small{display:block;color:var(--sub);margin-top:2px}
.btn{background:var(--primary);color:#fff;text-decoration:none;padding:9px 18px;border-radius:12px;font-size:14px;font-weight:600;white-space:nowrap}
.empty{color:var(--sub);text-align:center;margin:8px 0;font-size:14px}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="logo"><svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg></div>
    <div><h1>AirDrop Local</h1><p>نقل ملفات سريع بدون إنترنت</p></div>
  </header>

  <div class="card">
    <h2>⬆️ إرسال ملفات للموبايل</h2>
    <label class="drop" id="drop">
      <b>اضغط لاختيار الملفات</b>
      <span>صور، فيديوهات، مستندات... أي حجم</span>
      <input type="file" id="pick" multiple>
    </label>
    <div id="ups"></div>
  </div>

  <div class="card">
    <h2>⬇️ ملفات من الموبايل</h2>
    <div id="files"><p class="empty">جاري التحميل...</p></div>
  </div>
</div>

<script>
var queue = [], busy = false;
function $(id){ return document.getElementById(id); }
function fmt(b){
  if (b < 0) return "";
  if (b < 1024) return b + " B";
  if (b < 1048576) return (b/1024).toFixed(1) + " KB";
  if (b < 1073741824) return (b/1048576).toFixed(1) + " MB";
  return (b/1073741824).toFixed(2) + " GB";
}
function addFiles(list){
  for (var i = 0; i < list.length; i++) queue.push(list[i]);
  next();
}
function next(){
  if (busy || !queue.length) return;
  busy = true;
  send(queue.shift());
}
function send(file){
  var row = document.createElement("div");
  row.className = "row";
  row.innerHTML = '<div class="meta"><span class="name"></span><span class="st">0%</span></div><div class="bar"><i></i></div>';
  row.querySelector(".name").textContent = file.name + " (" + fmt(file.size) + ")";
  var box = $("ups");
  box.insertBefore(row, box.firstChild);
  var st = row.querySelector(".st"), bar = row.querySelector("i");

  var x = new XMLHttpRequest();
  x.open("POST", "/upload?name=" + encodeURIComponent(file.name));
  x.setRequestHeader("Content-Type", "application/octet-stream");
  x.upload.onprogress = function(e){
    if (e.lengthComputable){
      var p = Math.round(e.loaded * 100 / e.total);
      st.textContent = p + "%";
      bar.style.width = p + "%";
    }
  };
  x.onload = function(){
    if (x.status === 200){ st.textContent = "✅ تم"; bar.style.width = "100%"; bar.className = "ok"; }
    else { st.textContent = "❌ فشل"; bar.className = "bad"; }
    busy = false; next();
  };
  x.onerror = function(){ st.textContent = "❌ انقطع الاتصال"; bar.className = "bad"; busy = false; next(); };
  x.send(file);
}

$("pick").addEventListener("change", function(e){ addFiles(e.target.files); e.target.value = ""; });
var drop = $("drop");
["dragenter","dragover"].forEach(function(ev){
  drop.addEventListener(ev, function(e){ e.preventDefault(); drop.classList.add("over"); });
});
["dragleave","drop"].forEach(function(ev){
  drop.addEventListener(ev, function(e){ e.preventDefault(); drop.classList.remove("over"); });
});
drop.addEventListener("drop", function(e){ if (e.dataTransfer && e.dataTransfer.files) addFiles(e.dataTransfer.files); });

function load(){
  fetch("/api/files").then(function(r){ return r.json(); }).then(function(a){
    var box = $("files");
    if (!a.length){ box.innerHTML = '<p class="empty">مفيش ملفات متشاركة من الموبايل لسه</p>'; return; }
    box.innerHTML = "";
    a.forEach(function(f){
      var d = document.createElement("div"); d.className = "file";
      var info = document.createElement("div"); info.className = "fi";
      info.textContent = f.name;
      var s = document.createElement("small"); s.textContent = fmt(f.size);
      info.appendChild(s);
      var l = document.createElement("a"); l.className = "btn"; l.href = "/download/" + f.id; l.textContent = "تحميل";
      d.appendChild(info); d.appendChild(l);
      box.appendChild(d);
    });
  }).catch(function(){});
}
load();
setInterval(load, 3000);
</script>
</body>
</html>
'''

# ───────────────────────── GitHub Actions ─────────────────────────

files[".github/workflows/build.yml"] = r"""name: Build Android APK

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


# ───────────────────────── Workflow (يطلّع الأخطاء في Annotations) ─────────────────────────

files[".github/workflows/build.yml"] = r"""name: Build Android APK

on:
  push:
    branches: [ "main", "master" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v5

    - name: Set up JDK 17
      uses: actions/setup-java@v5
      with:
        java-version: '17'
        distribution: 'temurin'

    - name: Setup Gradle 8.5
      uses: gradle/actions/setup-gradle@v4
      with:
        gradle-version: '8.5'

    - name: Build Debug APK
      run: |
        set -o pipefail
        gradle assembleDebug --stacktrace --console=plain 2>&1 | tee build.log

    - name: Show build errors in Annotations
      if: failure()
      run: |
        msg=$(grep -E "^e: |error:|What went wrong|Execution failed|Could not|AAPT|Manifest merger|Duplicate|not found" -A2 build.log | head -30 | sed 's/%/%25/g' | awk '{printf "%s%%0A", $0}')
        echo "::error title=Gradle error::${msg}"

    - name: Upload build log
      if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: build-log
        path: build.log

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

print("✅ تم إنشاء المشروع كامل بنجاح! (%d ملف)" % len(files))

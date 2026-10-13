package com.example.airdropandroid

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

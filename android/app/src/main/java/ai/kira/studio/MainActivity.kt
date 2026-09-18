package ai.kira.studio
import android.app.*
import android.os.*
import android.content.*
import android.content.pm.PackageManager
import android.net.Uri
import android.webkit.*
import android.widget.EditText
import androidx.activity.OnBackPressedCallback
import androidx.work.*
import java.util.concurrent.TimeUnit

class MainActivity: Activity() {
 private lateinit var web:WebView
 private var chooser:ValueCallback<Array<Uri>>?=null
 private val pick=registerForActivityResult(androidx.activity.result.contract.ActivityResultContracts.GetContent()){u->chooser?.onReceiveValue(if(u==null)null else arrayOf(u));chooser=null}
 override fun onCreate(b:Bundle?){super.onCreate(b);setContentView(R.layout.activity_main);web=findViewById(R.id.web)
  if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS),9)
  web.settings.javaScriptEnabled=true;web.settings.domStorageEnabled=true;web.settings.mediaPlaybackRequiresUserGesture=false;web.settings.allowFileAccess=true
  web.webChromeClient=object:WebChromeClient(){override fun onShowFileChooser(v:WebView?,cb:ValueCallback<Array<Uri>>,p:FileChooserParams?):Boolean{chooser?.onReceiveValue(null);chooser=cb;pick.launch("application/zip");return true}}
  web.webViewClient=object:WebViewClient(){override fun shouldOverrideUrlLoading(v:WebView,r:WebResourceRequest):Boolean{val u=r.url;val h=u.host?:"";if(h.contains("google.com")||h.contains("twitch.tv")){startActivity(Intent(Intent.ACTION_VIEW,u));return true};return false}}
  val saved=getSharedPreferences("kira",0).getString("url","")?:"";if(saved.isBlank())askUrl()else{web.loadUrl(saved);scheduleHealth()}
  onBackPressedDispatcher.addCallback(this,object:OnBackPressedCallback(true){override fun handleOnBackPressed(){if(web.canGoBack())web.goBack()else finish()}})
 }
 private fun scheduleHealth(){val r=PeriodicWorkRequestBuilder<HealthWorker>(15,TimeUnit.MINUTES).build();WorkManager.getInstance(this).enqueueUniquePeriodicWork("kira-health",ExistingPeriodicWorkPolicy.UPDATE,r)}
 private fun askUrl(){val input=EditText(this);input.hint="https://server.example/studio";AlertDialog.Builder(this).setTitle("Подключить Kira Core").setMessage("Введи HTTPS-адрес сервера Киры").setView(input).setCancelable(false).setPositiveButton("Подключить"){_,_->var u=input.text.toString().trim();if(!u.endsWith("/studio"))u=u.trimEnd('/')+"/studio";getSharedPreferences("kira",0).edit().putString("url",u).apply();web.loadUrl(u);scheduleHealth()}.show()}
}

package ai.kira.studio
import android.app.*
import android.view.*
import android.graphics.Color
import android.os.*
import android.content.*
import android.content.pm.PackageManager
import android.net.Uri
import android.webkit.*
import android.widget.EditText
import android.widget.Toast
import java.io.File
import androidx.activity.OnBackPressedCallback
import androidx.work.*
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import java.util.concurrent.TimeUnit

class MainActivity:androidx.activity.ComponentActivity(){
 private lateinit var web:WebView
 private var chooser:ValueCallback<Array<Uri>>?=null
 private val pick=registerForActivityResult(androidx.activity.result.contract.ActivityResultContracts.OpenDocument()){u->chooser?.onReceiveValue(if(u==null)null else arrayOf(u));chooser=null}
 override fun onCreate(b:Bundle?){installSplashScreen();super.onCreate(b);setContentView(R.layout.activity_main);web=findViewById(R.id.web);web.setBackgroundColor(Color.rgb(10,7,16));showPreviousCrashIfAny()
  if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS),9)
  web.settings.javaScriptEnabled=true;web.settings.domStorageEnabled=true;web.settings.databaseEnabled=true;web.settings.cacheMode=WebSettings.LOAD_DEFAULT;web.settings.mediaPlaybackRequiresUserGesture=false;web.settings.allowFileAccess=false;web.settings.allowContentAccess=false;web.settings.setSupportZoom(false);web.settings.mixedContentMode=WebSettings.MIXED_CONTENT_NEVER_ALLOW;CookieManager.getInstance().setAcceptCookie(true);CookieManager.getInstance().setAcceptThirdPartyCookies(web,true);web.addJavascriptInterface(KiraBridge(this),"KiraAndroid")
  web.webChromeClient=object:WebChromeClient(){override fun onShowFileChooser(v:WebView?,cb:ValueCallback<Array<Uri>>,p:FileChooserParams?):Boolean{chooser?.onReceiveValue(null);chooser=cb;pick.launch(arrayOf("application/zip","application/octet-stream","application/x-zip-compressed"));return true}}
  web.webViewClient=object:WebViewClient(){override fun shouldOverrideUrlLoading(v:WebView,r:WebResourceRequest):Boolean{val u=r.url;val h=u.host?:"";if(h.endsWith("google.com")||h.endsWith("accounts.google.com")||h.endsWith("twitch.tv")||h.endsWith("youtube.com")){runCatching{startActivity(Intent(Intent.ACTION_VIEW,u))};return true};return false};override fun onReceivedError(v:WebView,r:WebResourceRequest,e:WebResourceError){if(r.isForMainFrame)toast("Kira Core недоступен: "+e.description)};override fun onReceivedSslError(v:WebView?,handler:SslErrorHandler?,error:android.net.http.SslError?){handler?.cancel();toast("HTTPS сертификат Kira Core отклонён")}}
  val saved=prefs().getString("url","")?:"";if(saved.isBlank())askUrl()else{web.loadUrl(saved);scheduleHealth()}
  web.setDownloadListener{url,_,_,_,_->runCatching{startActivity(Intent(Intent.ACTION_VIEW,Uri.parse(url)))}.onFailure{toast("Не удалось открыть загрузку")}}
  onBackPressedDispatcher.addCallback(this,object:OnBackPressedCallback(true){override fun handleOnBackPressed(){if(web.canGoBack())web.goBack()else finish()}})
 }
 private fun showPreviousCrashIfAny(){val f=File(filesDir,"last_crash.txt");if(!f.exists())return;val msg=runCatching{f.readText().take(6000)}.getOrDefault("Не удалось прочитать crash log");f.delete();AlertDialog.Builder(this).setTitle("Kira Studio восстановлена после сбоя").setMessage(msg).setPositiveButton("Продолжить",null).setNeutralButton("Копировать"){_,_->val cm=getSystemService(CLIPBOARD_SERVICE) as android.content.ClipboardManager;cm.setPrimaryClip(android.content.ClipData.newPlainText("Kira crash",msg));toast("Crash log скопирован")}.show()}
 private fun prefs()=getSharedPreferences("kira",0)
 private fun scheduleHealth(){val r=PeriodicWorkRequestBuilder<HealthWorker>(15,TimeUnit.MINUTES).build();WorkManager.getInstance(this).enqueueUniquePeriodicWork("kira-health",ExistingPeriodicWorkPolicy.UPDATE,r)}
 override fun onDestroy(){chooser?.onReceiveValue(null);chooser=null;web.stopLoading();web.removeJavascriptInterface("KiraAndroid");web.webChromeClient=null;web.webViewClient=WebViewClient();web.destroy();super.onDestroy()}
 fun reloadStudio(){web.reload()}
 fun openServerDialog(){askUrl()}
 private fun askUrl(){
  val view=layoutInflater.inflate(R.layout.dialog_server,null)
  val input=view.findViewById<EditText>(R.id.serverUrl)
  input.setText(prefs().getString("url","")?.substringBefore("/studio")?:"")
  val dialog=AlertDialog.Builder(this).setView(view).setCancelable(false).setPositiveButton("Подключить",null).setNegativeButton("Закрыть"){_,_->finish()}.create()
  dialog.setOnShowListener{
   dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener{
    var u=input.text.toString().trim()
    if(u.isBlank()){input.error="Введи адрес Kira Core";return@setOnClickListener}
    if(!u.startsWith("https://")){input.error="Нужен HTTPS-адрес";return@setOnClickListener}
    u=u.trimEnd('/')+"/studio";prefs().edit().putString("url",u).apply();web.loadUrl(u);scheduleHealth();dialog.dismiss()
   }
  }
  dialog.show()
 }
 private fun toast(s:String)=android.widget.Toast.makeText(this,s,android.widget.Toast.LENGTH_LONG).show()
}

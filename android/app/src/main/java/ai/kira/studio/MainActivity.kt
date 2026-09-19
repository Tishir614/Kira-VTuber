package ai.kira.studio
import android.app.*
import android.graphics.Color
import android.os.*
import android.content.*
import android.content.pm.PackageManager
import android.media.projection.MediaProjectionManager
import android.app.Activity
import android.net.Uri
import android.webkit.*
import android.widget.EditText
import java.io.File
import androidx.activity.OnBackPressedCallback
import androidx.work.*
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import java.util.concurrent.TimeUnit

class MainActivity:androidx.activity.ComponentActivity(){
 private lateinit var web:WebView
 private var chooser:ValueCallback<Array<Uri>>?=null
 private val capture=registerForActivityResult(androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult()){r->if(r.resultCode==Activity.RESULT_OK&&r.data!=null){val i=Intent(this,BroadcastService::class.java).setAction(BroadcastService.START).putExtra(BroadcastService.EXTRA_RESULT_CODE,r.resultCode).putExtra(BroadcastService.EXTRA_DATA,r.data);androidx.core.content.ContextCompat.startForegroundService(this,i)}else toast("Захват экрана отменён")}
 private val pick=registerForActivityResult(androidx.activity.result.contract.ActivityResultContracts.OpenDocument()){u->chooser?.onReceiveValue(if(u==null)null else arrayOf(u));chooser=null}
 override fun onCreate(b:Bundle?){
  installSplashScreen();super.onCreate(b);setContentView(R.layout.activity_main)
  web=findViewById(R.id.web);web.setBackgroundColor(Color.rgb(10,7,16));showPreviousCrashIfAny()
  if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS),9)
  with(web.settings){javaScriptEnabled=true;domStorageEnabled=true;databaseEnabled=true;cacheMode=WebSettings.LOAD_DEFAULT;mediaPlaybackRequiresUserGesture=false;allowFileAccess=false;allowContentAccess=false;setSupportZoom(false);mixedContentMode=WebSettings.MIXED_CONTENT_NEVER_ALLOW;userAgentString=userAgentString+" KiraStudioAndroid/1.4.0"}
  CookieManager.getInstance().setAcceptCookie(true);CookieManager.getInstance().setAcceptThirdPartyCookies(web,true)
  web.addJavascriptInterface(KiraBridge(this),"KiraAndroid")
  web.webChromeClient=object:WebChromeClient(){override fun onShowFileChooser(v:WebView?,cb:ValueCallback<Array<Uri>>,p:FileChooserParams?):Boolean{chooser?.onReceiveValue(null);chooser=cb;pick.launch(arrayOf("application/zip","application/octet-stream","application/x-zip-compressed"));return true}}
  web.webViewClient=object:WebViewClient(){
   override fun shouldOverrideUrlLoading(v:WebView,r:WebResourceRequest):Boolean{val u=r.url;val h=u.host?:"";if(h.endsWith("google.com")||h.endsWith("twitch.tv")||h.endsWith("youtube.com")){runCatching{startActivity(Intent(Intent.ACTION_VIEW,u))};return true};return false}
   override fun onReceivedError(v:WebView,r:WebResourceRequest,e:WebResourceError){if(r.isForMainFrame)toast("Kira Core недоступен: "+e.description)}
   override fun onReceivedSslError(v:WebView?,h:SslErrorHandler?,e:android.net.http.SslError?){h?.cancel();toast("HTTPS сертификат Kira Core отклонён")}
  }
  val saved=prefs().getString("url","")?:"";if(saved.isBlank())askUrl()else{loadStudio(saved);scheduleHealth()}
  web.setDownloadListener{url,_,_,_,_->runCatching{startActivity(Intent(Intent.ACTION_VIEW,Uri.parse(url)))}.onFailure{toast("Не удалось открыть загрузку")}}
  onBackPressedDispatcher.addCallback(this,object:OnBackPressedCallback(true){override fun handleOnBackPressed(){if(web.canGoBack())web.goBack()else finish()}})
 }
 private fun normalize(raw:String):String{val base=raw.trim().trimEnd('/').removeSuffix("/studio");return "$base/studio"}
 private fun loadStudio(raw:String){web.loadUrl(normalize(raw))}
 private fun showPreviousCrashIfAny(){val f=File(filesDir,"last_crash.txt");if(!f.exists())return;val msg=runCatching{f.readText().take(6000)}.getOrDefault("Не удалось прочитать crash log");f.delete();AlertDialog.Builder(this).setTitle("Kira Studio восстановлена после сбоя").setMessage(msg).setPositiveButton("Продолжить",null).setNeutralButton("Копировать"){_,_->val cm=getSystemService(CLIPBOARD_SERVICE) as android.content.ClipboardManager;cm.setPrimaryClip(android.content.ClipData.newPlainText("Kira crash",msg));toast("Crash log скопирован")}.show()}
 private fun prefs()=getSharedPreferences("kira",0)
 private fun scheduleHealth(){val r=PeriodicWorkRequestBuilder<HealthWorker>(15,TimeUnit.MINUTES).build();WorkManager.getInstance(this).enqueueUniquePeriodicWork("kira-health",ExistingPeriodicWorkPolicy.UPDATE,r)}
 override fun onDestroy(){chooser?.onReceiveValue(null);chooser=null;if(::web.isInitialized){web.stopLoading();web.removeJavascriptInterface("KiraAndroid");web.webChromeClient=null;web.webViewClient=WebViewClient();web.destroy()};super.onDestroy()}
 fun reloadStudio(){loadStudio(prefs().getString("url","")?:"")}
 fun requestBroadcast(){val m=getSystemService(MediaProjectionManager::class.java);capture.launch(m.createScreenCaptureIntent())}
 fun stopBroadcast(){startService(Intent(this,BroadcastService::class.java).setAction(BroadcastService.STOP))}
 fun openServerDialog(){askUrl()}
 private fun askUrl(){
  val view=layoutInflater.inflate(R.layout.dialog_server,null);val input=view.findViewById<EditText>(R.id.serverUrl)
  input.setText((prefs().getString("url","")?:"").removeSuffix("/studio"))
  val dialog=AlertDialog.Builder(this).setView(view).setCancelable(false).setPositiveButton("Подключить",null).setNegativeButton("Закрыть"){_,_->finish()}.create()
  dialog.setOnShowListener{dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener{var u=input.text.toString().trim();if(u.isBlank()){input.error="Введи адрес Kira Core";return@setOnClickListener};if(!u.startsWith("https://")){input.error="Нужен HTTPS-адрес";return@setOnClickListener};u=normalize(u);prefs().edit().putString("url",u).apply();loadStudio(u);scheduleHealth();dialog.dismiss()}}
  dialog.show()
 }
 private fun toast(s:String)=android.widget.Toast.makeText(this,s,android.widget.Toast.LENGTH_LONG).show()
}

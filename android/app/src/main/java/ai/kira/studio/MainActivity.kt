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
import androidx.activity.OnBackPressedCallback
import androidx.work.*
import java.util.concurrent.TimeUnit

class MainActivity:Activity(){
 private lateinit var web:WebView
 private var chooser:ValueCallback<Array<Uri>>?=null
 private val pick=registerForActivityResult(androidx.activity.result.contract.ActivityResultContracts.GetContent()){u->chooser?.onReceiveValue(if(u==null)null else arrayOf(u));chooser=null}
 override fun onCreate(b:Bundle?){super.onCreate(b);setContentView(R.layout.activity_main);web=findViewById(R.id.web);web.setBackgroundColor(Color.rgb(10,7,16))
  if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS),9)
  web.settings.javaScriptEnabled=true;web.settings.domStorageEnabled=true;web.settings.mediaPlaybackRequiresUserGesture=false;web.settings.allowFileAccess=true;web.addJavascriptInterface(KiraBridge(this),"KiraAndroid")
  web.webChromeClient=object:WebChromeClient(){override fun onShowFileChooser(v:WebView?,cb:ValueCallback<Array<Uri>>,p:FileChooserParams?):Boolean{chooser?.onReceiveValue(null);chooser=cb;pick.launch("application/zip");return true}}
  web.webViewClient=object:WebViewClient(){override fun shouldOverrideUrlLoading(v:WebView,r:WebResourceRequest):Boolean{val u=r.url;val h=u.host?:"";if(h.contains("google.com")||h.contains("twitch.tv")){startActivity(Intent(Intent.ACTION_VIEW,u));return true};return false}}
  val saved=prefs().getString("url","")?:"";if(saved.isBlank())askUrl()else{web.loadUrl(saved);scheduleHealth()}
  onBackPressedDispatcher.addCallback(this,object:OnBackPressedCallback(true){override fun handleOnBackPressed(){if(web.canGoBack())web.goBack()else finish()}})
 }
 private fun prefs()=getSharedPreferences("kira",0)
 private fun scheduleHealth(){val r=PeriodicWorkRequestBuilder<HealthWorker>(15,TimeUnit.MINUTES).build();WorkManager.getInstance(this).enqueueUniquePeriodicWork("kira-health",ExistingPeriodicWorkPolicy.UPDATE,r)}
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

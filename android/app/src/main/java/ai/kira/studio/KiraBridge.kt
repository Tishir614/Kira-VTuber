package ai.kira.studio
import android.content.Intent
import android.net.Uri
import android.webkit.JavascriptInterface

class KiraBridge(private val activity:MainActivity){
 @JavascriptInterface fun appVersion()="1.4.0"
 @JavascriptInterface fun platform()="android"
 @JavascriptInterface fun changeServer(){activity.runOnUiThread{activity.openServerDialog()}}
 @JavascriptInterface fun reload(){activity.runOnUiThread{activity.reloadStudio()}}
 @JavascriptInterface fun broadcastMode()="native-service"
 @JavascriptInterface fun broadcastRunning()=activity.getSharedPreferences("kira",0).getBoolean("broadcast_running",false)
 @JavascriptInterface fun startBroadcast(){activity.runOnUiThread{androidx.core.content.ContextCompat.startForegroundService(activity,Intent(activity,BroadcastService::class.java).setAction(BroadcastService.START))}}
 @JavascriptInterface fun stopBroadcast(){activity.runOnUiThread{activity.startService(Intent(activity,BroadcastService::class.java).setAction(BroadcastService.STOP))}}
 @JavascriptInterface fun openStreamlabs(){
  activity.runOnUiThread{
   val pm=activity.packageManager
   val candidates=listOf("com.streamlabs","com.streamlabs.slobs")
   val launch=candidates.firstNotNullOfOrNull{pm.getLaunchIntentForPackage(it)}
   if(launch!=null)activity.startActivity(launch)
   else activity.startActivity(Intent(Intent.ACTION_VIEW,Uri.parse("https://streamlabs.com/mobile-app")))
  }
 }
}

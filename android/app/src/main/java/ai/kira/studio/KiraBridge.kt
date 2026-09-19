package ai.kira.studio
import android.webkit.JavascriptInterface
class KiraBridge(private val activity:MainActivity){
 @JavascriptInterface fun appVersion()="1.4.0"
 @JavascriptInterface fun changeServer(){activity.runOnUiThread{activity.openServerDialog()}}
 @JavascriptInterface fun reload(){activity.runOnUiThread{activity.reloadStudio()}}
}

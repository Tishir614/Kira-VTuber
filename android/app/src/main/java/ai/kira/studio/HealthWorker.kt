package ai.kira.studio
import android.app.*
import android.content.Context
import android.os.Build
import androidx.work.*
import java.net.URL
class HealthWorker(ctx:Context,p:WorkerParameters):CoroutineWorker(ctx,p){
 override suspend fun doWork():Result{
  val base=applicationContext.getSharedPreferences("kira",0).getString("url","")?:"";if(base.isBlank())return Result.success()
  return try{val health=URL(base.substringBefore("/studio")+"/health").readText();if(!health.contains("\"ok\":true")&&!health.contains("\"ok\": true"))notify("Kira Core недоступен","Проверь сервер Киры.");Result.success()}catch(e:Exception){notify("Kira Core не отвечает","Android не смог связаться с сервером Киры.");Result.retry()}
 }
 private fun notify(t:String,b:String){if(Build.VERSION.SDK_INT>=33&&applicationContext.checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=android.content.pm.PackageManager.PERMISSION_GRANTED)return;val nm=applicationContext.getSystemService(NotificationManager::class.java);val id="kira_status";if(Build.VERSION.SDK_INT>=26)nm.createNotificationChannel(NotificationChannel(id,"Kira status",NotificationManager.IMPORTANCE_DEFAULT));val n=if(Build.VERSION.SDK_INT>=26)Notification.Builder(applicationContext,id) else Notification.Builder(applicationContext);nm.notify(7,n.setSmallIcon(android.R.drawable.stat_notify_error).setContentTitle(t).setContentText(b).build())}
}

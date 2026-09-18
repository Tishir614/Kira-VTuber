package ai.kira.studio
import android.app.*
import android.content.Context
import androidx.work.*
import java.net.URL
class HealthWorker(ctx:Context,p:WorkerParameters):CoroutineWorker(ctx,p){
 override suspend fun doWork():Result{
  val base=applicationContext.getSharedPreferences("kira",0).getString("url","")?:"";if(base.isBlank())return Result.success()
  return try{val health=URL(base.substringBefore("/studio")+"/health").readText();if(!health.contains("\"ok\":true")&&!health.contains("\"ok\": true"))notify("Kira Core недоступен","Проверь сервер Киры.");Result.success()}catch(e:Exception){notify("Kira Core не отвечает","Android не смог связаться с сервером Киры.");Result.retry()}
 }
 private fun notify(t:String,b:String){val nm=applicationContext.getSystemService(NotificationManager::class.java);val id="kira_status";nm.createNotificationChannel(NotificationChannel(id,"Kira status",NotificationManager.IMPORTANCE_DEFAULT));nm.notify(7,Notification.Builder(applicationContext,id).setSmallIcon(android.R.drawable.stat_notify_error).setContentTitle(t).setContentText(b).build())}
}

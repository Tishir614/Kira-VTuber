package ai.kira.studio
import android.app.*
import android.content.*
import android.os.*
import androidx.core.app.NotificationCompat

class BroadcastService:Service(){
 companion object{const val START="ai.kira.studio.BROADCAST_START";const val STOP="ai.kira.studio.BROADCAST_STOP";const val CHANNEL="kira_broadcast";const val ID=41}
 override fun onCreate(){super.onCreate();if(Build.VERSION.SDK_INT>=26)(getSystemService(NotificationManager::class.java)).createNotificationChannel(NotificationChannel(CHANNEL,"Kira Broadcast",NotificationManager.IMPORTANCE_LOW))}
 override fun onStartCommand(i:Intent?,flags:Int,startId:Int):Int{
  if(i?.action==STOP){stopForeground(STOP_FOREGROUND_REMOVE);stopSelf();getSharedPreferences("kira",0).edit().putBoolean("broadcast_running",false).apply();return START_NOT_STICKY}
  val open=PendingIntent.getActivity(this,0,Intent(this,MainActivity::class.java),PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
  val stop=PendingIntent.getService(this,1,Intent(this,BroadcastService::class.java).setAction(STOP),PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
  val n=NotificationCompat.Builder(this,CHANNEL).setSmallIcon(android.R.drawable.presence_video_online).setContentTitle("Kira Studio").setContentText("Мобильная студия активна").setOngoing(true).setContentIntent(open).addAction(android.R.drawable.ic_media_pause,"Остановить",stop).build()
  startForeground(ID,n);getSharedPreferences("kira",0).edit().putBoolean("broadcast_running",true).apply();return START_STICKY
 }
 override fun onBind(i:Intent?)=null
}

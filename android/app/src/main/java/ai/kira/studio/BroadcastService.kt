package ai.kira.studio
import android.app.*
import android.content.*
import android.os.*
import android.media.projection.*
import androidx.core.app.NotificationCompat
import com.pedro.common.ConnectChecker
import com.pedro.encoder.input.sources.audio.MicrophoneSource
import com.pedro.encoder.input.sources.video.NoVideoSource
import com.pedro.encoder.input.sources.video.ScreenSource
import com.pedro.library.generic.GenericStream
import java.io.File

class BroadcastService:Service(),ConnectChecker{
 companion object{const val START="ai.kira.studio.BROADCAST_START";const val STOP="ai.kira.studio.BROADCAST_STOP";const val EXTRA_RESULT_CODE="result_code";const val EXTRA_DATA="projection_data";const val CHANNEL="kira_broadcast";const val ID=41}
 private lateinit var stream:GenericStream
 private var projection:MediaProjection?=null
 override fun onCreate(){super.onCreate();if(Build.VERSION.SDK_INT>=26)getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel(CHANNEL,"Kira Broadcast",NotificationManager.IMPORTANCE_LOW));stream=GenericStream(baseContext,this,NoVideoSource(),MicrophoneSource()).apply{getGlInterface().setForceRender(true,30)}}
 override fun onStartCommand(i:Intent?,flags:Int,startId:Int):Int{
  if(i?.action==STOP){shutdown();return START_NOT_STICKY}
  startForeground(ID,note("Подготовка мобильного эфира…"))
  val data=if(Build.VERSION.SDK_INT>=33)i?.getParcelableExtra(EXTRA_DATA,Intent::class.java) else @Suppress("DEPRECATION") i?.getParcelableExtra(EXTRA_DATA)
  val code=i?.getIntExtra(EXTRA_RESULT_CODE,Activity.RESULT_CANCELED)?:Activity.RESULT_CANCELED
  if(data==null||code!=Activity.RESULT_OK){shutdown();return START_NOT_STICKY}
  val prefs=getSharedPreferences("kira",0);val base=prefs.getString("rtmp_url","")?.trim().orEmpty();val key=prefs.getString("rtmp_key","")?.trim().orEmpty()
  if(base.isBlank()||key.isBlank()){errorLog("RTMP/RTMPS адрес или Stream Key не настроен");shutdown();return START_NOT_STICKY}
  return try{
   val ok=stream.prepareVideo(720,1280,3_000_000,rotation=0)&&stream.prepareAudio(44_100,true,128_000,echoCanceler=true,noiseSuppressor=true)
   if(!ok)throw IllegalStateException("Не удалось подготовить H.264/AAC encoder")
   projection=getSystemService(MediaProjectionManager::class.java).getMediaProjection(code,data)?:throw IllegalStateException("MediaProjection недоступен")
   stream.changeVideoSource(ScreenSource(applicationContext,projection!!))
   val endpoint=base.trimEnd('/')+"/"+key
   stream.startStream(endpoint);prefs.edit().putBoolean("broadcast_running",true).apply();notifyState("Подключение к трансляции…");START_STICKY
  }catch(e:Throwable){errorLog(e.stackTraceToString());shutdown();START_NOT_STICKY}
 }
 private fun note(t:String):Notification{val open=PendingIntent.getActivity(this,0,Intent(this,MainActivity::class.java),PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT);val stop=PendingIntent.getService(this,1,Intent(this,BroadcastService::class.java).setAction(STOP),PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT);return NotificationCompat.Builder(this,CHANNEL).setSmallIcon(android.R.drawable.presence_video_online).setContentTitle("Kira Studio").setContentText(t).setOngoing(true).setContentIntent(open).addAction(android.R.drawable.ic_media_pause,"Остановить",stop).build()}
 private fun notifyState(t:String){getSystemService(NotificationManager::class.java).notify(ID,note(t))}
 private fun errorLog(t:String){runCatching{File(filesDir,"broadcast_error.txt").writeText(t)}}
 private fun shutdown(){if(::stream.isInitialized){runCatching{if(stream.isStreaming)stream.stopStream()};runCatching{stream.release()}};projection?.stop();projection=null;getSharedPreferences("kira",0).edit().putBoolean("broadcast_running",false).apply();stopForeground(STOP_FOREGROUND_REMOVE);stopSelf()}
 override fun onDestroy(){if(::stream.isInitialized)runCatching{stream.release()};projection?.stop();projection=null;super.onDestroy()}
 override fun onBind(i:Intent?)=null
 override fun onConnectionStarted(url:String){notifyState("Соединение с платформой…")}
 override fun onConnectionSuccess(){notifyState("🔴 Kira LIVE • 720×1280 • H.264/AAC")}
 override fun onConnectionFailed(reason:String){errorLog(reason);notifyState("Ошибка эфира: $reason");getSharedPreferences("kira",0).edit().putBoolean("broadcast_running",false).apply()}
 override fun onNewBitrate(bitrate:Long){if(bitrate>0)notifyState("🔴 Kira LIVE • "+(bitrate/1000)+" kbps")}
 override fun onDisconnect(){notifyState("Эфир отключён");getSharedPreferences("kira",0).edit().putBoolean("broadcast_running",false).apply()}
 override fun onAuthError(){notifyState("Ошибка Stream Key");getSharedPreferences("kira",0).edit().putBoolean("broadcast_running",false).apply()}
 override fun onAuthSuccess(){notifyState("🔴 Kira LIVE • авторизация успешна")}
}

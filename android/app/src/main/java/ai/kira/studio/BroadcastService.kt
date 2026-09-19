package ai.kira.studio
import android.app.*
import android.content.*
import android.os.*
import android.media.projection.*
import android.hardware.display.DisplayManager
import android.view.Surface
import android.media.MediaCodec
import android.media.MediaFormat
import androidx.core.app.NotificationCompat

class BroadcastService:Service(){
 companion object{const val START="ai.kira.studio.BROADCAST_START";const val STOP="ai.kira.studio.BROADCAST_STOP";const val EXTRA_RESULT_CODE="result_code";const val EXTRA_DATA="projection_data";const val CHANNEL="kira_broadcast";const val ID=41}
 private var projection:MediaProjection?=null
 private var display:android.hardware.display.VirtualDisplay?=null
 private var encoder:MediaCodec?=null
 override fun onCreate(){super.onCreate();if(Build.VERSION.SDK_INT>=26)getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel(CHANNEL,"Kira Broadcast",NotificationManager.IMPORTANCE_LOW))}
 override fun onStartCommand(i:Intent?,flags:Int,startId:Int):Int{
  if(i?.action==STOP){shutdown();return START_NOT_STICKY}
  startForeground(ID,notification("Подготовка мобильного эфира…"))
  val data=if(Build.VERSION.SDK_INT>=33)i?.getParcelableExtra(EXTRA_DATA,Intent::class.java) else @Suppress("DEPRECATION") i?.getParcelableExtra(EXTRA_DATA)
  val code=i?.getIntExtra(EXTRA_RESULT_CODE,Activity.RESULT_CANCELED)?:Activity.RESULT_CANCELED
  if(data==null||code!=Activity.RESULT_OK){shutdown();return START_NOT_STICKY}
  return try{
   val width=720;val height=1280;val dpi=resources.displayMetrics.densityDpi
   val format=MediaFormat.createVideoFormat(MediaFormat.MIMETYPE_VIDEO_AVC,width,height).apply{setInteger(MediaFormat.KEY_COLOR_FORMAT,android.media.MediaCodecInfo.CodecCapabilities.COLOR_FormatSurface);setInteger(MediaFormat.KEY_BIT_RATE,3_000_000);setInteger(MediaFormat.KEY_FRAME_RATE,30);setInteger(MediaFormat.KEY_I_FRAME_INTERVAL,2)}
   encoder=MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_VIDEO_AVC).apply{configure(format,null,null,MediaCodec.CONFIGURE_FLAG_ENCODE)}
   val surface:Surface=encoder!!.createInputSurface();encoder!!.start()
   projection=getSystemService(MediaProjectionManager::class.java).getMediaProjection(code,data)
   display=projection!!.createVirtualDisplay("KiraBroadcast",width,height,dpi,DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,surface,null,null)
   getSharedPreferences("kira",0).edit().putBoolean("broadcast_running",true).apply()
   getSystemService(NotificationManager::class.java).notify(ID,notification("Экран захватывается • H.264 720×1280 30 FPS"))
   START_STICKY
  }catch(e:Throwable){File(filesDir,"broadcast_error.txt").writeText(e.stackTraceToString());shutdown();START_NOT_STICKY}
 }
 private fun notification(text:String):Notification{val open=PendingIntent.getActivity(this,0,Intent(this,MainActivity::class.java),PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT);val stop=PendingIntent.getService(this,1,Intent(this,BroadcastService::class.java).setAction(STOP),PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT);return NotificationCompat.Builder(this,CHANNEL).setSmallIcon(android.R.drawable.presence_video_online).setContentTitle("Kira Studio").setContentText(text).setOngoing(true).setContentIntent(open).addAction(android.R.drawable.ic_media_pause,"Остановить",stop).build()}
 private fun shutdown(){display?.release();display=null;projection?.stop();projection=null;runCatching{encoder?.stop()};encoder?.release();encoder=null;getSharedPreferences("kira",0).edit().putBoolean("broadcast_running",false).apply();stopForeground(STOP_FOREGROUND_REMOVE);stopSelf()}
 override fun onDestroy(){shutdown();super.onDestroy()}
 override fun onBind(i:Intent?)=null
}

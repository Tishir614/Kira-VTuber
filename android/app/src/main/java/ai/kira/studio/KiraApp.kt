package ai.kira.studio
import android.app.*
import android.content.*
import android.os.*
import java.io.*

class KiraApp:Application(){
 override fun onCreate(){
  super.onCreate()
  val previous=Thread.getDefaultUncaughtExceptionHandler()
  Thread.setDefaultUncaughtExceptionHandler{t,e->
   val report=buildString{
    append("Kira Studio crash\n")
    append("Time: ").append(System.currentTimeMillis()).append('\n')
    append("Thread: ").append(t.name).append('\n')
    append("Android: ").append(Build.VERSION.RELEASE).append(" SDK ").append(Build.VERSION.SDK_INT).append('\n')
    append("Device: ").append(Build.MANUFACTURER).append(' ').append(Build.MODEL).append("\n\n")
    append(e.stackTraceToString())
   }
   runCatching{
    File(filesDir,"last_crash.txt").writeText(report)
    getSharedPreferences("kira",0).edit().putBoolean("crash_pending",true).commit()
   }
   previous?.uncaughtException(t,e) ?: run { android.os.Process.killProcess(android.os.Process.myPid()); kotlin.system.exitProcess(10) }
  }
 }
}

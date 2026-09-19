package ai.kira.studio
import android.app.*
import android.content.*
import android.os.*
import android.widget.*
import java.io.*

class KiraApp:Application(){
 override fun onCreate(){super.onCreate()
  val previous=Thread.getDefaultUncaughtExceptionHandler()
  Thread.setDefaultUncaughtExceptionHandler{t,e->
   runCatching{File(filesDir,"last_crash.txt").writeText("Thread: ${t.name}\nAndroid: ${Build.VERSION.RELEASE} SDK ${Build.VERSION.SDK_INT}\n\n"+e.stackTraceToString())}
   previous?.uncaughtException(t,e)
  }
 }
}

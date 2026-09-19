package ai.kira.studio
import android.app.*
import android.os.*
import android.content.*
import android.graphics.Color
import android.widget.*
import androidx.activity.ComponentActivity
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen

class MainActivity:ComponentActivity(){
 override fun onCreate(state:Bundle?){
  installSplashScreen()
  super.onCreate(state)
  val root=LinearLayout(this).apply{
   orientation=LinearLayout.VERTICAL
   gravity=android.view.Gravity.CENTER
   setPadding(48,48,48,48)
   setBackgroundColor(Color.rgb(10,7,16))
  }
  val title=TextView(this).apply{
   text="Kira Studio 🦊"
   textSize=28f
   setTextColor(Color.WHITE)
   gravity=android.view.Gravity.CENTER
  }
  val info=TextView(this).apply{
   text="Безопасный режим Android запущен.\n\nWebView, WorkManager, Broadcast и Kira Core временно не запускаются автоматически."
   textSize=16f
   setTextColor(Color.rgb(205,190,220))
   gravity=android.view.Gravity.CENTER
   setPadding(0,28,0,28)
  }
  val status=TextView(this).apply{
   text="Версия "+BuildConfig.VERSION_NAME+" • SAFE MODE"
   setTextColor(Color.rgb(168,85,247))
   gravity=android.view.Gravity.CENTER
  }
  val reset=Button(this).apply{
   text="Сбросить сохранённый адрес Core"
   setOnClickListener{
    getSharedPreferences("kira",0).edit().remove("url").remove("crash_pending").apply()
    Toast.makeText(this@MainActivity,"Настройки подключения сброшены",Toast.LENGTH_SHORT).show()
   }
  }
  root.addView(title);root.addView(info);root.addView(status);root.addView(reset)
  setContentView(root)
 }
}

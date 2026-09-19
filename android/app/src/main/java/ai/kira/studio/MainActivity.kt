package ai.kira.studio
import android.app.Activity
import android.os.Bundle
import android.graphics.Color
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity:Activity(){
 override fun onCreate(state:Bundle?){
  super.onCreate(state)
  val root=LinearLayout(this).apply{
   orientation=LinearLayout.VERTICAL
   gravity=Gravity.CENTER
   setPadding(48,48,48,48)
   setBackgroundColor(Color.rgb(10,7,16))
  }
  root.addView(TextView(this).apply{
   text="Kira Studio"
   textSize=30f
   setTextColor(Color.WHITE)
   gravity=Gravity.CENTER
  })
  root.addView(TextView(this).apply{
   text="Android platform-only SAFE BUILD 1.5.1\nЕсли этот экран остаётся открытым, базовый APK исправен."
   textSize=17f
   setTextColor(Color.rgb(205,190,220))
   gravity=Gravity.CENTER
   setPadding(0,28,0,0)
  })
  setContentView(root)
 }
}
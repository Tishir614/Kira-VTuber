plugins { id("com.android.application") }
android { namespace="ai.kira.studio"; compileSdk=35
 defaultConfig { applicationId="ai.kira.studio"; minSdk=26; targetSdk=35; versionCode=3; versionName="1.2.0" }
 buildFeatures { buildConfig=true }
}
dependencies {
 implementation("androidx.activity:activity-ktx:1.10.1")
 implementation("androidx.core:core-ktx:1.15.0")
 implementation("androidx.work:work-runtime-ktx:2.10.0")
 implementation("androidx.core:core-splashscreen:1.0.1")
}

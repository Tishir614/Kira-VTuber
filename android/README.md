# Kira Studio Android

Native Android shell for Kira Studio. It opens the mobile Studio served by Kira Core and behaves like a dedicated app.

## Build
Open `android/` in Android Studio and build the `app` module.

Set the Kira Core URL on first launch, for example `https://kira.example.com/studio`. HTTPS is recommended. The URL is stored only on the device.

The Android app includes:
- dedicated fullscreen WebView
- JavaScript, DOM storage and file upload for Live2D ZIP
- Android back navigation
- external OAuth links open in the system browser
- pull-to-refresh through the reload action in Studio

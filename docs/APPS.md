# Kira Studio applications

Kira Studio ships as three clients around one Kira Core.

## Windows
Use the generated `Kira-Studio-Setup.exe`. User data is stored under LocalAppData/KiraStudio. Only one desktop instance is allowed at a time.

## Arch/Linux
Extract `Kira-Studio-Linux-x86_64.tar.gz` and run `./install.sh`. The application installs per-user into `~/.local/bin` and its desktop entry into `~/.local/share/applications`. Runtime data is stored in `~/.local/share/KiraStudio`.

## Android
The Android app is a native WebView shell for a reachable Kira Core. It stores the chosen HTTPS server address locally, performs background health checks, and exposes the native bridge used by Studio.

The heavy local models, streaming integrations and Live2D backend remain in Kira Core rather than being duplicated inside the Android APK.

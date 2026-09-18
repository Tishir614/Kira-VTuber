# Kira Cloud design

Kira Cloud is a separate desktop, not remote control of the user's applications.

The first implementation provides an isolated Linux desktop reachable only from localhost. Kira can have her own browser profile, downloads, save files and installed applications there. Host folders are not mounted.

## Safety boundaries
Kira Core should request explicit capabilities from the cloud agent. Browser navigation, screenshots, keyboard/mouse and game launch belong inside the isolated desktop. Credentials are scoped per service and must not be copied from the user's host browser.

## Games
Browser games and Linux-native games can run in the isolated environment. GPU-heavy games need a machine/VM with GPU passthrough and compatible drivers. Anti-cheat protected games may not work in containers.

## Next agent layer
A cloud-agent API can expose: open URL, search web, screenshot, click/type, launch an allow-listed game, stop game, and report current foreground app. Keep destructive filesystem/shell operations outside the default capability set.

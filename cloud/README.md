# Kira Cloud Desktop

Isolated desktop intended for Kira's own browser/game workspace. It does not control the host desktop.

Architecture:
- Linux container/VM dedicated to Kira
- Chromium profile owned by Kira
- optional game clients installed only inside that environment
- no host home-directory mounts by default
- browser/game automation talks to Kira Core through an explicit local API
- persistent Kira home volume for saves and browser profile

For real game GPU acceleration, prefer a dedicated VM or container host with explicit GPU passthrough. Never mount the user's personal home, browser profile, SSH keys, or application data into Kira Cloud.

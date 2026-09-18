# Local self-test

Kira Studio exposes local-only checks for audio devices, microphone recording, speech recognition and Piper playback.

These tests deliberately do not install system packages automatically. Package availability and names can change on Arch Linux, and system-level installation should remain an explicit user action.

Use `scripts/arch-check.sh` to see which executables are currently available. The API remains bound to localhost by default.

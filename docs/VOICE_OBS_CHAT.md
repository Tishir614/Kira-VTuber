# Voice + OBS + chat pipeline

Primary runtime path:

Twitch / YouTube chat -> normalized queue -> stream brain -> local LLM -> subtitle state -> Piper WAV -> RMS lip-sync -> local playback -> OBS browser overlay.

The overlay is intentionally independent from OBS WebSocket. It can be captured as a Browser Source using localhost only. This keeps basic subtitles/avatar rendering usable without granting scene-control permissions to Kira.

Piper audio remains local. Lip-sync is driven from the generated WAV amplitude instead of a timer, so the future Live2D mouth parameter can follow the actual synthesized speech.

Platform chat adapters stay separate from voice and OBS. This lets one failed integration reconnect without taking down Kira's LLM, TTS or avatar state.

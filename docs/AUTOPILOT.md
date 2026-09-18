# Kira Autopilot

Autopilot is an opt-in local service. It can keep Kira's chat-response pipeline running and publish scheduled Telegram channel posts without the owner manually typing each post.

Current autonomous actions:
- generate a short channel post with the local LLM
- publish it to a configured Telegram channel through the Bot API
- keep Twitch/YouTube chat responders independent from the posting loop

Guardrails:
- disabled until explicitly enabled in Studio/API
- no fabricated news in the posting prompt
- minimum posting interval is one hour
- credentials stay in local runtime settings, excluded from Git

Going live on Twitch/YouTube is a separate media-control problem. Platform APIs manage broadcasts/channels, but an encoder such as OBS must still supply the actual audio/video stream. Future OBS WebSocket control can let Kira start/stop an already configured OBS stream profile.

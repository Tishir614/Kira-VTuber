# Kira autonomous schedule

Kira can persist a local weekly stream schedule. The scheduler uses the computer's local clock.

Flow:
1. At the configured time, ShowRunner starts the configured OBS stream.
2. Director and Stream Brain take over the live show.
3. Kira can announce the start in Telegram.
4. After the configured duration, the stream is stopped and Kira can post a closing message.
5. Enabled schedule and Telegram autopilot are restored after Kira Core restarts.

Keep OBS, Ollama, Piper and the Kira Core process running for unattended operation.

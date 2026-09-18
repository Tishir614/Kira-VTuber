# Kira Watchdog

The watchdog is the recovery layer for unattended operation.

It periodically checks the local Ollama endpoint and OBS WebSocket, watches integration task state, and attempts to restore Twitch using the saved OAuth refresh flow. During a live show, repeated critical LLM/OBS failures can trigger a safe ShowRunner stop instead of leaving an unattended broken broadcast running.

Settings:
- watchdog_interval_seconds
- watchdog_failure_limit
- watchdog_safe_stop
- watchdog_reconnect_twitch

YouTube recovery needs persisted YouTube credentials/session configuration and is intentionally not faked by this first recovery implementation.

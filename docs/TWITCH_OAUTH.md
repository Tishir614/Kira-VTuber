# Twitch OAuth

Kira uses Twitch's Authorization Code Grant for the local integration. The callback defaults to `http://127.0.0.1:8765/auth/twitch/callback` and must be registered exactly as an OAuth redirect URL in the Twitch developer application.

The current chat reader requests only `user:read:chat`, the scope required for a user-token WebSocket `channel.chat.message` subscription.

Tokens are stored only under `runtime/twitch_oauth.json`, which is excluded from Git. Client secrets must remain local.

Twitch requires third-party apps maintaining an OAuth session to validate access tokens at startup and hourly. Automatic refresh/periodic validation is the next hardening step.

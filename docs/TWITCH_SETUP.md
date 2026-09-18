# Twitch setup

Kira uses Twitch EventSub WebSocket transport and the `channel.chat.message` subscription.

Required local configuration:
- Twitch application Client ID
- user access token with the chat-read authorization required by Twitch
- broadcaster user ID
- authorized bot/user ID

Secrets/tokens must remain local and must not be committed to Git.

Kira deduplicates EventSub message IDs because Twitch EventSub delivery is at-least-once. Reconnect messages are followed using Twitch's supplied reconnect URL.

OAuth UI/token refresh and optional sending of Kira's written replies are separate follow-up pieces.

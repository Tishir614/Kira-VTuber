# Twitch

Twitch's current preferred chatbot architecture is EventSub plus the Twitch API. For a chatbot running on the user's own computer, Twitch documents WebSocket transport as the appropriate EventSub option.

Kira's Twitch boundary is intentionally not implemented with legacy IRC. The next step is OAuth plus an EventSub WebSocket subscription for `channel.chat.message`, then the Send Chat Message API for optional written replies.

Never commit Twitch client secrets or OAuth tokens.

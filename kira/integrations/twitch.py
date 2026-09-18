"""Twitch adapter boundary.

OAuth/client credentials are intentionally not hard-coded. The actual network
adapter will be enabled only after the user configures credentials locally.
Incoming normalized messages should be passed to chat_queue.push().
"""
from .base import ChatAdapter

class TwitchAdapter(ChatAdapter):
    platform="twitch"
    async def run(self): raise RuntimeError("Twitch credentials/adapter are not configured yet")
    async def stop(self): return None

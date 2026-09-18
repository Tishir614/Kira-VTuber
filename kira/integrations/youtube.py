"""YouTube Live adapter boundary.

The core does not scrape chat. A supported authenticated API adapter will feed
normalized events into chat_queue once credentials are configured locally.
"""
from .base import ChatAdapter

class YouTubeAdapter(ChatAdapter):
    platform="youtube"
    async def run(self): raise RuntimeError("YouTube credentials/adapter are not configured yet")
    async def stop(self): return None

# YouTube Live

The YouTube adapter uses the official Live Streaming API. Configure credentials locally; do not commit them.

The adapter requests `liveChatMessages.list`, follows `nextPageToken`, and respects the server-provided `pollingIntervalMillis`. Text chat messages are normalized into Kira's common stream queue.

For lower latency, the adapter can later move to the official `liveChatMessages.streamList` server-streaming method.

# Viewer memory

Kira stores a small local profile per platform + username under `runtime/viewers.json`.

Automatically stored:
- first/last seen timestamps
- message count
- normalized stream-event counters

Explicit facts are separate and limited to 20 per viewer. The core does not automatically infer sensitive traits from chat messages.

The API includes per-viewer lookup, explicit fact storage and a forget endpoint. This makes it possible to build viewer-facing privacy controls and moderator tools without deleting unrelated Kira data.

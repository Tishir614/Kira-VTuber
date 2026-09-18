# OBS audio routing

Kira can target a PipeWire playback node for synthesized speech. Set the local Studio setting `audio_output` to the node/name accepted by `pw-play --target`.

For a clean stream mix, create or select a dedicated PipeWire sink/virtual device and capture that source in OBS. Keep game/system audio on a separate device if you want independent volume control.

Kira does not automatically rewrite the user's PipeWire graph. Device creation/routing remains an explicit local setup action.

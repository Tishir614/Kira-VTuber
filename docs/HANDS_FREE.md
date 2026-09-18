# Hands-free conversation

The current microphone endpoint supports bounded recordings. The VAD module defines configuration for the next streaming microphone layer: activation threshold, silence cutoff and maximum utterance duration.

The intended pipeline is:

microphone -> VAD -> faster-whisper -> Ollama -> emotion -> Piper -> lip-sync -> avatar

Echo cancellation / half-duplex gating will prevent Kira from transcribing her own synthesized voice.

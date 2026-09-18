# Kira VTuber Core

Local-first AI VTuber core for Arch Linux.

Current foundation: Ollama local LLM, FastAPI core, avatar emotion/state bridge, and optional Supabase configuration. Inference stays local by default.

## Quick start

Install Ollama and Python 3.11+, clone this repository, run `bash scripts/install_arch.sh`, edit `.env`, pull the model configured there, and run `python -m kira.main` from the virtual environment.

## Live2D

Runtime rendering needs an exported Cubism package containing `.model3.json`, `.moc3`, textures and related files. A `.cmo3` source project must be exported from Cubism Editor first.

Next phases: faster-whisper STT, Piper TTS, persistent memory, Live2D renderer bridge, lip sync and streaming integrations.

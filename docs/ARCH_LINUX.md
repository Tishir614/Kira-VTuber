# Arch Linux local setup

Install Python, PipeWire tools and Ollama using the current packages available for your system. Do not paste secrets into shell history.

After cloning:

```bash
bash scripts/install_arch.sh
source .venv/bin/activate
pip install -r requirements-stt.txt
cp -n .env.example .env
python -m kira.main
```

The local control API binds to 127.0.0.1 by default, so it is not exposed to the LAN or Internet.

For hands-free mode the machine needs a working default microphone input. Kira pauses microphone polling while her own TTS is marked as speaking to reduce self-transcription. A future audio-stream VAD/AEC layer will improve this further.

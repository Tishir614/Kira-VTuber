class SpeechToText:
    def __init__(self) -> None:
        self._model = None

    def load(self, model_size: str = "small", device: str = "cpu", compute_type: str = "int8"):
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError("Install the optional STT dependencies first") from exc
        self._model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio_path: str, language: str = "ru") -> str:
        if self._model is None:
            self.load()
        segments, _ = self._model.transcribe(audio_path, language=language, vad_filter=True)
        return " ".join(segment.text.strip() for segment in segments).strip()

stt = SpeechToText()

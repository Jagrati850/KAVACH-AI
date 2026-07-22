"""
KAVACH AI — Speech-to-Text Engine
Transcribes uploaded call recordings (mp3/wav/m4a/ogg) to text using
faster-whisper (local Whisper model, no external API required).
The transcript is then fed into the existing scam-analysis pipeline.
"""

import asyncio
import io
from typing import Any, Dict, Optional

_model = None
_model_lock = asyncio.Lock()

# "base" is a good speed/accuracy balance for CPU-only machines and
# handles both English and Hindi/Hinglish call audio.
MODEL_SIZE = "base"


def _load_model():
    """Load the Whisper model once (lazy singleton)."""
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def _transcribe_sync(audio_bytes: bytes, language: Optional[str]) -> Dict[str, Any]:
    """Blocking transcription — run inside a worker thread."""
    model = _load_model()
    segments, info = model.transcribe(
        io.BytesIO(audio_bytes),
        language=language,
        beam_size=5,
        vad_filter=True,
    )
    parts = [seg.text.strip() for seg in segments]
    transcript = " ".join(p for p in parts if p).strip()
    return {
        "transcript": transcript,
        "detected_language": info.language,
        "language_probability": round(float(info.language_probability or 0.0), 4),
        "duration_seconds": round(float(info.duration or 0.0), 2),
    }


async def transcribe_audio(
    audio_bytes: bytes,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Transcribe call audio to text.
    language: 'en', 'hi', or None for auto-detection.
    Runs the CPU-bound model in a thread so the event loop stays responsive.
    """
    if language not in ("en", "hi"):
        language = None  # auto-detect
    async with _model_lock:
        return await asyncio.to_thread(_transcribe_sync, audio_bytes, language)

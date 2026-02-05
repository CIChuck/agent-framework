"""Adapter factory helpers for friday-speech."""

from __future__ import annotations

from ..config import SpeechConfig, TTSProvider, WakeWordProvider
from ..errors import AdapterError
from ..interfaces import STTAdapter, TTSAdapter, WakeWordAdapter


def build_tts_adapter(config: SpeechConfig) -> TTSAdapter:
    """Create a TTS adapter for the configured provider."""
    if config.tts.provider == TTSProvider.ELEVENLABS:
        from .elevenlabs import ElevenLabsAdapter

        return ElevenLabsAdapter(config.elevenlabs)
    if config.tts.provider == TTSProvider.PICOVOICE:
        from .picovoice import PicovoiceOrcaAdapter

        return PicovoiceOrcaAdapter(config.picovoice)
    raise AdapterError(f"Unsupported TTS provider: {config.tts.provider}")


def build_wakeword_adapter(config: SpeechConfig) -> WakeWordAdapter | None:
    """Create a wake word adapter if enabled."""
    if not config.wakeword.enabled:
        return None
    if config.wakeword.provider == WakeWordProvider.PICOVOICE:
        from .picovoice import PicovoicePorcupineAdapter

        return PicovoicePorcupineAdapter(config.picovoice)
    raise AdapterError(f"Unsupported wake word provider: {config.wakeword.provider}")


def build_stt_adapter(config: SpeechConfig) -> STTAdapter | None:
    """Create a speech-to-text adapter if enabled."""
    if not config.stt.enabled:
        return None
    if config.stt.provider.value == "picovoice":
        from .picovoice import PicovoiceLeopardAdapter

        return PicovoiceLeopardAdapter(config.picovoice)
    raise AdapterError(f"Unsupported STT provider: {config.stt.provider}")

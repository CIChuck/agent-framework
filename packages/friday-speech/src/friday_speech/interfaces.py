"""Protocols and shared data structures for speech adapters."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .config import VoiceSettingsConfig


class AudioFormat(str, Enum):
    """Supported audio encodings for playback."""

    MP3 = "mp3"
    PCM = "pcm"


@dataclass(frozen=True)
class AudioStream:
    """Async audio stream with format metadata."""

    format: AudioFormat
    chunks: AsyncIterator[bytes]
    sample_rate: int | None = None
    channels: int | None = None


class TTSAdapter(Protocol):
    """Text-to-speech adapter interface."""

    output_format: AudioFormat
    sample_rate: int | None
    channels: int | None

    async def stream(
        self, text: str, voice_id: str | None, settings: VoiceSettingsConfig
    ) -> AudioStream:
        """Return an async stream of audio chunks for the given text."""
        ...


class WakeWordAdapter(Protocol):
    """Wake word detection adapter interface."""

    async def wait_for_wakeword(self) -> None:
        """Block until the configured wake word is detected."""
        ...

    async def close(self) -> None:
        """Release resources and stop detection."""
        ...


class STTAdapter(Protocol):
    """Speech-to-text adapter interface."""

    async def transcribe(self) -> str:
        """Capture audio and return the transcription."""
        ...


@dataclass
class AdapterRegistry:
    """Optional adapter overrides for testing or custom wiring."""

    tts: TTSAdapter | None = None
    wakeword: WakeWordAdapter | None = None
    stt: STTAdapter | None = None

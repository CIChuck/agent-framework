"""Friday speech package."""

from .config import SpeechConfig
from .errors import (
    AdapterError,
    DependencyError,
    PlaybackError,
    SelectionError,
    SpeechConfigError,
    SpeechError,
    STTError,
    WakeWordError,
)
from .harness import SpeechHarness
from .interfaces import AdapterRegistry, AudioFormat, AudioStream, STTAdapter, TTSAdapter, WakeWordAdapter
from .service import SpeechService

__all__ = [
    "AdapterError",
    "AdapterRegistry",
    "AudioFormat",
    "AudioStream",
    "DependencyError",
    "PlaybackError",
    "SelectionError",
    "SpeechConfig",
    "SpeechConfigError",
    "SpeechError",
    "SpeechHarness",
    "SpeechService",
    "STTAdapter",
    "STTError",
    "TTSAdapter",
    "WakeWordAdapter",
    "WakeWordError",
]

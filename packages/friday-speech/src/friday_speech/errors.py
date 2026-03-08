# mypy: ignore-errors
"""Speech package errors and exception hierarchy."""


class SpeechError(Exception):
    """Base error for friday-speech."""


class SpeechConfigError(SpeechError):
    """Raised when speech configuration is invalid."""


class DependencyError(SpeechError):
    """Raised when an optional dependency is missing or incompatible."""


class AdapterError(SpeechError):
    """Raised when a provider adapter fails."""


class PlaybackError(SpeechError):
    """Raised when audio playback fails."""


class SelectionError(SpeechError):
    """Raised when speech selection/parsing fails."""


class WakeWordError(SpeechError):
    """Raised when wake word detection fails."""


class STTError(SpeechError):
    """Raised when speech-to-text processing fails."""

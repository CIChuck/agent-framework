"""Configuration models for friday-speech."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SpeechMode(str, Enum):
    """Playback mode selection."""

    LIVE = "live"
    FILE = "file"


class TTSProvider(str, Enum):
    """Supported text-to-speech providers."""

    ELEVENLABS = "elevenlabs"
    PICOVOICE = "picovoice"


class WakeWordProvider(str, Enum):
    """Supported wake word providers."""

    PICOVOICE = "picovoice"


class STTProvider(str, Enum):
    """Supported speech-to-text providers."""

    PICOVOICE = "picovoice"


class SelectionStrategy(str, Enum):
    """Strategies for selecting what to speak."""

    ALL = "all"
    FIRST_SENTENCE = "first_sentence"
    FIRST_N_WORDS = "first_n_words"
    TAGGED_ONLY = "tagged_only"
    TAGGED_EXCLUDE = "tagged_exclude"


class ChunkBoundary(str, Enum):
    """Chunking boundary selection for long speech."""

    SENTENCE = "sentence"
    WORD = "word"


class VoiceSettingsConfig(BaseModel):
    """Provider-agnostic voice settings."""

    speed: float | None = None
    stability: float | None = None
    similarity_boost: float | None = None
    style: float | None = None

    model_config = ConfigDict(extra="ignore")

    @field_validator("speed")
    @classmethod
    def _validate_speed(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if value <= 0:
            raise ValueError("speech.voice.speed must be > 0")
        return value


class SelectionTagsConfig(BaseModel):
    """Tag markers for controlling spoken content."""

    include_open: str = "<speech>"
    include_close: str = "</speech>"
    exclude_open: str = "<nospeech>"
    exclude_close: str = "</nospeech>"

    model_config = ConfigDict(extra="ignore")


class SelectionConfig(BaseModel):
    """Configuration for spoken content selection."""

    strategy: SelectionStrategy = SelectionStrategy.FIRST_SENTENCE
    max_words: int = 40
    use_punctuation: bool = True
    streaming_min_words: int | None = None
    streaming_min_chars: int | None = None
    tags: SelectionTagsConfig = Field(default_factory=SelectionTagsConfig)

    model_config = ConfigDict(extra="ignore")

    @field_validator("max_words")
    @classmethod
    def _validate_max_words(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("speech.selection.max_words must be > 0")
        return value

    @field_validator("streaming_min_words")
    @classmethod
    def _validate_streaming_min_words(cls, value: int | None) -> int | None:
        if value is None:
            return value
        if value <= 0:
            raise ValueError("speech.selection.streaming_min_words must be > 0")
        return value

    @field_validator("streaming_min_chars")
    @classmethod
    def _validate_streaming_min_chars(cls, value: int | None) -> int | None:
        if value is None:
            return value
        if value <= 0:
            raise ValueError("speech.selection.streaming_min_chars must be > 0")
        return value


class ChunkingConfig(BaseModel):
    """Configuration for chunking long speech before synthesis."""

    enabled: bool = False
    max_chars: int = 1800
    boundary: ChunkBoundary = ChunkBoundary.SENTENCE

    model_config = ConfigDict(extra="ignore")

    @field_validator("max_chars")
    @classmethod
    def _validate_max_chars(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("speech.chunking.max_chars must be > 0")
        return value


class PlaybackConfig(BaseModel):
    """Playback behavior configuration."""

    enabled: bool = True
    blocking: bool = False

    model_config = ConfigDict(extra="ignore")


class LimitsConfig(BaseModel):
    """Optional playback limits."""

    max_seconds: float | None = None

    model_config = ConfigDict(extra="ignore")

    @field_validator("max_seconds")
    @classmethod
    def _validate_max_seconds(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if value <= 0:
            raise ValueError("speech.limits.max_seconds must be > 0")
        return value


class TTSConfig(BaseModel):
    """TTS provider selection."""

    provider: TTSProvider = TTSProvider.ELEVENLABS

    model_config = ConfigDict(extra="ignore")


class WakeWordConfig(BaseModel):
    """Wake word configuration."""

    enabled: bool = False
    provider: WakeWordProvider = WakeWordProvider.PICOVOICE

    model_config = ConfigDict(extra="ignore")


class STTConfig(BaseModel):
    """Speech-to-text configuration."""

    enabled: bool = False
    provider: STTProvider = STTProvider.PICOVOICE

    model_config = ConfigDict(extra="ignore")


class ElevenLabsConfig(BaseModel):
    """ElevenLabs API configuration."""

    api_key: str | None = None
    voice_id: str | None = None
    model_id: str = "eleven_multilingual_v2"
    output_format: str = "mp3_44100_128"

    model_config = ConfigDict(extra="ignore")


class PicovoiceOrcaConfig(BaseModel):
    """Picovoice Orca TTS configuration."""

    model_path: str | None = None
    voice: str = "default"
    speech_rate: float = 1.0

    model_config = ConfigDict(extra="ignore")

    @field_validator("speech_rate")
    @classmethod
    def _validate_speech_rate(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("speech.picovoice.orca.speech_rate must be > 0")
        return value


class PicovoicePorcupineConfig(BaseModel):
    """Picovoice Porcupine wake word configuration."""

    enabled: bool = False
    keywords: list[str] = Field(default_factory=lambda: ["friday"])
    keyword_paths: list[str] = Field(default_factory=list)
    sensitivities: list[float] = Field(default_factory=lambda: [0.5])
    model_path: str | None = None

    model_config = ConfigDict(extra="ignore")

    @field_validator("sensitivities")
    @classmethod
    def _validate_sensitivities(cls, value: list[float]) -> list[float]:
        for entry in value:
            if entry < 0 or entry > 1:
                raise ValueError("speech.picovoice.porcupine.sensitivities must be 0-1")
        return value


class PicovoiceRecorderConfig(BaseModel):
    """Picovoice recorder settings."""

    device_index: int | None = None
    frame_length: int | None = None

    model_config = ConfigDict(extra="ignore")


class PicovoiceSpeakerConfig(BaseModel):
    """Picovoice speaker settings."""

    device_index: int | None = None
    buffer_size_secs: int = 20
    buffered_frames: int | None = None
    bits_per_sample: int = 16

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="after")
    def _coerce_buffered_frames(self) -> "PicovoiceSpeakerConfig":
        if self.buffered_frames is not None and self.buffer_size_secs == 20:
            self.buffer_size_secs = self.buffered_frames
        return self

    @field_validator("bits_per_sample")
    @classmethod
    def _bits_per_sample_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("speech.picovoice.speaker.bits_per_sample must be > 0")
        return value

    @field_validator("buffer_size_secs")
    @classmethod
    def _buffer_size_secs_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("speech.picovoice.speaker.buffer_size_secs must be > 0")
        return value


class PicovoiceCobraConfig(BaseModel):
    """Picovoice Cobra VAD configuration."""

    enabled: bool = False

    model_config = ConfigDict(extra="ignore")


class PicovoiceConfig(BaseModel):
    """Picovoice provider configuration."""

    access_key: str | None = None
    orca: PicovoiceOrcaConfig = Field(default_factory=PicovoiceOrcaConfig)
    porcupine: PicovoicePorcupineConfig = Field(default_factory=PicovoicePorcupineConfig)
    recorder: PicovoiceRecorderConfig = Field(default_factory=PicovoiceRecorderConfig)
    speaker: PicovoiceSpeakerConfig = Field(default_factory=PicovoiceSpeakerConfig)
    cobra: PicovoiceCobraConfig = Field(default_factory=PicovoiceCobraConfig)

    model_config = ConfigDict(extra="ignore")


class SpeechConfig(BaseModel):
    """Top-level speech configuration."""

    enabled: bool = False
    tts: TTSConfig = Field(default_factory=TTSConfig)
    wakeword: WakeWordConfig = Field(default_factory=WakeWordConfig)
    stt: STTConfig = Field(default_factory=STTConfig)
    elevenlabs: ElevenLabsConfig = Field(default_factory=ElevenLabsConfig)
    picovoice: PicovoiceConfig = Field(default_factory=PicovoiceConfig)
    mode: SpeechMode = SpeechMode.LIVE
    streaming: bool = True
    output_dir: Path = Path(".friday/speech")
    playback: PlaybackConfig = Field(default_factory=PlaybackConfig)
    selection: SelectionConfig = Field(default_factory=SelectionConfig)
    voice: VoiceSettingsConfig = Field(default_factory=VoiceSettingsConfig)
    limits: LimitsConfig = Field(default_factory=LimitsConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="after")
    def _validate_requirements(self) -> "SpeechConfig":
        if self.enabled:
            if self.tts.provider == TTSProvider.ELEVENLABS and not self.elevenlabs.api_key:
                raise ValueError(
                    "speech.elevenlabs.api_key is required when speech.tts.provider=elevenlabs"
                )
            if self.tts.provider == TTSProvider.PICOVOICE and not self.picovoice.access_key:
                raise ValueError(
                    "speech.picovoice.access_key is required when speech.tts.provider=picovoice"
                )
            if self.wakeword.enabled:
                if self.wakeword.provider == WakeWordProvider.PICOVOICE and not self.picovoice.access_key:
                    raise ValueError(
                        "speech.picovoice.access_key is required when speech.wakeword.enabled=true"
                    )
            if self.stt.enabled:
                if self.stt.provider == STTProvider.PICOVOICE and not self.picovoice.access_key:
                    raise ValueError(
                        "speech.picovoice.access_key is required when speech.stt.enabled=true"
                    )
        if self.mode == SpeechMode.FILE and not str(self.output_dir):
            raise ValueError("speech.output_dir is required when speech.mode=file")
        return self

    @classmethod
    def from_dict(cls, data: dict | None) -> "SpeechConfig":
        """Build SpeechConfig from a raw dict (typically config.yaml speech block)."""
        return cls(**(data or {}))

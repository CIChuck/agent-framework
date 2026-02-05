"""Picovoice adapters for wake word and TTS."""

from __future__ import annotations

import asyncio
import unicodedata
from array import array
from collections.abc import AsyncIterator
from typing import Any

from friday_core.logging import get_logger

from ..config import PicovoiceConfig, VoiceSettingsConfig
from ..errors import AdapterError, DependencyError, STTError, WakeWordError
from ..interfaces import AudioFormat, AudioStream, STTAdapter, TTSAdapter, WakeWordAdapter

logger = get_logger(__name__)

class PicovoiceOrcaAdapter(TTSAdapter):
    """Picovoice Orca TTS adapter."""

    def __init__(self, config: PicovoiceConfig) -> None:
        self._config = config
        self._logger = get_logger(__name__)
        self.output_format = AudioFormat.PCM
        self.sample_rate = None
        self.channels = 1

    async def stream(
        self,
        text: str,
        voice_id: str | None,
        settings: VoiceSettingsConfig,
    ) -> AudioStream:
        if not self._config.access_key:
            raise AdapterError("Picovoice access_key is required")

        try:
            import pvorca  # type: ignore
        except Exception as exc:  # pragma: no cover - dependency gate
            raise DependencyError(
                "Picovoice Orca not installed. Install with: pip install pvorca"
            ) from exc

        create_kwargs: dict[str, Any] = {
            "access_key": self._config.access_key,
            "model_path": self._config.orca.model_path,
        }

        try:
            import inspect

            supported = inspect.signature(pvorca.create).parameters
            filtered = {k: v for k, v in create_kwargs.items() if k in supported and v is not None}
            dropped = {k for k in create_kwargs if k not in filtered}
            if dropped:
                self._logger.warning(
                    "Picovoice Orca create() does not support parameters; ignoring.",
                    dropped=sorted(dropped),
                )
            orca = pvorca.create(**filtered)
        except TypeError as exc:
            self._logger.error(
                "Picovoice Orca create() failed with configured parameters; retrying with minimal args.",
                error=str(exc),
            )
            orca = pvorca.create(
                access_key=self._config.access_key,
                model_path=self._config.orca.model_path,
            )

        try:
            sanitized = _sanitize_for_orca(text, getattr(orca, "valid_characters", None))
            pcm_data = orca.synthesize(sanitized, speech_rate=self._config.orca.speech_rate)
            if isinstance(pcm_data, tuple):
                if pcm_data:
                    pcm_data = pcm_data[0]
                else:
                    pcm_data = None
            pcm_bytes = _ensure_pcm_bytes(pcm_data)

            self.sample_rate = getattr(orca, "sample_rate", None)

        finally:
            if hasattr(orca, "delete"):
                orca.delete()

        async def _generator() -> AsyncIterator[bytes]:
            yield pcm_bytes

        if not pcm_bytes:
            raise AdapterError("Picovoice Orca returned no audio")

        return AudioStream(
            format=self.output_format,
            chunks=_generator(),
            sample_rate=self.sample_rate,
            channels=self.channels,
        )


def _ensure_pcm_bytes(payload: Any) -> bytes:
    if payload is None:
        return b""
    if isinstance(payload, (bytes, bytearray)):
        return bytes(payload)
    if isinstance(payload, memoryview):
        return payload.tobytes()
    if isinstance(payload, array):
        return payload.tobytes()
    if isinstance(payload, list):
        if not payload:
            return b""
        if any(isinstance(item, float) for item in payload):
            max_abs = max(abs(float(item)) for item in payload)
            if max_abs <= 1.0:
                scaled = [int(max(-1.0, min(1.0, float(item))) * 32767) for item in payload]
                return array("h", scaled).tobytes()
        return array("h", payload).tobytes()
    if isinstance(payload, tuple):
        for item in payload:
            try:
                return _ensure_pcm_bytes(item)
            except AdapterError:
                continue
        return array("h", payload).tobytes()
    if isinstance(payload, dict):
        for key in ("pcm", "pcm_data", "audio", "data"):
            if key in payload:
                return _ensure_pcm_bytes(payload[key])
    if hasattr(payload, "pcm"):
        return _ensure_pcm_bytes(getattr(payload, "pcm"))
    if hasattr(payload, "tobytes"):
        try:
            return payload.tobytes()
        except Exception:
            pass
    try:
        import numpy as np  # type: ignore

        if isinstance(payload, np.ndarray):
            if payload.dtype != np.int16:
                payload = payload.astype(np.int16)
            return payload.tobytes()
    except Exception:
        pass
    logger.error("Unsupported PCM payload from Picovoice Orca", payload_type=type(payload).__name__)
    raise AdapterError("Unsupported PCM payload from Picovoice Orca")


def _sanitize_for_orca(text: str, valid_characters: str | None) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKC", text)
    translation = str.maketrans(
        {
            "“": '"',
            "”": '"',
            "‘": "'",
            "’": "'",
            "—": "-",
            "–": "-",
            "…": "...",
            "\u00a0": " ",
        }
    )
    normalized = normalized.translate(translation)
    if not valid_characters:
        return normalized
    allowed = set(valid_characters)
    sanitized = "".join(ch if ch in allowed else " " for ch in normalized)
    return " ".join(sanitized.split())


class PicovoicePorcupineAdapter(WakeWordAdapter):
    """Picovoice Porcupine wake word adapter."""

    def __init__(self, config: PicovoiceConfig) -> None:
        self._config = config
        self._logger = get_logger(__name__)
        self._porcupine = None
        self._recorder = None
        self._active = False

    async def wait_for_wakeword(self) -> None:
        if not self._config.access_key:
            raise WakeWordError("Picovoice access_key is required")
        await asyncio.to_thread(self._blocking_wait)

    def _blocking_wait(self) -> None:
        if not self._active:
            self._initialize()
        if not self._porcupine or not self._recorder:
            raise WakeWordError("Wake word adapter not initialized")
        while True:
            pcm = self._recorder.read()
            result = self._porcupine.process(pcm)
            if result >= 0:
                return

    def _initialize(self) -> None:
        try:
            import pvporcupine  # type: ignore
            from pvrecorder import PvRecorder  # type: ignore
        except Exception as exc:  # pragma: no cover - dependency gate
            raise DependencyError(
                "Picovoice Porcupine not installed. Install with: pip install pvporcupine pvrecorder"
            ) from exc

        porcupine_config = self._config.porcupine
        keywords = porcupine_config.keywords
        keyword_paths = porcupine_config.keyword_paths

        if not keywords and not keyword_paths:
            raise WakeWordError("Porcupine requires keywords or keyword_paths")

        self._porcupine = pvporcupine.create(
            access_key=self._config.access_key,
            keywords=keywords if keywords else None,
            keyword_paths=keyword_paths if keyword_paths else None,
            sensitivities=porcupine_config.sensitivities,
            model_path=porcupine_config.model_path,
        )

        frame_length = self._porcupine.frame_length
        recorder_config = self._config.recorder
        self._recorder = PvRecorder(
            device_index=recorder_config.device_index,
            frame_length=recorder_config.frame_length or frame_length,
        )
        self._recorder.start()
        self._active = True

    async def close(self) -> None:
        await asyncio.to_thread(self._shutdown)

    def _shutdown(self) -> None:
        if self._recorder:
            self._recorder.stop()
            if hasattr(self._recorder, "delete"):
                self._recorder.delete()
        if self._porcupine and hasattr(self._porcupine, "delete"):
            self._porcupine.delete()
        self._recorder = None
        self._porcupine = None
        self._active = False


class PicovoiceLeopardAdapter(STTAdapter):
    """Picovoice Leopard speech-to-text adapter (capture handled externally)."""

    def __init__(self, config: PicovoiceConfig) -> None:
        self._config = config
        self._logger = get_logger(__name__)

    async def transcribe(self) -> str:
        raise STTError(
            "Picovoice STT is not wired yet. Provide a custom STT adapter or implement capture."
        )

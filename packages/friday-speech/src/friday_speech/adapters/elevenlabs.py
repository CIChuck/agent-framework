# mypy: ignore-errors
"""ElevenLabs TTS adapter (best-effort streaming)."""

from __future__ import annotations

import asyncio
import re
import threading
from collections.abc import AsyncIterator, Iterable
from typing import Any

from ..config import ElevenLabsConfig, VoiceSettingsConfig
from ..errors import AdapterError, DependencyError
from ..interfaces import AudioFormat, AudioStream, TTSAdapter


class ElevenLabsAdapter(TTSAdapter):
    """ElevenLabs adapter using the official Python SDK when available."""

    def __init__(self, config: ElevenLabsConfig) -> None:
        self._config = config
        self.output_format = _infer_audio_format(config.output_format)
        self.sample_rate = _infer_sample_rate(config.output_format)
        self.channels = None

    async def stream(
        self,
        text: str,
        voice_id: str | None,
        settings: VoiceSettingsConfig,
    ) -> AudioStream:
        if not self._config.api_key:
            raise AdapterError("ElevenLabs API key is required")

        elevenlabs = _import_elevenlabs()
        client = _build_client(elevenlabs, self._config.api_key)
        payload = _build_voice_settings(settings)

        text_to_speech = getattr(client, "text_to_speech", None)
        if text_to_speech is None:
            raise AdapterError("ElevenLabs client missing text_to_speech interface")

        if hasattr(text_to_speech, "convert_as_stream"):
            sync_stream = text_to_speech.convert_as_stream(
                text=text,
                voice_id=voice_id or self._config.voice_id,
                model_id=self._config.model_id,
                output_format=self._config.output_format,
                voice_settings=payload or None,
            )
            chunks = _async_from_sync_iterator(sync_stream)
            return AudioStream(
                format=self.output_format,
                chunks=chunks,
                sample_rate=self.sample_rate,
                channels=self.channels,
            )

        if hasattr(text_to_speech, "convert"):
            audio = await asyncio.to_thread(
                text_to_speech.convert,
                text=text,
                voice_id=voice_id or self._config.voice_id,
                model_id=self._config.model_id,
                output_format=self._config.output_format,
                voice_settings=payload or None,
            )
            chunks = _async_single_chunk(audio)
            return AudioStream(
                format=self.output_format,
                chunks=chunks,
                sample_rate=self.sample_rate,
                channels=self.channels,
            )

        raise AdapterError(
            "Unsupported ElevenLabs SDK: expected text_to_speech.convert[_as_stream]"
        )


def _import_elevenlabs() -> Any:
    try:
        import elevenlabs  # type: ignore

        return elevenlabs
    except Exception as exc:  # pragma: no cover - dependency gate
        raise DependencyError(
            "ElevenLabs SDK not installed. Install with: pip install elevenlabs"
        ) from exc


def _build_client(module: Any, api_key: str) -> Any:
    for path in ("client", None):
        try:
            if path:
                client_mod = __import__(f"elevenlabs.{path}", fromlist=["ElevenLabs"])
                client_cls = getattr(client_mod, "ElevenLabs", None)
            else:
                client_cls = getattr(module, "ElevenLabs", None)
            if client_cls:
                return client_cls(api_key=api_key)
        except Exception:
            continue
    raise AdapterError("Unable to initialize ElevenLabs client")


def _build_voice_settings(settings: VoiceSettingsConfig) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if settings.stability is not None:
        payload["stability"] = settings.stability
    if settings.similarity_boost is not None:
        payload["similarity_boost"] = settings.similarity_boost
    if settings.style is not None:
        payload["style"] = settings.style
    if settings.speed is not None:
        payload["speed"] = settings.speed
    return payload


def _infer_audio_format(output_format: str) -> AudioFormat:
    value = output_format.lower()
    if value.startswith("mp3"):
        return AudioFormat.MP3
    if value.startswith("pcm"):
        return AudioFormat.PCM
    raise AdapterError(f"Unsupported ElevenLabs output_format: {output_format}")


def _infer_sample_rate(output_format: str) -> int | None:
    match = re.search(r"(\d{4,6})", output_format)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _async_single_chunk(audio: Any) -> AsyncIterator[bytes]:
    async def _generator() -> AsyncIterator[bytes]:
        if isinstance(audio, (bytes, bytearray)):
            yield bytes(audio)
            return
        if isinstance(audio, Iterable):
            for chunk in audio:
                if isinstance(chunk, (bytes, bytearray)):
                    yield bytes(chunk)
                else:
                    raise AdapterError("ElevenLabs stream yielded non-bytes chunk")
            return
        raise AdapterError("ElevenLabs audio payload is not bytes or iterable")

    return _generator()


def _async_from_sync_iterator(stream: Iterable[Any]) -> AsyncIterator[bytes]:
    async def _generator() -> AsyncIterator[bytes]:
        queue: asyncio.Queue[Any] = asyncio.Queue()
        sentinel = object()
        loop = asyncio.get_running_loop()

        def _worker() -> None:
            try:
                for chunk in stream:
                    loop.call_soon_threadsafe(queue.put_nowait, chunk)
            except Exception as exc:
                loop.call_soon_threadsafe(queue.put_nowait, exc)
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, sentinel)

        threading.Thread(target=_worker, daemon=True).start()

        while True:
            item = await queue.get()
            if item is sentinel:
                break
            if isinstance(item, Exception):
                raise item
            if not isinstance(item, (bytes, bytearray)):
                raise AdapterError("ElevenLabs stream yielded non-bytes chunk")
            yield bytes(item)

    return _generator()

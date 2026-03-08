# mypy: ignore-errors
"""Audio playback utilities for friday-speech."""

from __future__ import annotations

import asyncio
import shutil
import tempfile
from array import array
from collections.abc import AsyncIterator, Iterable
from datetime import datetime, timezone
from pathlib import Path

from friday_core.logging import get_logger

from .config import LimitsConfig, PlaybackConfig, SpeechMode
from .errors import DependencyError, PlaybackError
from .interfaces import AudioFormat, AudioStream

logger = get_logger(__name__)


def _timestamp_slug() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y%m%d_%H%M%S")


async def play_audio_stream(
    stream: AudioStream,
    mode: SpeechMode,
    playback: PlaybackConfig,
    output_dir: Path,
    streaming: bool,
    limits: LimitsConfig,
    speaker_config: object | None = None,
) -> Path | None:
    """Play or save the provided audio stream."""
    if mode == SpeechMode.FILE:
        return await _save_mp3(stream, output_dir)

    if not playback.enabled:
        logger.info("Speech playback disabled; skipping audio output")
        return None

    if stream.format == AudioFormat.MP3:
        if streaming:
            logger.warning("MP3 streaming is not supported; buffering before playback")
        if limits.max_seconds is not None:
            logger.warning("max_seconds limit not enforced for MP3 playback")
        data = await _collect_chunks(stream.chunks)
        await _play_mp3_bytes(data, playback.blocking)
        return None

    if stream.format == AudioFormat.PCM:
        await _play_pcm_stream(
            stream,
            playback.blocking,
            streaming,
            limits,
            speaker_config,
        )
        return None

    raise PlaybackError(f"Unsupported audio format: {stream.format}")


async def _save_mp3(stream: AudioStream, output_dir: Path) -> Path:
    if stream.format != AudioFormat.MP3:
        raise PlaybackError("File mode requires MP3 output format")
    output_dir.mkdir(parents=True, exist_ok=True)
    data = await _collect_chunks(stream.chunks)
    filename = f"speech_{_timestamp_slug()}.mp3"
    target = output_dir / filename
    target.write_bytes(data)
    logger.info("Saved speech audio", path=str(target))
    return target


async def _collect_chunks(chunks: Iterable[bytes] | AsyncIterator[bytes]) -> bytes:
    if isinstance(chunks, (bytes, bytearray)):
        return bytes(chunks)
    if isinstance(chunks, Iterable):
        return b"".join(chunks)
    data = bytearray()
    async for chunk in chunks:
        data.extend(chunk)
    return bytes(data)


async def _play_mp3_bytes(data: bytes, blocking: bool) -> None:
    if not data:
        raise PlaybackError("No audio data to play")
    if not shutil.which("afplay"):
        raise PlaybackError("afplay not found on PATH")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)

    try:
        process = await asyncio.create_subprocess_exec("afplay", str(tmp_path))
    except Exception as exc:
        _cleanup_temp(tmp_path)
        raise PlaybackError(f"Failed to start afplay: {exc}") from exc
    if blocking:
        try:
            await process.wait()
        finally:
            _cleanup_temp(tmp_path)
    else:
        asyncio.create_task(_await_process(process, tmp_path))


async def _await_process(process: asyncio.subprocess.Process, tmp_path: Path) -> None:
    try:
        await process.wait()
    except asyncio.CancelledError:
        process.terminate()
        raise
    finally:
        _cleanup_temp(tmp_path)


def _cleanup_temp(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        logger.warning("Failed to remove temp audio file", path=str(path))


async def _play_pcm_stream(
    stream: AudioStream,
    blocking: bool,
    _streaming: bool,
    limits: LimitsConfig,
    speaker_config: object | None,
) -> None:
    if stream.sample_rate is None:
        raise PlaybackError("PCM playback requires sample_rate")

    try:
        from pvspeaker import PvSpeaker  # type: ignore
    except Exception as exc:  # pragma: no cover - dependency gate
        raise DependencyError(
            "Picovoice speaker not installed. Install with: pip install pvspeaker"
        ) from exc

    speaker_kwargs: dict[str, int] = {}
    if hasattr(speaker_config, "device_index"):
        device_index = speaker_config.device_index
        if device_index is not None:
            speaker_kwargs["device_index"] = device_index
    if hasattr(speaker_config, "buffer_size_secs"):
        speaker_kwargs["buffer_size_secs"] = speaker_config.buffer_size_secs

    supported = {}
    try:
        import inspect

        supported = inspect.signature(PvSpeaker.__init__).parameters
        if "bits_per_sample" in supported and "bits_per_sample" not in speaker_kwargs:
            bits_per_sample = getattr(speaker_config, "bits_per_sample", 16)
            if bits_per_sample:
                speaker_kwargs["bits_per_sample"] = bits_per_sample
        filtered = {
            k: v for k, v in speaker_kwargs.items() if k in supported and v is not None
        }
        dropped = {k for k in speaker_kwargs if k not in filtered}
        if dropped:
            logger.warning(
                "PvSpeaker does not support parameters; ignoring.",
                dropped=sorted(dropped),
            )
        speaker = PvSpeaker(stream.sample_rate, **filtered)
    except TypeError as exc:
        logger.error(
            "PvSpeaker init failed with configured parameters; retrying with minimal args.",  # noqa: E501
            error=str(exc),
        )
        if "bits_per_sample" in supported:
            speaker = PvSpeaker(
                stream.sample_rate, speaker_kwargs.get("bits_per_sample", 16)
            )
        else:
            speaker = PvSpeaker(stream.sample_rate)
    speaker.start()

    max_frames = None
    if limits.max_seconds is not None:
        max_frames = int(stream.sample_rate * limits.max_seconds)

    try:
        frames_written = 0
        bits_per_sample = speaker_kwargs.get("bits_per_sample", 16)
        bytes_per_sample = max(1, bits_per_sample // 8)
        async for chunk in stream.chunks:
            if not chunk:
                continue
            if max_frames is not None and frames_written >= max_frames:
                break
            if bits_per_sample == 16 and isinstance(
                chunk, (bytes, bytearray, memoryview)
            ):
                pcm_samples = array("h")
                pcm_samples.frombytes(bytes(chunk))
                offset = 0
                total = len(pcm_samples)
                while offset < total:
                    written = speaker.write(pcm_samples[offset:])
                    if written <= 0:
                        await asyncio.sleep(0.01)
                        continue
                    offset += written
                    frames_written += written
            elif isinstance(chunk, array):
                offset = 0
                total = len(chunk)
                while offset < total:
                    written = speaker.write(chunk[offset:])
                    if written <= 0:
                        await asyncio.sleep(0.01)
                        continue
                    offset += written
                    frames_written += written
            else:
                view = memoryview(chunk)
                offset = 0
                length = len(view)
                while offset < length:
                    written = speaker.write(view[offset:])
                    if written <= 0:
                        await asyncio.sleep(0.01)
                        continue
                    offset += written
                    frames_written += written // bytes_per_sample
    except asyncio.CancelledError:
        raise
    finally:
        if blocking:
            speaker.flush()
        else:
            await asyncio.to_thread(speaker.flush)
        speaker.stop()
        if hasattr(speaker, "delete"):
            speaker.delete()

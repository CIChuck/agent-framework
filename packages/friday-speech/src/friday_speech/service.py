"""High-level speech orchestration service."""

from __future__ import annotations

from friday_core.logging import get_logger

from .adapters import build_stt_adapter, build_tts_adapter, build_wakeword_adapter
from .chunking import chunk_text
from .config import SpeechConfig, SpeechMode
from .errors import AdapterError
from .interfaces import AdapterRegistry, STTAdapter, TTSAdapter, WakeWordAdapter
from .playback import play_audio_stream
from .selection import select_speech_text


class SpeechService:
    """Orchestrates speech selection, synthesis, and playback."""

    def __init__(
        self,
        config: SpeechConfig,
        adapters: AdapterRegistry | None = None,
    ) -> None:
        self._logger = get_logger(__name__)
        self._config = config
        self._adapters = adapters or AdapterRegistry()
        self._tts_adapter: TTSAdapter | None = self._adapters.tts
        self._wakeword_adapter: WakeWordAdapter | None = self._adapters.wakeword
        self._stt_adapter: STTAdapter | None = self._adapters.stt

    @property
    def config(self) -> SpeechConfig:
        """Return the current speech configuration."""
        return self._config

    async def speak(
        self,
        text: str,
        voice_id: str | None = None,
        apply_selection: bool = True,
    ) -> None:
        """Select and synthesize speech for the provided text."""
        if not self._config.enabled:
            self._logger.debug("Speech disabled; skipping")
            return

        if self._config.mode == SpeechMode.LIVE and not self._config.playback.enabled:
            self._logger.info("Speech playback disabled; skipping synthesis")
            return

        speak_text = (
            select_speech_text(text, self._config.selection)
            if apply_selection
            else text
        )
        if not speak_text.strip():
            self._logger.info("No speech content selected")
            return

        tts = self._get_tts_adapter()
        chunks = [speak_text]
        if self._config.chunking.enabled:
            chunks = chunk_text(
                speak_text,
                max_chars=self._config.chunking.max_chars,
                boundary=self._config.chunking.boundary.value,
            )

        for chunk in chunks:
            if not chunk.strip():
                continue
            audio_stream = await tts.stream(chunk, voice_id, self._config.voice)

            await play_audio_stream(
                audio_stream,
                mode=self._config.mode,
                playback=self._config.playback,
                output_dir=self._config.output_dir,
                streaming=self._config.streaming,
                limits=self._config.limits,
                speaker_config=self._config.picovoice.speaker,
            )

    async def wait_for_wakeword(self) -> None:
        """Block until wake word detection triggers."""
        if not self._config.enabled or not self._config.wakeword.enabled:
            return
        adapter = self._get_wakeword_adapter()
        await adapter.wait_for_wakeword()

    async def transcribe(self) -> str:
        """Run speech-to-text and return the transcription."""
        if not self._config.enabled or not self._config.stt.enabled:
            raise AdapterError("Speech-to-text is not enabled")
        adapter = self._get_stt_adapter()
        return await adapter.transcribe()

    async def close(self) -> None:
        """Close any underlying adapters."""
        if self._wakeword_adapter:
            await self._wakeword_adapter.close()

    def _get_tts_adapter(self) -> TTSAdapter:
        if self._tts_adapter is None:
            self._tts_adapter = build_tts_adapter(self._config)
        return self._tts_adapter

    def _get_wakeword_adapter(self) -> WakeWordAdapter:
        if self._wakeword_adapter is None:
            adapter = build_wakeword_adapter(self._config)
            if adapter is None:
                raise AdapterError("Wake word adapter is not configured")
            self._wakeword_adapter = adapter
        return self._wakeword_adapter

    def _get_stt_adapter(self) -> STTAdapter:
        if self._stt_adapter is None:
            adapter = build_stt_adapter(self._config)
            if adapter is None:
                raise AdapterError("Speech-to-text adapter is not configured")
            self._stt_adapter = adapter
        return self._stt_adapter

# mypy: ignore-errors
"""Speech test harness for wake word, STT, and TTS."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Any

from friday_core.logging import get_logger

from .config import SpeechConfig
from .errors import SpeechConfigError
from .interfaces import AdapterRegistry
from .service import SpeechService


class SpeechHarness:
    """Configurable speech harness for local testing."""

    def __init__(
        self,
        config: SpeechConfig,
        adapters: AdapterRegistry | None = None,
    ) -> None:
        self._logger = get_logger(__name__)
        self._config = config
        self._service = SpeechService(config, adapters=adapters)

    async def run(self) -> None:
        """Run the harness continuously."""
        if not self._config.enabled:
            raise SpeechConfigError("speech.enabled must be true to run the harness")
        self._logger.info("Speech harness started")
        try:
            while True:
                await self.run_once()
        finally:
            await self._service.close()

    async def run_once(self, text: str | None = None) -> None:
        """Run a single wake word -> STT -> TTS cycle."""
        if not self._config.enabled:
            raise SpeechConfigError("speech.enabled must be true to run the harness")

        if self._config.wakeword.enabled:
            self._logger.info("Waiting for wake word")
            await self._service.wait_for_wakeword()
            self._logger.info("Wake word detected")

        if self._config.stt.enabled:
            self._logger.info("Listening for speech")
            text = await self._service.transcribe()
            self._logger.info("STT captured", text=text)

        if text is None:
            text = await _prompt_text()

        response = f"Echo: {text}"
        self._logger.info("Speaking response")
        await self._service.speak(response)


async def _prompt_text() -> str:
    return await asyncio.to_thread(input, "Type text to speak: ")


def _load_speech_config(path: Path) -> SpeechConfig:
    try:
        import yaml
    except Exception as exc:  # pragma: no cover - dependency gate
        raise SpeechConfigError(
            "pyyaml is required to load config.yaml (pip install pyyaml)"
        ) from exc

    if not path.exists():
        raise SpeechConfigError(f"Config file not found: {path}")

    raw: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
    speech_block = raw.get("speech", {})
    return SpeechConfig.from_dict(speech_block)


def main() -> None:
    """Entry point for running the speech harness standalone."""
    parser = argparse.ArgumentParser(description="Friday Speech Harness")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml (default: ./config.yaml)",
    )
    args = parser.parse_args()

    config = _load_speech_config(Path(args.config))
    asyncio.run(SpeechHarness(config).run())


if __name__ == "__main__":
    main()

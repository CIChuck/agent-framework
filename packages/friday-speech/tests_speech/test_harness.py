"""Tests for the speech harness pipeline."""

import pytest
from friday_speech import (
    AdapterRegistry,
    AudioFormat,
    AudioStream,
    SpeechConfig,
    SpeechHarness,
)


class FakeTTSAdapter:
    """Minimal TTS adapter for testing."""

    output_format = AudioFormat.MP3
    sample_rate = None
    channels = None

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def stream(
        self, text: str, voice_id: str | None, settings: object
    ) -> AudioStream:
        self.calls.append(text)

        async def _generator():
            yield b"fake-audio"

        return AudioStream(format=self.output_format, chunks=_generator())


@pytest.mark.asyncio
async def test_harness_runs_single_cycle(tmp_path) -> None:
    config = SpeechConfig.from_dict(
        {
            "enabled": True,
            "tts": {"provider": "elevenlabs"},
            "elevenlabs": {"api_key": "test"},
            "mode": "file",
            "output_dir": str(tmp_path),
        }
    )
    fake_tts = FakeTTSAdapter()
    harness = SpeechHarness(config, adapters=AdapterRegistry(tts=fake_tts))

    await harness.run_once(text="hello")

    assert fake_tts.calls == ["Echo: hello"]
    files = list(tmp_path.glob("*.mp3"))
    assert files, "expected an mp3 file to be created"

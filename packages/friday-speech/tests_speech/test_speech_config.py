# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for speech configuration validation."""

import pytest
from friday_speech import SpeechConfig


def test_disabled_allows_missing_keys() -> None:
    config = SpeechConfig.from_dict({})
    assert config.enabled is False


def test_enabled_requires_elevenlabs_key() -> None:
    with pytest.raises(ValueError):
        SpeechConfig.from_dict({"enabled": True})


def test_enabled_picovoice_requires_access_key() -> None:
    with pytest.raises(ValueError):
        SpeechConfig.from_dict({"enabled": True, "tts": {"provider": "picovoice"}})

    config = SpeechConfig.from_dict(
        {
            "enabled": True,
            "tts": {"provider": "picovoice"},
            "picovoice": {"access_key": "test"},
        }
    )
    assert config.picovoice.access_key == "test"


def test_wakeword_requires_access_key() -> None:
    with pytest.raises(ValueError):
        SpeechConfig.from_dict(
            {
                "enabled": True,
                "tts": {"provider": "elevenlabs"},
                "elevenlabs": {"api_key": "test"},
                "wakeword": {"enabled": True, "provider": "picovoice"},
            }
        )


def test_streaming_selection_thresholds_validate() -> None:
    with pytest.raises(ValueError):
        SpeechConfig.from_dict({"selection": {"streaming_min_words": 0}})
    with pytest.raises(ValueError):
        SpeechConfig.from_dict({"selection": {"streaming_min_chars": -1}})


def test_chunking_max_chars_validate() -> None:
    with pytest.raises(ValueError):
        SpeechConfig.from_dict({"chunking": {"max_chars": 0}})

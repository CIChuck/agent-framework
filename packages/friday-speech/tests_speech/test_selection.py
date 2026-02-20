"""Tests for speech text selection and tag parsing."""

from friday_speech.config import SelectionConfig, SelectionStrategy
from friday_speech.selection import select_speech_text


def test_include_tags_override_strategy() -> None:
    config = SelectionConfig(strategy=SelectionStrategy.ALL)
    text = "Hello <speech>World</speech>!"
    assert select_speech_text(text, config) == "World"


def test_malformed_tags_fallback_to_strategy() -> None:
    config = SelectionConfig(strategy=SelectionStrategy.FIRST_N_WORDS, max_words=1)
    text = "Hello <speech>World"
    assert select_speech_text(text, config) == "Hello"


def test_tagged_only_without_tags_is_empty() -> None:
    config = SelectionConfig(strategy=SelectionStrategy.TAGGED_ONLY)
    assert select_speech_text("No tags here", config) == ""


def test_tagged_exclude_removes_segment() -> None:
    config = SelectionConfig(strategy=SelectionStrategy.TAGGED_EXCLUDE)
    text = "Say this <nospeech>ignore</nospeech> please."
    result = select_speech_text(text, config)
    assert "ignore" not in result
    assert result.startswith("Say")


def test_first_sentence_strategy() -> None:
    config = SelectionConfig(strategy=SelectionStrategy.FIRST_SENTENCE)
    text = "First sentence. Second sentence."
    assert select_speech_text(text, config) == "First sentence."

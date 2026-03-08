# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for speech chunking helpers."""

from friday_speech.chunking import chunk_text


def test_chunk_text_sentence_boundary() -> None:
    text = "Hello world. This is a test. Another sentence."
    chunks = chunk_text(text, max_chars=20, boundary="sentence")
    assert chunks
    assert all(len(chunk) <= 20 for chunk in chunks)


def test_chunk_text_word_boundary_fallback() -> None:
    text = "word " * 100
    chunks = chunk_text(text, max_chars=30, boundary="word")
    assert chunks
    assert all(len(chunk) <= 30 for chunk in chunks)

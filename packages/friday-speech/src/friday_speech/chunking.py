"""Chunking helpers for long speech synthesis."""

from __future__ import annotations

import re


def chunk_text(text: str, max_chars: int, boundary: str) -> list[str]:
    """Split text into chunks that fit within max_chars."""
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    if boundary == "sentence":
        return _chunk_by_sentence(text, max_chars)
    return _chunk_by_word(text, max_chars)


def _chunk_by_sentence(text: str, max_chars: int) -> list[str]:
    pattern = re.compile(r".*?[.!?](?:\s+|$)", re.DOTALL)
    sentences = pattern.findall(text)
    if not sentences:
        return _chunk_by_word(text, max_chars)

    remainder = text[sum(len(s) for s in sentences):]
    if remainder:
        sentences.append(remainder)

    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(sentence) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(_chunk_by_word(sentence, max_chars))
            continue
        if len(current) + len(sentence) <= max_chars:
            current += sentence
        else:
            if current:
                chunks.append(current.strip())
            current = sentence

    if current.strip():
        chunks.append(current.strip())
    return chunks


def _chunk_by_word(text: str, max_chars: int) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    current_words: list[str] = []
    current_len = 0

    for word in words:
        extra = len(word) + (1 if current_words else 0)
        if current_len + extra <= max_chars:
            current_words.append(word)
            current_len += extra
            continue
        if current_words:
            chunks.append(" ".join(current_words))
        current_words = [word]
        current_len = len(word)

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks

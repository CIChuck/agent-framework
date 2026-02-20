"""Speech selection strategies and tag parsing."""

from __future__ import annotations

import re

from .config import SelectionConfig, SelectionStrategy, SelectionTagsConfig
from .errors import SelectionError


class TagParseResult:
    """Result of parsing speech tags."""

    def __init__(
        self,
        include_segments: list[str],
        exclude_spans: list[tuple[int, int]],
        malformed: bool,
    ):
        self.include_segments = include_segments
        self.exclude_spans = exclude_spans
        self.malformed = malformed


def _compile_tag_pattern(tags: SelectionTagsConfig) -> re.Pattern[str]:
    escaped = [
        re.escape(tags.include_open),
        re.escape(tags.include_close),
        re.escape(tags.exclude_open),
        re.escape(tags.exclude_close),
    ]
    return re.compile("|".join(escaped))


def _strip_tags(text: str, tags: SelectionTagsConfig) -> str:
    pattern = _compile_tag_pattern(tags)
    return pattern.sub("", text)


def _parse_tags(text: str, tags: SelectionTagsConfig) -> TagParseResult:
    pattern = _compile_tag_pattern(tags)
    include_segments: list[str] = []
    exclude_spans: list[tuple[int, int]] = []
    current: tuple[str, int] | None = None
    malformed = False

    for match in pattern.finditer(text):
        token = match.group(0)
        if token == tags.include_open:
            if current is not None:
                malformed = True
                break
            current = ("include", match.end())
        elif token == tags.include_close:
            if current is None or current[0] != "include":
                malformed = True
                break
            include_segments.append(text[current[1] : match.start()])
            current = None
        elif token == tags.exclude_open:
            if current is not None:
                malformed = True
                break
            current = ("exclude", match.end())
        elif token == tags.exclude_close:
            if current is None or current[0] != "exclude":
                malformed = True
                break
            exclude_spans.append((current[1], match.start()))
            current = None

    if current is not None:
        malformed = True

    return TagParseResult(include_segments, exclude_spans, malformed)


def _apply_excludes(text: str, spans: list[tuple[int, int]]) -> str:
    if not spans:
        return text
    filtered: list[str] = []
    last_index = 0
    for start, end in sorted(spans):
        filtered.append(text[last_index:start])
        last_index = end
    filtered.append(text[last_index:])
    return "".join(filtered)


def _first_sentence(text: str, use_punctuation: bool) -> str:
    if not use_punctuation:
        return text.strip()
    match = re.search(r"[.!?]", text)
    if not match:
        return text.strip()
    return text[: match.end()].strip()


def _first_n_words(text: str, count: int) -> str:
    words = text.split()
    if len(words) <= count:
        return text
    return " ".join(words[:count])


def select_speech_text(text: str, config: SelectionConfig) -> str:
    """Select the portion of text that should be spoken."""
    if not text:
        return ""

    tags = config.tags
    tag_result = _parse_tags(text, tags)

    if tag_result.malformed:
        cleaned = _strip_tags(text, tags)
        return _apply_strategy(cleaned, config)

    if tag_result.include_segments:
        return " ".join(
            segment.strip()
            for segment in tag_result.include_segments
            if segment.strip()
        )

    if config.strategy == SelectionStrategy.TAGGED_ONLY:
        return ""

    cleaned = _strip_tags(text, tags)

    if config.strategy == SelectionStrategy.TAGGED_EXCLUDE and tag_result.exclude_spans:
        excluded = _apply_excludes(text, tag_result.exclude_spans)
        cleaned = _strip_tags(excluded, tags)

    return _apply_strategy(cleaned, config)


def _apply_strategy(text: str, config: SelectionConfig) -> str:
    if config.strategy == SelectionStrategy.ALL:
        return text.strip()
    if config.strategy == SelectionStrategy.FIRST_SENTENCE:
        return _first_sentence(text, config.use_punctuation)
    if config.strategy == SelectionStrategy.FIRST_N_WORDS:
        return _first_n_words(text, config.max_words)
    if config.strategy == SelectionStrategy.TAGGED_EXCLUDE:
        return text.strip()
    if config.strategy == SelectionStrategy.TAGGED_ONLY:
        return ""
    raise SelectionError(f"Unsupported strategy: {config.strategy}")

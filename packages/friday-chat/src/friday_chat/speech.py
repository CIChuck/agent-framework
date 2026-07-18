"""Speech integration for FridayV2."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

SPEECH_PROMPT_SNIPPET = (
    "\n\nWhen speech is enabled, wrap speakable assistant text in "
    "<say>...</say> and non-spoken text in <nosay>...</nosay>."
)


@dataclass
class SpeechPlaybackController:
    """Fake playback controller with cancellation semantics."""

    current_task_id: int | None = None
    cancelled_count: int = 0
    _next_task_id: int = 1
    started_text: list[str] = field(default_factory=list)

    def start(self, text: str) -> int:
        """Start fake playback and cancel any previous playback."""
        if self.current_task_id is not None:
            self.cancel()
        next_id = self._next_task_id
        self._next_task_id += 1
        self.current_task_id = next_id
        self.started_text.append(text)
        return next_id

    def cancel(self) -> None:
        """Cancel fake playback."""
        if self.current_task_id is not None:
            self.cancelled_count += 1
        self.current_task_id = None


def add_speech_prompt_snippet(system_prompt: str) -> str:
    """Append the speech prompt snippet once."""
    if SPEECH_PROMPT_SNIPPET.strip() in system_prompt:
        return system_prompt
    return system_prompt + SPEECH_PROMPT_SNIPPET


def remove_speech_prompt_snippet(system_prompt: str) -> str:
    """Remove the speech prompt snippet if present."""
    return system_prompt.replace(SPEECH_PROMPT_SNIPPET, "")


def strip_speech_tags(text: str) -> str:
    """Strip Friday speech include/exclude tags for terminal display."""
    text = re.sub(r"</?(say|nosay)>", "", text, flags=re.IGNORECASE)
    return text


def clean_speakable_text(text: str, *, assistant_name: str = "Friday") -> str:
    """Clean assistant text before speech playback."""
    cleaned = strip_speech_tags(text).strip()
    cleaned = re.sub(r"^\d{4}-\d{2}-\d{2}T\S+\s*", "", cleaned)
    cleaned = re.sub(r"^\[[^\]]+\]\s*", "", cleaned)
    cleaned = re.sub(rf"^{re.escape(assistant_name)}:\s*", "", cleaned)
    return cleaned.strip()


def select_streaming_snippet(
    text: str,
    *,
    strategy: str = "first_sentence",
    streaming_min_words: int = 4,
    streaming_min_chars: int = 20,
    first_n_words: int = 8,
) -> str | None:
    """Select a streaming speech snippet using Friday-py precedence."""
    include_match = re.search(r"<say>(.*?)</say>", text, flags=re.IGNORECASE | re.DOTALL)
    if include_match:
        return clean_speakable_text(include_match.group(1))
    open_include = re.search(r"<say>(.*)$", text, flags=re.IGNORECASE | re.DOTALL)
    if open_include:
        return clean_speakable_text(open_include.group(1))

    cleaned = clean_speakable_text(text)
    if strategy == "all":
        return None
    if len(cleaned.split()) >= streaming_min_words:
        return cleaned
    if len(cleaned) >= streaming_min_chars:
        return cleaned
    if strategy == "first_sentence":
        sentence = re.split(r"(?<=[.!?])\s+", cleaned, maxsplit=1)[0]
        return sentence or None
    if strategy == "first_n_words":
        return " ".join(cleaned.split()[:first_n_words]) or None
    return None

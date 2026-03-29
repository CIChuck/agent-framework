from __future__ import annotations

import textwrap
from dataclasses import dataclass

from friday_agent.profile import AgentProfile


@dataclass(frozen=True)
class PromptComposition:
    runtime_base_prompt: str | None
    agent_prompt: str
    composed_system_prompt: str


def compose_system_prompt(
    profile: AgentProfile,
    runtime_base_prompt: str | None = None,
) -> PromptComposition:
    agent_prompt = profile.render_system_prompt()
    parts = [part.strip() for part in (runtime_base_prompt, agent_prompt) if part]
    composed = "\n\n".join(parts)
    return PromptComposition(
        runtime_base_prompt=_normalize_prompt(runtime_base_prompt),
        agent_prompt=agent_prompt,
        composed_system_prompt=composed,
    )


def _normalize_prompt(prompt: str | None) -> str | None:
    if prompt is None:
        return None
    normalized = textwrap.dedent(prompt).strip()
    return normalized or None

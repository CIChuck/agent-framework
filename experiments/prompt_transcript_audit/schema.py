"""Structured result contracts for the prompt/transcript audit experiment."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PromptTranscriptAuditScenarioConfig:
    agent_name: str
    prompt: str


@dataclass
class PromptTranscriptAuditResult:
    success: bool
    agent_name: str
    session_id: str | None
    prompt: str
    response: str
    runtime_base_system_prompt: str | None
    rendered_system_prompt: str | None
    composed_system_prompt: str | None
    transcript_session_system_prompt: str | None
    transcript_entry_id: str | None
    transcript_entry_turn_number: int | None
    transcript_entry_persisted: bool
    transcript_entry_agent_id: str | None
    transcript_entry_llm_service: str | None
    transcript_entry_provider_name: str | None
    transcript_entry_model_name: str | None
    prompt_metadata_persisted: bool
    capture_context_log_enabled: bool
    context_log_present: bool
    context_log_message_count: int
    context_log_system_prompt: str | None
    context_log_matches_composed_prompt: bool
    context_log_response_content: str | None
    context_log_matches_response: bool
    llm_mode: str
    telemetry_enabled: bool
    artifact_result_path: str | None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

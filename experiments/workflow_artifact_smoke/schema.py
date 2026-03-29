from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class WorkflowArtifactSmokeScenarioConfig:
    workflow_name: str
    query: str
    output_filename: str


@dataclass
class WorkflowArtifactSmokeResult:
    success: bool
    workflow_name: str
    execution_id: str | None
    session_id: str | None
    query: str
    output_filename: str
    output_path: str | None
    output_exists: bool
    output_paragraph_count: int
    output_mentions_source: bool
    selected_article_title: str | None
    selected_article_url: str | None
    selected_article_source: str | None
    selected_article_published_at: str | None
    selected_article_valid_json: bool
    summary_artifact_present: bool
    summary_artifact_output_ref: str | None
    transcript_path: str
    transcript_exists: bool
    transcript_entry_count: int
    transcript_agent_ids: list[str]
    transcript_tool_call_count: int
    chroma_path: str
    graph_path: str
    memory_root: str
    memory_root_exists: bool
    artifact_result_path: str | None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

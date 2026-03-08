"""Tests for transcript provenance model helpers."""

from friday_transcript.models.transcript import TranscriptEntry


class TestTranscriptEntryProvenance:
    """Tests provenance field synchronization for transcript entries."""

    def test_explicit_provenance_fields_are_mirrored_into_metadata(self) -> None:
        entry = TranscriptEntry(
            id="entry-1",
            session_id="session-1",
            turn_number=1,
            workflow_id="wf-1",
            execution_id="exec-1",
            pipeline_id="pl-1",
            task_id="task-1",
            assignment_id="assign-1",
            llm_service="reasoning",
            provider_name="openai",
        )

        assert entry.metadata["workflow_id"] == "wf-1"
        assert entry.metadata["execution_id"] == "exec-1"
        assert entry.metadata["pipeline_id"] == "pl-1"
        assert entry.metadata["task_id"] == "task-1"
        assert entry.metadata["assignment_id"] == "assign-1"
        assert entry.metadata["llm_service"] == "reasoning"
        assert entry.metadata["provider_name"] == "openai"

    def test_provenance_fields_load_from_metadata(self) -> None:
        entry = TranscriptEntry(
            id="entry-2",
            session_id="session-1",
            turn_number=2,
            metadata={
                "workflow_id": "wf-2",
                "execution_id": "exec-2",
                "pipeline_id": "pl-2",
                "task_id": "task-2",
                "assignment_id": "assign-2",
                "llm_service": "fast_openai",
                "provider_name": "openai",
            },
        )

        assert entry.workflow_id == "wf-2"
        assert entry.execution_id == "exec-2"
        assert entry.pipeline_id == "pl-2"
        assert entry.task_id == "task-2"
        assert entry.assignment_id == "assign-2"
        assert entry.llm_service == "fast_openai"
        assert entry.provider_name == "openai"

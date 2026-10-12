"""Contract tests for versioned typed reorganization records."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from friday_chat.config import FridayChatConfig
from friday_chat.reorganization import (
    JournalSafeBoundary,
    JournalState,
    OperationTrigger,
    ProgressStep,
    RecoveryJournal,
    RecoveryRequest,
    ReorganizationError,
    ReorganizationErrorCode,
    ReorganizationMode,
    ReorganizationRequest,
    ReorganizationResult,
    ResultStatus,
    StoreCapabilityState,
    StoreOperationResult,
    StoreOperationStatus,
)
from friday_chat.reorganization.assembly import (
    ExitReorganizationModeError,
    build_exit_reorganization_request,
)
from friday_chat.reorganization.contracts import (
    MutationStep,
    MutationStepResult,
    MutationStepStatus,
)
from pydantic import ValidationError


def test_reorganization_and_recovery_requests_are_distinct() -> None:
    ordinary = ReorganizationRequest(
        trigger=OperationTrigger.MANUAL,
        mode=ReorganizationMode.BACKUP,
        execute=True,
    )
    recovery = RecoveryRequest(run_id="a" * 32, execute=True)

    assert ordinary.mode is ReorganizationMode.BACKUP
    assert recovery.trigger is OperationTrigger.RECOVERY
    assert "mode" not in RecoveryRequest.model_fields
    assert "run_id" not in ReorganizationRequest.model_fields


def test_analyze_execute_is_rejected_by_typed_request() -> None:
    with pytest.raises(ValidationError, match="does not support execute"):
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.ANALYZE,
            execute=True,
        )


def test_nested_store_results_reject_contradictory_outcomes() -> None:
    with pytest.raises(ValidationError, match="completed store result"):
        StoreOperationResult(
            store="vector",
            capability_state=StoreCapabilityState.PRESENT,
            status=StoreOperationStatus.COMPLETED,
            verified=False,
        )
    with pytest.raises(ValidationError, match="failed store result"):
        StoreOperationResult(
            store="transcript",
            capability_state=StoreCapabilityState.CORRUPT,
            status=StoreOperationStatus.FAILED,
            verified=False,
        )


def test_terminal_results_reject_incoherent_progress_and_cancellation() -> None:
    with pytest.raises(ValidationError, match="cancellation evidence"):
        ReorganizationResult(
            status=ResultStatus.CANCELLED,
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.BACKUP,
        )
    with pytest.raises(ValidationError, match="must have been attempted"):
        ReorganizationResult(
            status=ResultStatus.COMPLETED,
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.BACKUP,
            completed_steps=[ProgressStep.COMPLETE],
        )


def test_dry_run_rejects_execute_artifacts_and_completed_mutation() -> None:
    with pytest.raises(ValidationError, match="execute artifacts"):
        ReorganizationResult(
            status=ResultStatus.DRY_RUN_COMPLETE,
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.BACKUP,
            run_id="a" * 32,
        )
    with pytest.raises(ValidationError, match="completed mutation"):
        ReorganizationResult(
            status=ResultStatus.DRY_RUN_COMPLETE,
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            mutation_steps=[
                MutationStepResult(
                    step=MutationStep.DEDUPE,
                    status=MutationStepStatus.COMPLETED,
                    scanned_count=None,
                    candidate_count=None,
                    changed_count=None,
                )
            ],
        )


def test_failed_store_accepts_nullable_metrics_with_typed_error() -> None:
    result = StoreOperationResult(
        store="graph",
        capability_state=StoreCapabilityState.CORRUPT,
        status=StoreOperationStatus.FAILED,
        verified=False,
        item_count=None,
        errors=[
            ReorganizationError(
                code=ReorganizationErrorCode.PREFLIGHT_FAILED,
                message="graph discovery failed",
                store="graph",
            )
        ],
    )

    assert result.item_count is None


def test_exit_mode_adapter_preserves_fast_full_and_deep_contract() -> None:
    def request_for(mode: str) -> ReorganizationRequest | None:
        config = FridayChatConfig.model_validate(
            {
                "llm": {"model": "openai/test-chat-model"},
                "session": {
                    "reorganize_on_exit": True,
                    "reorganize_mode": mode,
                },
            }
        )
        return build_exit_reorganization_request(config)

    fast = request_for("fast")
    full = request_for("full")
    deep = request_for("deep")

    assert fast is not None
    assert fast.trigger is OperationTrigger.SHUTDOWN
    assert fast.mode is ReorganizationMode.FULL
    assert fast.execute
    assert fast.skip_synthesis
    assert fast.skip_verify
    assert full is not None
    assert deep is not None
    assert full == deep
    assert not full.skip_synthesis
    assert not full.skip_verify


def test_exit_mode_adapter_disables_cleanly_and_rejects_unknown_values() -> None:
    disabled = FridayChatConfig.model_validate(
        {
            "llm": {"model": "openai/test-chat-model"},
            "session": {
                "reorganize_on_exit": False,
                "reorganize_mode": "unknown-while-disabled",
            },
        }
    )
    unknown = FridayChatConfig.model_validate(
        {
            "llm": {"model": "openai/test-chat-model"},
            "session": {
                "reorganize_on_exit": True,
                "reorganize_mode": "unknown",
            },
        }
    )

    assert build_exit_reorganization_request(disabled) is None
    with pytest.raises(ExitReorganizationModeError, match="fast.*full.*deep"):
        build_exit_reorganization_request(unknown)


def test_journal_schema_and_terminal_status_are_closed(tmp_path: Path) -> None:
    now = datetime.now(UTC)
    run_id = "1" * 32
    recovery_root = tmp_path / "recovery"
    journal = RecoveryJournal(
        journal_id="2" * 32,
        lease_id="3" * 32,
        lease_nonce="4" * 32,
        run_id=run_id,
        application_id="friday-chat",
        application_version="0.1.0",
        layout_fingerprint="5" * 64,
        trigger=OperationTrigger.MANUAL,
        requested_mode=ReorganizationMode.BACKUP,
        safe_boundary=JournalSafeBoundary.LIVE_UNMODIFIED,
        recovery_root=recovery_root,
        journal_path=recovery_root / run_id / "journal.json",
        created_at=now,
        updated_at=now,
        revision=0,
        state=JournalState.CREATED,
    ).transition(
        JournalState.COMPLETE,
        updated_at=now + timedelta(microseconds=1),
        safe_boundary=JournalSafeBoundary.LIVE_UNMODIFIED,
        terminal_status=ResultStatus.FAILED,
    )

    persisted = journal.model_dump(mode="json")
    assert persisted["schema_version"] == 1
    assert persisted["terminal_status"] == "failed"

    with pytest.raises(ValidationError):
        RecoveryJournal.model_validate_json(
            json.dumps({**persisted, "schema_version": 2})
        )

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        RecoveryJournal.model_validate_json(
            json.dumps({**persisted, "unexpected": "schema drift"})
        )

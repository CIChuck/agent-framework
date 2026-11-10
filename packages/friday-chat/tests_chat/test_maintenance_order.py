"""MAINT-001 domain delegation, safe evidence and presentation tests.

The synthetic pipeline mixin below adapts historical coordinator test doubles;
its fabricated counts are never used as product or real-store behavior proof.
"""

from __future__ import annotations

import pytest
from friday_chat.reorganization.contracts import MutationStep
from friday_chat.reorganization.coordinator import to_memory_request
from friday_memory.maintenance.mutation import (
    MemoryMutationVerification,
    MemoryVerificationCounts,
)
from friday_memory.maintenance.pipeline import (
    MemoryMaintenancePipeline,
    MemoryMaintenanceRunResult,
    MemoryMaintenanceStageReceipt,
    MemoryMaintenanceStageResult,
)


def synthetic_planned_steps(request):
    return tuple(
        MutationStep(s.value)
        for s in MemoryMaintenancePipeline.planned_stages(to_memory_request(request))
    )


class SyntheticPipelineMixin:
    """Test-only application-envelope fake; real domain proofs use real Memory."""

    async def execute_pipeline(self, request, *, run_id, observer, boundary):
        self.begin_run(request)
        stages = []
        try:
            for i, stage in enumerate(
                MemoryMaintenancePipeline.planned_stages(request)
            ):
                before = MemoryMaintenanceStageReceipt(
                    operation_id=run_id, sequence=i, stage=stage
                )

                async def run_stage(stage=stage, before=before):
                    await observer.before_stage(before)
                    if MemoryMaintenancePipeline._skipped(request, stage):
                        result = MemoryMaintenanceStageResult(
                            stage=stage, receipt=before, status="skipped"
                        )
                    else:
                        receipt = before.model_copy(
                            update={
                                "plan_id": None
                                if stage.value == "lifecycle"
                                else "a" * 64,
                                "selection_sha256": "b" * 64
                                if stage.value
                                in {"verify", "verify_pending", "verify_generated"}
                                else None,
                            }
                        )
                        await observer.stage_planned(receipt)
                        old = await self.execute_step(
                            request, MutationStep(stage.value)
                        )
                        counts = (
                            MemoryVerificationCounts(
                                selected=old.candidate_count or 0,
                                verified=old.candidate_count or 0,
                                rejected=0,
                                uncertain=0,
                            )
                            if stage.value
                            in {"verify", "verify_pending", "verify_generated"}
                            else None
                        )
                        result = MemoryMaintenanceStageResult(
                            stage=stage,
                            receipt=receipt,
                            status=old.status.value,
                            scanned_count=old.scanned_count,
                            candidate_count=old.candidate_count,
                            changed_count=old.changed_count,
                            verification_counts=counts,
                        )
                    await observer.after_stage(result)
                    return result

                stages.append(await boundary.run_atomic(run_stage))

            async def post():
                await observer.before_postconditions()
                old = await self.verify_postconditions(request)
                result = MemoryMutationVerification(verified=old.verified)
                await observer.after_postconditions(result)
                return result

            verification = await boundary.run_atomic(post)
            return MemoryMaintenanceRunResult(
                operation_id=run_id,
                succeeded=verification.verified,
                stages=tuple(stages),
                postconditions=verification,
            )
        finally:
            self.end_run(request)


class CaptureObserver:
    def __init__(self):
        self.results = []
        self.plans = []

    async def before_stage(self, receipt):
        pass

    async def stage_planned(self, receipt):
        self.plans.append(receipt)

    async def after_stage(self, result):
        self.results.append(result)

    async def before_postconditions(self):
        pass

    async def after_postconditions(self, result):
        pass


async def real_coordinator(tmp_path):
    from friday_chat.reorganization.mutation import FrameworkMaintenanceMutationAdapter
    from friday_memory.maintenance import ExplicitMemoryMutationParticipant
    from friday_memory.maintenance.provider_contracts import (
        ExplicitMaintenanceProviderRegistry,
    )
    from friday_memory.maintenance.recovery_models import MemoryMaintenanceLayout
    from test_reorganization_coordinator import _production_coordinator

    fixture = await _production_coordinator(tmp_path)

    class Provider:
        def __init__(self, role):
            self.role = role
            self.calls = 0
            self.probes = 0

        async def probe(self):
            self.probes += 1

        async def complete_model(self, response_model, *, system_prompt, user_payload):
            import json

            from friday_memory.maintenance.mutation import MemoryVerificationStatus
            from friday_memory.maintenance.provider_contracts import (
                VerificationDecision,
                VerificationResponse,
            )

            self.calls += 1
            return VerificationResponse(
                decisions=tuple(
                    VerificationDecision(
                        collection=r["collection"],
                        memory_id=r["memory_id"],
                        status=MemoryVerificationStatus.VERIFIED,
                        confidence=0.9,
                    )
                    for r in json.loads(user_payload)["records"]
                )
            )

    from friday_memory.maintenance.provider_contracts import MaintenanceLlmRole

    providers = {
        r: Provider(r)
        for r in [
            MaintenanceLlmRole.CLASSIFIER,
            MaintenanceLlmRole.RESEARCHER,
            MaintenanceLlmRole.JUDGE,
        ]
    }
    memory = ExplicitMemoryMutationParticipant(
        MemoryMaintenanceLayout(
            vector_directory=fixture.layout.vector_directory,
            graph_path=fixture.layout.graph_path,
            recovery_directory=fixture.layout.recovery_root,
            log_directory=fixture.layout.log_root,
        ),
        graph_store=fixture.graph,
    )
    adapter = FrameworkMaintenanceMutationAdapter(
        memory, ExplicitMaintenanceProviderRegistry(providers, None), None
    )
    fixture.coordinator._mutation = adapter
    return fixture, adapter, providers


@pytest.mark.asyncio
@pytest.mark.parametrize("substitute", [False, True])
async def test_chat_delegates_pipeline_once(tmp_path, substitute):
    from friday_chat.reorganization.contracts import (
        OperationTrigger,
        ReorganizationMode,
        ReorganizationRequest,
        ResultStatus,
    )
    from friday_memory.maintenance.pipeline import MemoryMaintenanceRequest

    fixture, adapter, providers = await real_coordinator(tmp_path)
    original = adapter.execute_pipeline
    calls = []

    async def spy(request, *, run_id, observer, boundary):
        assert type(request) is MemoryMaintenanceRequest
        calls.append((request, run_id, observer, boundary))
        result = await original(
            request, run_id=run_id, observer=observer, boundary=boundary
        )
        return result.model_copy(update={"stages": ()}) if substitute else result

    adapter.execute_pipeline = spy
    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.VERIFY,
            execute=True,
        )
    )
    assert len(calls) == 1 and calls[0][1] == result.run_id
    assert result.status is (
        ResultStatus.FAILED_ROLLED_BACK if substitute else ResultStatus.COMPLETED
    )
    assert all(p.calls == 1 and p.probes == 0 for p in providers.values())
    assert adapter.memory._operation_id is None
    if substitute:
        import chromadb

        rows = (
            chromadb.PersistentClient(path=str(fixture.layout.vector_directory))
            .get_collection("coordinator-test")
            .get(include=["metadatas"])
        )
        assert rows["metadatas"] == [None]


@pytest.mark.asyncio
@pytest.mark.parametrize("fail_write", [False, True])
async def test_scope_receipts_reach_durable_evidence(tmp_path, fail_write):
    import json

    from friday_chat.reorganization.contracts import (
        MaintenanceRunEvidence,
        OperationTrigger,
        ReorganizationMode,
        ReorganizationRequest,
        ResultStatus,
    )
    from friday_chat.reorganization.durability import DurableArtifactError

    fixture, adapter, providers = await real_coordinator(tmp_path)
    original = fixture.coordinator._artifacts.write_run_evidence

    def write(evidence):
        if fail_write and evidence.state == "planned":
            raise DurableArtifactError("synthetic planned evidence write failure")
        return original(evidence)

    fixture.coordinator._artifacts.write_run_evidence = write
    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.VERIFY,
            execute=True,
        )
    )
    files = sorted(
        (fixture.layout.recovery_root / result.run_id / "evidence").glob("*.json")
    )
    events = [MaintenanceRunEvidence.model_validate_json(f.read_bytes()) for f in files]
    assert events[0].state == "started"
    if fail_write:
        assert result.status is ResultStatus.FAILED_ROLLED_BACK
        assert all(p.calls == 0 for p in providers.values())
    else:
        assert [e.state for e in events] == ["started", "planned", "completed"]
        assert (
            events[1].receipt == events[2].receipt == result.mutation_steps[0].receipt
        )
        assert events[1].receipt.selection_sha256 is not None
        assert "synthetic memory" not in json.dumps(
            [json.loads(f.read_text()) for f in files]
        )
        with pytest.raises(DurableArtifactError):
            original(events[1])
        wrong = events[-1].model_dump(mode="json")
        wrong["receipt"]["selection_sha256"] = "f" * 64
        with pytest.raises(ValueError):
            MaintenanceRunEvidence.model_validate(wrong, strict=False)


@pytest.mark.parametrize("args", [(), ("--execute",), ("--skip-verify", "--execute")])
def test_explicit_full_and_unchanged_modes(args):
    from friday_chat.commands.registry import (
        _parse_reorganize_invocation,
        _ReorganizeUsageError,
    )

    assert _parse_reorganize_invocation(args) == _parse_reorganize_invocation(
        ("--full", *args)
    )
    for invalid in [
        ("--full", "--full"),
        ("--full", "--verify"),
        ("--full", "--recover", "1" * 32),
        ('"--full"',),
    ]:
        with pytest.raises(_ReorganizeUsageError):
            _parse_reorganize_invocation(invalid)
    assert _parse_reorganize_invocation(("--verify",)).mode == "verify"


@pytest.mark.parametrize(
    "status", ["completed", "failed_rolled_back", "recovery_required"]
)
def test_stage_counts_and_failure_rendering(status):
    from friday_chat.commands.registry import _format_reorganization_result
    from friday_chat.reorganization.contracts import (
        MutationStepResult,
        MutationStepStatus,
        OperationTrigger,
        ReorganizationError,
        ReorganizationErrorCode,
        ReorganizationMode,
        ReorganizationResult,
        ResultStatus,
        VerificationCounts,
    )
    from friday_memory.maintenance.pipeline import MemoryMaintenanceStage

    receipt = MemoryMaintenanceStageReceipt(
        operation_id="1" * 32,
        sequence=0,
        stage=MemoryMaintenanceStage.VERIFY_PENDING,
        plan_id="a" * 64,
        selection_sha256="b" * 64,
    )
    stage = MutationStepResult(
        step=MutationStep.VERIFY_PENDING,
        status=MutationStepStatus.COMPLETED,
        candidate_count=3,
        changed_count=3,
        receipt=receipt,
        verification_counts=VerificationCounts(
            selected=3, verified=1, rejected=1, uncertain=1
        ),
    )
    result = ReorganizationResult(
        status=ResultStatus(status),
        trigger=OperationTrigger.MANUAL,
        mode=ReorganizationMode.FULL,
        mutation_steps=[stage],
        errors=[]
        if status == "completed"
        else [
            ReorganizationError(
                code=ReorganizationErrorCode.MUTATION_FAILED,
                message="synthetic failure",
            )
        ],
    )
    text = _format_reorganization_result(result, dry_run=False)
    assert "selected=3; verified=1; rejected=1; uncertain=1" in text
    assert ("attempted; rolled back" in text) == (status == "failed_rolled_back")
    assert ("retention uncertain" in text) == (status == "recovery_required")
    assert "selected=9" not in text


@pytest.mark.asyncio
async def test_approved_maintenance_help_delta_preserves_frozen_families(
    tmp_path, monkeypatch
):
    """Bounded new comparison; original immutable failing probes stay unchanged."""
    import hashlib
    import json
    from dataclasses import asdict
    from pathlib import Path

    from friday_chat.commands.registry import (
        RegistryCommandContext,
        build_default_registry,
    )
    from test_command_diagnostics import (
        FIXTURE as DIAG,
    )
    from test_command_diagnostics import (
        PILOT_EXPECTED,
        SESSION_FIXTURE,
        _capture_diagnostics,
        _capture_pilot,
        _capture_session,
    )
    from test_command_pilot import ORACLE

    monkeypatch.chdir(tmp_path)
    old_flags = [
        "--backup",
        "--dedupe",
        "--analyze",
        "--prune",
        "--synthesize",
        "--verify",
    ]
    old_usage = "[" + "|".join(old_flags) + "]"
    new_usage = "[--full|" + "|".join(old_flags) + "]"
    old_description = "Run one reorganization step instead of the full operation."
    new_description = "Choose explicit full mode or one reorganization step."

    def transform(value, reverse=False):
        if isinstance(value, dict):
            return {k: transform(v, reverse) for k, v in value.items()}
        if isinstance(value, list):
            if value == (["--full", *old_flags] if reverse else old_flags):
                return old_flags if reverse else ["--full", *old_flags]
            return [transform(v, reverse) for v in value]
        if isinstance(value, str):
            replacements = [
                (old_usage, new_usage),
                (old_description, new_description),
                (", ".join(old_flags), ", ".join(["--full", *old_flags])),
            ]
            for old, new in replacements:
                value = value.replace(new, old) if reverse else value.replace(old, new)
        return value

    registry = build_default_registry()
    actual = json.loads(
        json.dumps({k: asdict(v) for k, v in registry.commands.items()})
    )
    assert actual == transform(ORACLE["metadata"])
    assert {k: v for k, v in actual.items() if k != "reorganize"} == {
        k: v for k, v in ORACLE["metadata"].items() if k != "reorganize"
    }
    for row in ORACLE["help"]:
        assert registry.render_help(row["focus"]) == transform(row["output"])
    for row in ORACLE["dispatch"]:
        context = RegistryCommandContext(registry=registry)
        handled, result = await registry.execute(row["input"], context)
        captured = {
            "input": row["input"],
            "handled": handled,
            "output": None if result is None else result.output,
            "result_handled": None if result is None else result.handled,
            "exit": None if result is None else result.exit_requested,
            "effects": [] if result is None else [e.value for e in result.ui_effects],
            "context_exit": context.exit_requested,
        }
        assert captured == transform(row)
    from test_command_memory_queries import FIXTURE as MEMQ
    from test_command_memory_queries import _capture_memory_queries

    memory_capture = json.loads(json.dumps(await _capture_memory_queries()))
    assert memory_capture["metadata"] == MEMQ["metadata"]
    kind_refusals = {
        "insights:service-returns-meta-kind",
        "meta:service-returns-insight-kind-empty",
    }
    repaired = {
        "list-ingested:" + label
        for label in (
            "attribute-missing",
            "empty",
            "documents",
            "missing-key",
            "falsy-non-list",
            "tuple",
        )
    }
    counts = [0, 0, 0, 0]
    for row, expected in zip(memory_capture["cases"], MEMQ["cases"], strict=True):
        assert row["case"] == expected["case"]
        if row["case"] in kind_refusals:
            assert row["exception"]["type"] == "ValueError" and "result" not in row
            assert {k: v for k, v in row.items() if k != "exception"} == {
                k: v for k, v in expected.items() if k != "result"
            }
            counts[1] += 1
        elif row["case"] in repaired:
            counts[2] += (
                1  # Accepted option-R rows; typed listing tests remain authoritative.
            )
        elif row["case"] == "entities:quoted":
            changed = json.loads(json.dumps(expected))
            replacement = {
                "memory.list_entities:'\"a b\"'": "memory.list_entities:'a b'",
                "memory.list_relationships:'\"a b\"'": "memory.list_relationships:'a b'",
            }
            assert all(changed["events"].count(event) == 1 for event in replacement)
            changed["events"] = [
                replacement.get(event, event) for event in changed["events"]
            ]
            assert row == changed
            counts[3] += 1
        else:
            assert row == expected
            counts[0] += 1
    assert counts == [67, 2, 6, 1]
    # Exactly the already approved four non-string DIAG cache refusals remain.
    diagnostic = json.loads(
        json.dumps(
            await _capture_diagnostics(
                Path(str(tmp_path).removeprefix("/private")) / "exports"
            )
        )
    )
    assert diagnostic["metadata"] == DIAG["metadata"]
    refusals = 0
    for row, expected in zip(diagnostic["cases"], DIAG["cases"], strict=True):
        if ":undeclared-cache:truthy-" in expected["case"]:
            assert row["exception"]["type"] == "TypeError" and "result" not in row
            row = {k: v for k, v in row.items() if k != "exception"}
            expected = {k: v for k, v in expected.items() if k != "result"}
            refusals += 1
        assert row == expected
    assert refusals == 4
    assert json.loads(json.dumps(await _capture_session())) == SESSION_FIXTURE
    pilot = json.loads(json.dumps(await _capture_pilot()))
    for group, (count, digest) in PILOT_EXPECTED.items():
        assert len(pilot[group]) == count
        assert (
            hashlib.sha256(
                json.dumps(transform(pilot[group], True), sort_keys=True).encode()
            ).hexdigest()
            == digest
        ), group

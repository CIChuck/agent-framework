"""Complete shared execution, scope evidence and atomic cancellation proofs."""

from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

import chromadb
import pytest
from friday_memory.maintenance.models import SynthesisConfig
from friday_memory.maintenance.mutation import (
    MemoryVerificationCounts,
    MemoryVerificationSelection,
    MemoryVerificationStatus,
    VectorMemoryReference,
)
from friday_memory.maintenance.pipeline import (
    MemoryMaintenanceMode as Mode,
)
from friday_memory.maintenance.pipeline import (
    MemoryMaintenancePipeline,
    MemoryMaintenanceStageReceipt,
    ShieldedMemoryMaintenanceBoundary,
    selection_canonical_bytes,
)
from friday_memory.maintenance.pipeline import (
    MemoryMaintenanceRequest as Request,
)
from friday_memory.maintenance.pipeline import (
    MemoryMaintenanceStage as Stage,
)
from friday_memory.maintenance.provider_contracts import (
    ExplicitMaintenanceProviderRegistry,
    LifecycleStepReport,
    MaintenanceLlmRole,
    StrictProviderModel,
    SynthesisDraft,
    SynthesisResponse,
    VerificationDecision,
    VerificationResponse,
)
from pydantic import ValidationError

from .test_mutation_participant import _participant

OP = "1" * 32


@dataclass
class Llm:
    role: MaintenanceLlmRole
    calls: list[tuple[str, tuple[str, ...]]] = field(default_factory=list)
    probes: int = 0
    verdict: MemoryVerificationStatus = MemoryVerificationStatus.VERIFIED
    abstain: bool = False

    async def probe(self) -> None:
        self.probes += 1

    async def complete_model[T: StrictProviderModel](
        self, response_model: type[T], *, system_prompt: str, user_payload: str
    ) -> T:
        del system_prompt
        payload = json.loads(user_payload)
        rows = payload["records"]
        self.calls.append((self.role.value, tuple(r["memory_id"] for r in rows)))
        if response_model is SynthesisResponse:
            result = SynthesisResponse(
                drafts=()
                if self.abstain
                else (
                    SynthesisDraft(
                        collection=rows[0]["collection"],
                        source_memory_ids=tuple(r["memory_id"] for r in rows[:2]),
                        document="A novel synthetic cross-record conclusion",
                        confidence=0.99,
                        reasoning="The topic has two independent sources",
                    ),
                )
            )
        else:
            assert response_model is VerificationResponse
            expected = {"classifier": 0, "researcher": 1, "judge": 2}[self.role.value]
            assert len(payload.get("prior_decisions", [])) == expected * len(rows)
            result = VerificationResponse(
                decisions=tuple(
                    VerificationDecision(
                        collection=r["collection"],
                        memory_id=r["memory_id"],
                        status=self.verdict,
                        confidence=0.9,
                    )
                    for r in rows
                )
            )
        return response_model.model_validate(result)


@dataclass
class Embedding:
    calls: int = 0
    probes: int = 0

    async def probe(self) -> None:
        self.probes += 1

    async def embed_documents(
        self, documents: tuple[str, ...]
    ) -> tuple[tuple[float, ...], ...]:
        self.calls += 1
        return tuple((0.25, 0.75) for _ in documents)


@dataclass
class Lifecycle:
    calls: int = 0

    async def preview_reorganization_lifecycle(self) -> LifecycleStepReport:
        return LifecycleStepReport(succeeded=True)

    async def run_reorganization_lifecycle(self) -> LifecycleStepReport:
        self.calls += 1
        return LifecycleStepReport(succeeded=True, changed_count=0)


@dataclass
class Observer:
    events: list[tuple[str, object]] = field(default_factory=list)

    async def before_stage(self, receipt):
        self.events.append(("started", receipt))

    async def stage_planned(self, receipt):
        self.events.append(("planned", receipt))

    async def after_stage(self, result):
        self.events.append(("terminal", result))

    async def before_postconditions(self):
        self.events.append(("postconditions", None))

    async def after_postconditions(self, verification):
        self.events.append(("verified", verification))


async def pipeline_fixture(tmp_path: Path):
    memory, graph = await _participant(
        tmp_path, synthesis_config=SynthesisConfig(cluster_min_size=2)
    )
    collection = chromadb.PersistentClient(
        path=str(tmp_path / "vector")
    ).get_collection("primary")
    collection.update(
        ids=["insight-a", "insight-b", "pending"],
        metadatas=[
            {
                "type": "insight",
                "topic": "synthetic",
                "verification_status": "unverified",
            }
        ]
        * 3,
    )
    llms = {role: Llm(role) for role in MaintenanceLlmRole}
    embedding = Embedding()
    lifecycle = Lifecycle()
    pipeline = MemoryMaintenancePipeline(
        memory, ExplicitMaintenanceProviderRegistry(llms, embedding), lifecycle
    )
    return pipeline, llms, embedding, lifecycle, graph


@pytest.mark.parametrize("index", [0, 1])
def test_selection_digest_fixed_vectors(index: int) -> None:
    fixture = Path(__file__).with_name("fixtures") / "selection-digest-vectors.json"
    assert (
        hashlib.sha256(fixture.read_bytes()).hexdigest()
        == "398b65267321aeda278c2f161aaefc306a71187e57655941afcf03774e8b41d5"
    )
    row = json.loads(fixture.read_text())["vectors"][index]
    args = row["input"]
    selection = MemoryVerificationSelection.model_validate(
        args["selection"], strict=False
    )
    refs = tuple(VectorMemoryReference(**r) for r in args["references"])
    actual = selection_canonical_bytes(
        operation_id=args["operation_id"],
        sequence=args["sequence"],
        stage=Stage(args["stage"]),
        plan_id=args["plan_id"],
        selection=selection,
        references=refs,
    )
    assert actual == row["expected_canonical_json"].encode("utf-8")
    assert hashlib.sha256(actual).hexdigest() == row["expected_sha256"]
    for changed in [
        dict(operation_id="f" * 32),
        dict(sequence=42),
        dict(plan_id="f" * 64),
        dict(stage=Stage.VERIFY),
    ]:
        fields = dict(
            operation_id=args["operation_id"],
            sequence=args["sequence"],
            stage=Stage(args["stage"]),
            plan_id=args["plan_id"],
            selection=selection,
            references=refs,
        )
        fields.update(changed)
        if selection.mode == "created" and "operation_id" in changed:
            with pytest.raises(ValueError):
                selection_canonical_bytes(**fields)
        else:
            assert (
                hashlib.sha256(selection_canonical_bytes(**fields)).hexdigest()
                != row["expected_sha256"]
            )
    if refs:
        with pytest.raises(ValueError):
            selection_canonical_bytes(
                operation_id=args["operation_id"],
                sequence=0,
                stage=Stage.VERIFY,
                plan_id=args["plan_id"],
                selection=selection,
                references=(refs[0], refs[0]),
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "skip_synthesis,skip_verify,skip_lifecycle",
    [
        (False, False, False),
        (False, False, True),
        (False, True, False),
        (False, True, True),
        (True, False, False),
        (True, False, True),
        (True, True, False),
        (True, True, True),
    ],
)
async def test_full_order_and_same_run_synthesis(
    tmp_path: Path, skip_synthesis: bool, skip_verify: bool, skip_lifecycle: bool
) -> None:
    pipeline, llms, embedding, lifecycle, _ = await pipeline_fixture(tmp_path)
    observer = Observer()
    result = await pipeline.execute(
        Request(
            mode=Mode.FULL,
            execute=True,
            skip_synthesis=skip_synthesis,
            skip_verify=skip_verify,
            skip_lifecycle=skip_lifecycle,
        ),
        operation_id=OP,
        observer=observer,
    )
    assert result.succeeded, result.errors
    assert [r.stage.value for r in result.stages] == [
        "dedupe",
        "prune",
        "verify_pending",
        "synthesize",
        "verify_generated",
        "lifecycle",
    ]
    assert lifecycle.calls == int(not skip_lifecycle)
    if not skip_verify:
        pending = result.stages[2]
        assert pending.verification_counts == MemoryVerificationCounts(
            selected=3, verified=3, rejected=0, uncertain=0
        )
        assert pending.receipt.selection_sha256 is not None
    if not skip_synthesis and not skip_verify:
        assert llms[MaintenanceLlmRole.SYNTHESIZER].calls
        assert result.stages[4].verification_counts.selected == 1
        assert (
            result.stages[4].receipt.selection_sha256
            != result.stages[2].receipt.selection_sha256
        )
    if skip_verify:
        assert not llms[MaintenanceLlmRole.CLASSIFIER].calls
        assert result.stages[2].status == result.stages[4].status == "skipped"
    assert pipeline.memory._operation_id is None
    assert pipeline.memory._synthesis_receipts == {}


@pytest.mark.asyncio
async def test_generated_scope_is_exact(tmp_path: Path) -> None:
    pipeline, llms, _, _, _ = await pipeline_fixture(tmp_path)
    llms[MaintenanceLlmRole.JUDGE].verdict = MemoryVerificationStatus.UNCERTAIN
    result = await pipeline.execute(
        Request(mode=Mode.FULL, execute=True), operation_id=OP
    )
    assert result.succeeded, result.errors
    # No approved sources; abstention is an explicit empty creation batch.
    assert result.stages[4].verification_counts == MemoryVerificationCounts(
        selected=0, verified=0, rejected=0, uncertain=0
    )
    assert len(llms[MaintenanceLlmRole.CLASSIFIER].calls) == 1
    # A later run may reassess pending sources, never reuses a prior created receipt.
    llms[MaintenanceLlmRole.JUDGE].verdict = MemoryVerificationStatus.VERIFIED
    again = await pipeline.execute(
        Request(mode=Mode.FULL, execute=True), operation_id="2" * 32
    )
    assert again.succeeded
    assert len(llms[MaintenanceLlmRole.CLASSIFIER].calls) == 3
    generated = llms[MaintenanceLlmRole.CLASSIFIER].calls[-1][1]
    assert len(generated) == 1 and generated[0].startswith("reorg-synth-")


@pytest.mark.asyncio
async def test_preview_and_verification_call_policy(tmp_path: Path) -> None:
    pipeline, llms, embedding, _, _ = await pipeline_fixture(tmp_path)
    request = Request(mode=Mode.FULL)
    assert (await pipeline.preflight(request)).supported
    results = await pipeline.preview(request)
    assert results[3].selection_state == results[4].selection_state == "deferred"
    assert results[3].candidate_count is None and results[4].candidate_count is None
    assert (
        all(not x.calls and not x.probes for x in llms.values())
        and not embedding.calls
        and not embedding.probes
    )
    assert pipeline.memory._operation_id is None
    assert (await pipeline.preflight(Request(mode=Mode.FULL, execute=True))).supported
    assert llms[MaintenanceLlmRole.SYNTHESIZER].probes == 1
    assert all(
        not llms[r].probes
        for r in [
            MaintenanceLlmRole.CLASSIFIER,
            MaintenanceLlmRole.RESEARCHER,
            MaintenanceLlmRole.JUDGE,
        ]
    )
    pipeline.providers = ExplicitMaintenanceProviderRegistry({}, None)
    assert (await pipeline.preflight(request)).supported
    assert not (
        await pipeline.preflight(Request(mode=Mode.FULL, execute=True))
    ).supported


@pytest.mark.asyncio
@pytest.mark.parametrize("fail_worker", [False, True])
@pytest.mark.parametrize("injected", [False, True])
async def test_default_and_injected_cancellation_boundaries(
    tmp_path: Path, fail_worker: bool, injected: bool
) -> None:
    pipeline, _, _, lifecycle, graph = await pipeline_fixture(tmp_path)
    entered = asyncio.Event()
    release = asyncio.Event()
    failure = RuntimeError("worker failed after a write")
    original = lifecycle.run_reorganization_lifecycle

    async def suspended():
        # Earlier stages have already persisted verification and synthesized a record.
        entered.set()
        await release.wait()
        if fail_worker:
            raise failure
        return await original()

    lifecycle.run_reorganization_lifecycle = suspended
    observer = Observer()
    task = asyncio.create_task(
        pipeline.execute(
            Request(mode=Mode.FULL, execute=True),
            operation_id=OP,
            observer=observer,
            boundary=ShieldedMemoryMaintenanceBoundary() if injected else None,
        )
    )
    await asyncio.wait_for(entered.wait(), 5)
    task.cancel()
    await asyncio.sleep(0)
    task.cancel()
    await asyncio.sleep(0)
    assert not task.done()
    assert pipeline.memory._operation_id == OP
    release.set()
    with pytest.raises(
        RuntimeError if fail_worker else asyncio.CancelledError
    ) as raised:
        await asyncio.wait_for(task, 5)
    if fail_worker:
        assert raised.value is failure
    assert not any(e[0] == "postconditions" for e in observer.events)
    assert (
        pipeline.memory._operation_id is None
        and pipeline.memory._synthesis_receipts == {}
    )
    # Whole-run restoration is deliberately an outer transaction obligation.
    assert (await graph.get_node("active-node")) is not None


@pytest.mark.asyncio
async def test_scope_receipts_reach_durable_evidence(tmp_path: Path) -> None:
    pipeline, _, _, _, _ = await pipeline_fixture(tmp_path)
    observer = Observer()
    result = await pipeline.execute(
        Request(mode=Mode.FULL, execute=True), operation_id=OP, observer=observer
    )
    assert result.succeeded
    for stage in [Stage.VERIFY_PENDING, Stage.VERIFY_GENERATED]:
        planned = [
            v for event, v in observer.events if event == "planned" and v.stage is stage
        ]
        terminal = [
            v
            for event, v in observer.events
            if event == "terminal" and v.stage is stage
        ]
        assert len(planned) == len(terminal) == 1
        assert planned[0] is terminal[0].receipt
        assert (
            planned[0].operation_id == OP
            and planned[0].plan_id
            and planned[0].selection_sha256
        )

    class Substitute:
        async def run_atomic(self, operation):
            actual = await operation()
            return actual.model_copy()

    with pytest.raises(ValueError, match="substituted"):
        await pipeline.execute(
            Request(mode=Mode.DEDUPE, execute=True),
            operation_id="3" * 32,
            boundary=Substitute(),
        )
    assert pipeline.memory._operation_id is None


def test_strict_requests_and_receipts() -> None:
    for fields in [
        dict(mode=Mode.ANALYZE, execute=True),
        dict(mode=Mode.VERIFY, skip_verify=True),
        dict(mode=Mode.FULL, execute=1),
    ]:
        with pytest.raises(ValidationError):
            Request(**fields)
    with pytest.raises(ValidationError):
        MemoryMaintenanceStageReceipt(
            operation_id=OP, sequence=True, stage=Stage.VERIFY
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role",
    [
        MaintenanceLlmRole.CLASSIFIER,
        MaintenanceLlmRole.RESEARCHER,
        MaintenanceLlmRole.JUDGE,
    ],
)
async def test_strict_assessment_coverage_aborts_before_synthesis(
    tmp_path: Path, role
) -> None:
    pipeline, llms, _, _, _ = await pipeline_fixture(tmp_path)
    original = llms[role].complete_model

    async def incomplete(response_model, *, system_prompt, user_payload):
        response = await original(
            response_model, system_prompt=system_prompt, user_payload=user_payload
        )
        return response.model_copy(update={"decisions": response.decisions[:-1]})

    llms[role].complete_model = incomplete
    with pytest.raises(ValueError, match="changed the plan"):
        await pipeline.execute(Request(mode=Mode.FULL, execute=True), operation_id=OP)
    assert not llms[MaintenanceLlmRole.SYNTHESIZER].calls
    assert (
        pipeline.memory._operation_id is None
        and not pipeline.memory._synthesis_receipts
    )


@pytest.mark.asyncio
async def test_direct_execute_checks_capabilities_before_any_write(
    tmp_path: Path,
) -> None:
    pipeline, llms, embedding, _, graph = await pipeline_fixture(tmp_path)
    request = Request(mode=Mode.FULL, execute=True)
    assert (await pipeline.preflight(request)).supported
    # Even an earlier success cannot admit a newly missing capability.
    pipeline.providers = ExplicitMaintenanceProviderRegistry({}, None)
    failed = await pipeline.execute(request, operation_id=OP)
    assert not failed.succeeded and failed.stages == ()
    collection = chromadb.PersistentClient(
        path=str(tmp_path / "vector")
    ).get_collection("primary")
    assert set(collection.get()["ids"]) == {
        "insight-a",
        "insight-b",
        "expired",
        "pending",
    }
    assert await graph.get_node("decayed-node") is not None
    assert (
        pipeline.memory._operation_id is None
        and pipeline._prepared_key is None
        and not pipeline._active
    )
    pipeline.providers = ExplicitMaintenanceProviderRegistry(llms, embedding)
    assert (await pipeline.preflight(request)).supported
    before = (llms[MaintenanceLlmRole.SYNTHESIZER].probes, embedding.probes)
    assert (await pipeline.execute(request, operation_id="2" * 32)).succeeded
    assert (llms[MaintenanceLlmRole.SYNTHESIZER].probes, embedding.probes) == before
    assert pipeline._prepared_key is None

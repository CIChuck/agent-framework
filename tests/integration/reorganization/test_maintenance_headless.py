"""Self-contained no-Chat real-store consumer, reusable by installed proof.

Only this proof program and immutable fixture data are copied into the installed
probe lane. Production imports always resolve through that lane's interpreter.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import sys
from contextlib import suppress
from pathlib import Path


def require(value: object, message: str) -> None:
    if not value:
        raise RuntimeError(message)


class Provider:
    def __init__(self, role):
        self.role = role
        self.calls = []
        self.probes = 0

    async def probe(self):
        self.probes += 1

    async def complete_model(self, response_model, *, system_prompt, user_payload):
        from friday_memory.maintenance.mutation import MemoryVerificationStatus
        from friday_memory.maintenance.provider_contracts import (
            SynthesisDraft,
            SynthesisResponse,
            VerificationDecision,
            VerificationResponse,
        )

        payload = json.loads(user_payload)
        rows = payload["records"]
        self.calls.append(tuple(r["memory_id"] for r in rows))
        if response_model is SynthesisResponse:
            return SynthesisResponse(
                drafts=(
                    SynthesisDraft(
                        collection=rows[0]["collection"],
                        source_memory_ids=tuple(r["memory_id"] for r in rows),
                        document="A new synthetic relationship supported by the topic sources",
                        confidence=0.99,
                        reasoning="The supplied sources support this novel combination",
                    ),
                )
            )
        return VerificationResponse(
            decisions=tuple(
                VerificationDecision(
                    collection=r["collection"],
                    memory_id=r["memory_id"],
                    status=MemoryVerificationStatus.UNCERTAIN
                    if r["memory_id"] == "uncertain"
                    else MemoryVerificationStatus.VERIFIED,
                    confidence=0.9,
                )
                for r in rows
            )
        )


class Embedding:
    def __init__(self):
        self.probes = 0
        self.calls = 0

    async def probe(self):
        self.probes += 1

    async def embed_documents(self, documents):
        self.calls += 1
        return tuple((0.25, 0.75) for _ in documents)


class Lifecycle:
    def __init__(self):
        self.calls = 0

    async def preview_reorganization_lifecycle(self):
        from friday_memory.maintenance.provider_contracts import LifecycleStepReport

        return LifecycleStepReport(succeeded=True)

    async def run_reorganization_lifecycle(self):
        from friday_memory.maintenance.provider_contracts import LifecycleStepReport

        self.calls += 1
        return LifecycleStepReport(succeeded=True, changed_count=0)


class Observer:
    def __init__(self):
        self.events = []

    async def before_stage(self, receipt):
        self.events.append(("started", receipt))

    async def stage_planned(self, receipt):
        self.events.append(("planned", receipt))

    async def after_stage(self, result):
        self.events.append(("terminal", result))

    async def before_postconditions(self):
        self.events.append(("postconditions", None))

    async def after_postconditions(self, result):
        self.events.append(("verified", result))


def check_vectors(fixture: Path):
    from friday_memory.maintenance.mutation import (
        MemoryVerificationSelection,
        VectorMemoryReference,
    )
    from friday_memory.maintenance.pipeline import (
        MemoryMaintenanceStage,
        selection_canonical_bytes,
    )

    require(
        hashlib.sha256(fixture.read_bytes()).hexdigest()
        == "398b65267321aeda278c2f161aaefc306a71187e57655941afcf03774e8b41d5",
        "fixed-vector fixture changed",
    )
    for row in json.loads(fixture.read_text())["vectors"]:
        data = row["input"]
        canonical = selection_canonical_bytes(
            operation_id=data["operation_id"],
            sequence=data["sequence"],
            stage=MemoryMaintenanceStage(data["stage"]),
            plan_id=data["plan_id"],
            selection=MemoryVerificationSelection.model_validate(
                data["selection"], strict=False
            ),
            references=tuple(VectorMemoryReference(**r) for r in data["references"]),
        )
        require(
            canonical == row["expected_canonical_json"].encode(),
            "canonical bytes differ from literal",
        )
        require(
            hashlib.sha256(canonical).hexdigest() == row["expected_sha256"],
            "selection hash differs from literal",
        )


async def setup(root):
    import chromadb
    from friday_memory.adapters.graph import ElementXGraphStore
    from friday_memory.maintenance.models import SynthesisConfig
    from friday_memory.maintenance.mutation import ExplicitMemoryMutationParticipant
    from friday_memory.maintenance.pipeline import MemoryMaintenancePipeline
    from friday_memory.maintenance.provider_contracts import (
        ExplicitMaintenanceProviderRegistry,
        MaintenanceLlmRole,
    )
    from friday_memory.maintenance.recovery_models import MemoryMaintenanceLayout
    from friday_memory.models.graph import GraphNode, ProvenanceMetadata

    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(root / "vector"))
    collection = client.create_collection("headless")
    ids = ["source-a", "source-b", "uncertain", "old-meta", "non-source"]
    metadata = [
        {"type": "insight", "topic": "demo", "verification_status": "unverified"}
        for _ in ids
    ]
    metadata[3] = {
        "type": "meta_insight",
        "topic": "old",
        "verification_status": "unverified",
    }
    metadata[4] = {"type": "other", "verification_status": "unverified"}
    collection.add(
        ids=ids,
        documents=["Synthetic observation " + i for i in ids],
        metadatas=metadata,
        embeddings=[[1.0, 0.0] for _ in ids],
    )
    graph = ElementXGraphStore(str(root / "graph.gpickle"))
    await graph.add_node(
        GraphNode(
            id="baseline",
            type="Entity",
            label="Synthetic baseline",
            provenance=ProvenanceMetadata(source_id="synthetic", source_type="test"),
        )
    )
    layout = MemoryMaintenanceLayout(
        vector_directory=root / "vector",
        graph_path=root / "graph.gpickle",
        recovery_directory=root / "recovery",
        log_directory=root / "logs",
    )
    memory = ExplicitMemoryMutationParticipant(
        layout, graph_store=graph, synthesis_config=SynthesisConfig(cluster_min_size=2)
    )
    providers = {r: Provider(r) for r in MaintenanceLlmRole}
    embedding = Embedding()
    lifecycle = Lifecycle()
    return (
        MemoryMaintenancePipeline(
            memory, ExplicitMaintenanceProviderRegistry(providers, embedding), lifecycle
        ),
        providers,
        embedding,
        lifecycle,
        collection,
        graph,
        layout,
    )


async def run_flow(
    root: Path, vectors: Path, *, allow_chat: bool = False, force_reembed: bool = False
):
    if not allow_chat:
        require(
            not any(
                n == "friday_chat" or n.startswith("friday_chat.") for n in sys.modules
            ),
            "Chat imported before headless flow",
        )
    from friday_memory.maintenance.pipeline import (
        MemoryMaintenanceMode as Mode,
    )
    from friday_memory.maintenance.pipeline import (
        MemoryMaintenanceRequest as Request,
    )
    from friday_memory.maintenance.provider_contracts import MaintenanceLlmRole

    check_vectors(vectors)
    pipeline, providers, embedding, lifecycle, collection, graph, layout = await setup(
        root
    )
    preview = await pipeline.preview(Request(mode=Mode.FULL))
    require(
        [r.stage.value for r in preview]
        == [
            "dedupe",
            "prune",
            "verify_pending",
            "synthesize",
            "verify_generated",
            "lifecycle",
        ],
        "shared preview order changed",
    )
    require(
        preview[3].selection_state == preview[4].selection_state == "deferred",
        "preview predicted dependent scope",
    )
    require(
        all(not p.calls and not p.probes for p in providers.values())
        and not embedding.calls
        and not embedding.probes,
        "preview called a provider",
    )
    observer = Observer()
    request = Request(mode=Mode.FULL, execute=True, force_reembed=force_reembed)
    preflight = await pipeline.preflight(request)
    require(preflight.supported, "headless preflight failed")
    require(
        all(
            providers[r].probes == 0
            for r in [
                MaintenanceLlmRole.CLASSIFIER,
                MaintenanceLlmRole.RESEARCHER,
                MaintenanceLlmRole.JUDGE,
            ]
        ),
        "verification readiness completion occurred",
    )
    result = await pipeline.execute(request, operation_id="1" * 32, observer=observer)
    require(result.succeeded, "headless execution failed")
    pending = result.stages[3 if force_reembed else 2]
    generated = result.stages[5 if force_reembed else 4]
    require(
        pending.verification_counts.selected == 5
        and pending.verification_counts.verified == 4
        and pending.verification_counts.uncertain == 1,
        "pending scope/counts changed",
    )
    require(
        generated.verification_counts.selected
        == generated.verification_counts.verified
        == 1,
        "generated scope/counts changed",
    )
    for role in [
        MaintenanceLlmRole.CLASSIFIER,
        MaintenanceLlmRole.RESEARCHER,
        MaintenanceLlmRole.JUDGE,
    ]:
        require(
            len(providers[role].calls) == 2
            and set(providers[role].calls[0])
            == {"source-a", "source-b", "uncertain", "old-meta", "non-source"},
            "pending coverage or assessment count changed",
        )
        require(
            len(providers[role].calls[1]) == 1
            and providers[role].calls[1][0].startswith("reorg-synth-"),
            "generated scope broadened",
        )
    require(
        providers[MaintenanceLlmRole.SYNTHESIZER].calls == [("source-a", "source-b")],
        "synthesis did not use same-run verified sources",
    )
    require(
        lifecycle.calls == 1 and embedding.calls == (3 if force_reembed else 1),
        "lifecycle/embedding call count changed",
    )
    for stage in [pending, generated]:
        planned = [
            r
            for kind, r in observer.events
            if kind == "planned" and r.stage is stage.stage
        ]
        require(
            len(planned) == 1
            and planned[0] == stage.receipt
            and stage.receipt.selection_sha256,
            "planned scope missing/substituted",
        )
    require(
        pipeline.memory._operation_id is None
        and not pipeline.memory._synthesis_receipts,
        "operation receipt state leaked",
    )
    # Standalone and full skip semantics use the same engine and existing selector.
    verification = await pipeline.execute(
        Request(mode=Mode.VERIFY, execute=True), operation_id="2" * 32
    )
    require(
        len(verification.stages) == 1
        and verification.stages[0].verification_counts.selected == 1,
        "standalone pending selection changed",
    )
    synthesis = await pipeline.execute(
        Request(mode=Mode.SYNTHESIZE, execute=True), operation_id="3" * 32
    )
    require(
        len(synthesis.stages) == 1 and synthesis.stages[0].changed_count == 0,
        "standalone synthesis repeated an existing fingerprint",
    )
    skipped = await pipeline.execute(
        Request(
            mode=Mode.FULL,
            execute=True,
            skip_synthesis=True,
            skip_verify=True,
            skip_lifecycle=True,
        ),
        operation_id="4" * 32,
    )
    require(
        skipped.succeeded and [r.status for r in skipped.stages[2:]] == ["skipped"] * 4,
        "skip behavior changed",
    )
    if not allow_chat:
        require(
            not any(
                n == "friday_chat" or n.startswith("friday_chat.") for n in sys.modules
            ),
            "Chat imported during headless flow",
        )
    return {
        "stages": [r.stage.value for r in result.stages],
        "pending": pending.verification_counts.model_dump(),
        "generated": generated.verification_counts.model_dump(),
        "vectors": 2,
        "no_chat": not allow_chat,
        "records": collection.count(),
    }


def test_headless_created_verification_flow(tmp_path):
    import os
    import subprocess

    fixture = (
        Path(__file__).resolve().parents[3]
        / "packages/friday-memory/tests_memory/test_maintenance/fixtures/selection-digest-vectors.json"
    )
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(Path(__file__).resolve()),
            str(tmp_path),
            str(fixture),
        ],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    require(result.returncode == 0, result.stdout + result.stderr)
    require(
        json.loads(result.stdout.splitlines()[-1])["no_chat"],
        "headless proof did not establish no Chat",
    )


if __name__ == "__main__":
    print(
        json.dumps(
            asyncio.run(run_flow(Path(sys.argv[1]), Path(sys.argv[2]))), sort_keys=True
        )
    )


async def cancellation_restore_flow(root: Path, *, injected: bool):
    """An explicit outer transaction restores all preceding domain writes."""
    import chromadb
    from friday_memory.maintenance.pipeline import (
        MemoryMaintenanceMode as Mode,
    )
    from friday_memory.maintenance.pipeline import (
        MemoryMaintenanceRequest as Request,
    )
    from friday_memory.maintenance.pipeline import (
        ShieldedMemoryMaintenanceBoundary,
    )
    from friday_memory.maintenance.provider_contracts import LifecycleStepReport
    from friday_memory.maintenance.recovery import MemoryMaintenanceParticipant
    from friday_memory.maintenance.recovery_models import MemoryRecoveryOperation
    from friday_memory.models.graph import GraphNode, ProvenanceMetadata

    pipeline, providers, embedding, lifecycle, collection, graph, layout = await setup(
        root
    )
    recovery = MemoryMaintenanceParticipant(layout, graph_store=graph)
    before = collection.get(include=["documents", "metadatas"])
    async with recovery.maintenance_quiescence(
        MemoryRecoveryOperation.SNAPSHOT
    ) as token:
        snapshot = await recovery.create_snapshot("e" * 32, token)
    require(snapshot.verified and snapshot.manifest_path, "headless backup failed")
    entered = asyncio.Event()
    release = asyncio.Event()

    async def suspended():
        await graph.add_node(
            GraphNode(
                id="lifecycle-write",
                type="Entity",
                label="Synthetic lifecycle write",
                provenance=ProvenanceMetadata(
                    source_id="synthetic", source_type="test"
                ),
            )
        )
        entered.set()
        await release.wait()
        return LifecycleStepReport(succeeded=True, changed_count=1)

    lifecycle.run_reorganization_lifecycle = suspended
    observer = Observer()
    task = asyncio.create_task(
        pipeline.execute(
            Request(mode=Mode.FULL, execute=True),
            operation_id="d" * 32,
            observer=observer,
            boundary=ShieldedMemoryMaintenanceBoundary() if injected else None,
        )
    )
    try:
        await asyncio.wait_for(entered.wait(), 5)
        require(
            collection.count() == 6, "no preceding persisted synthesis before cancel"
        )
        task.cancel()
        await asyncio.sleep(0)
        task.cancel()
        await asyncio.sleep(0)
        require(
            not task.done() and pipeline.memory._operation_id == "d" * 32,
            "stage escaped drain under repeated cancellation",
        )
        release.set()
        try:
            await asyncio.wait_for(task, 5)
        except asyncio.CancelledError:
            pass
        else:
            raise RuntimeError("cancellation was reported as success")
        require(
            not any(kind == "postconditions" for kind, _ in observer.events),
            "next boundary ran after cancellation",
        )
        require(
            pipeline.memory._operation_id is None
            and not pipeline.memory._synthesis_receipts,
            "cancelled operation state leaked",
        )
        async with recovery.maintenance_quiescence(
            MemoryRecoveryOperation.RESTORE
        ) as token:
            restored = await recovery.restore_snapshot(snapshot.manifest_path, token)
        require(restored.verified, "headless outer restore failed")
        after = (
            chromadb.PersistentClient(path=str(layout.vector_directory))
            .get_collection("headless")
            .get(include=["documents", "metadatas"])
        )

        def records(rows):
            return {
                i: (d, m)
                for i, d, m in zip(
                    rows["ids"], rows["documents"], rows["metadatas"], strict=True
                )
            }

        require(
            records(after) == records(before),
            "rollback lost verdicts or retained generated records",
        )
        require(
            await graph.get_node("lifecycle-write") is None
            and await graph.get_node("baseline") is not None,
            "rollback did not restore graph",
        )
        return {
            "injected": injected,
            "cancelled": True,
            "restored_records": len(after["ids"]),
        }
    finally:
        release.set()
        if not task.done():
            task.cancel()
            with suppress(BaseException):
                await task


def test_default_and_injected_cancellation_boundaries(tmp_path):
    for injected in [False, True]:
        result = asyncio.run(
            cancellation_restore_flow(tmp_path / str(injected), injected=injected)
        )
        require(result["cancelled"], "headless cancellation proof failed")


async def recover_v1_fixture(fixture: Path, destination: Path, kind: str):
    """Relocate a synthetic old fixture with a recorded JSON-pointer audit."""
    import shutil

    from friday_chat.reorganization.contracts import (
        RecoveryJournal,
        RecoveryRequest,
        ResultStatus,
    )
    from friday_chat.reorganization.coordinator import (
        ManualMaintenanceDrainResult,
        ManualMaintenanceResumeResult,
        ReorganizationCoordinator,
    )
    from friday_chat.reorganization.gate import MaintenanceAdmissionGate
    from friday_chat.reorganization.layout import FridayChatMaintenanceLayout
    from friday_chat.reorganization.lease import DarwinLayoutLeaseRegistry
    from friday_memory.adapters.graph import ElementXGraphStore
    from friday_memory.maintenance.recovery import MemoryMaintenanceParticipant
    from friday_memory.maintenance.recovery_models import MemoryMaintenanceLayout
    from friday_transcript import SQLiteTranscriptStore

    source = fixture / kind
    destination = destination.resolve()
    shutil.copytree(source, destination)
    # Git archives preserve executable bits, not owner-only recovery modes.
    # Reconstitute stricter private modes only in this disposable test copy.
    permission_changes = []
    for item in [destination, *destination.rglob("*")]:
        desired = 0o700 if item.is_dir() else 0o600
        current = item.stat().st_mode & 0o777
        if current != desired:
            item.chmod(desired)
            permission_changes.append(
                {
                    "path": str(item.relative_to(destination)),
                    "before": oct(current),
                    "after": oct(desired),
                }
            )
    journal_path = next((destination / "recovery").glob("*/journal.json"))
    raw_journal = json.loads(journal_path.read_text())
    old_root = str(Path(raw_journal["recovery_root"]).parent)
    old_chat_fingerprint = raw_journal["layout_fingerprint"]
    layout = FridayChatMaintenanceLayout.resolve_once(
        captured_process_cwd=destination,
        vector_directory=destination / "live/vector",
        graph_path=destination / "live/graph.gpickle",
        access_buffer_wal_path=None,
        transcript_database_path=destination / "transcript/friday.sqlite",
        recovery_root=destination / "recovery",
        log_root=destination / "logs",
    )
    memory_layout = MemoryMaintenanceLayout(
        vector_directory=layout.vector_directory,
        graph_path=layout.graph_path,
        access_buffer_wal_path=None,
        recovery_directory=layout.recovery_root,
        log_directory=layout.log_root,
    )
    old_memory_fingerprint = json.loads(
        (journal_path.parent / "memory/manifest.json").read_text()
    )["layout_fingerprint"]
    # Instantiate the actual participant to obtain its public layout identity.
    graph = ElementXGraphStore(str(layout.graph_path))
    memory = MemoryMaintenanceParticipant(memory_layout, graph_store=graph)
    substitutions = {
        old_chat_fingerprint: layout.layout_fingerprint,
        old_memory_fingerprint: memory.layout_fingerprint,
    }
    audit = []
    original_hashes = {}
    json_files = sorted(destination.rglob("*.json"))

    def rewrite(value, pointer, file, hashes=False):
        if isinstance(value, dict):
            return {
                k: rewrite(
                    v,
                    pointer + "/" + k.replace("~", "~0").replace("/", "~1"),
                    file,
                    hashes,
                )
                for k, v in value.items()
            }
        if isinstance(value, list):
            return [
                rewrite(v, pointer + "/" + str(i), file, hashes)
                for i, v in enumerate(value)
            ]
        if isinstance(value, str):
            updated = value
            if hashes:
                updated = substitutions.get(value, value)
            elif value == old_root or value.startswith(old_root + "/"):
                updated = str(destination) + value[len(old_root) :]
            elif value in substitutions:
                updated = substitutions[value]
            if updated != value:
                audit.append(
                    {
                        "file": str(file.relative_to(destination)),
                        "pointer": pointer,
                        "old": value,
                        "new": updated,
                    }
                )
            return updated
        return value

    for file in json_files:
        original_hashes[file] = hashlib.sha256(file.read_bytes()).hexdigest()
        value = rewrite(json.loads(file.read_text()), "", file)
        file.write_text(json.dumps(value, separators=(",", ":")))
    # Update only transitive manifest hash references, in dependency order until stable.
    for _ in range(12):
        changed = False
        for file in json_files:
            current = hashlib.sha256(file.read_bytes()).hexdigest()
            previous = substitutions.get(original_hashes[file])
            if previous is not None and previous != current:
                substitutions[previous] = current
            substitutions[original_hashes[file]] = current
        for file in json_files:
            value = json.loads(file.read_text())
            updated = rewrite(value, "", file, True)
            if updated != value:
                file.write_text(json.dumps(updated, separators=(",", ":")))
                changed = True
        if not changed:
            break
    else:
        raise RuntimeError("fixture manifest checksums did not converge")
    for index, file in enumerate(json_files):
        if file.name.startswith(old_chat_fingerprint + "."):
            renamed = file.with_name(
                layout.layout_fingerprint + file.name[len(old_chat_fingerprint) :]
            )
            file.rename(renamed)
            audit.append(
                {
                    "file": str(file.relative_to(destination)),
                    "pointer": "$filename",
                    "old": file.name,
                    "new": renamed.name,
                }
            )
            original_hashes[renamed] = original_hashes[file]
            json_files[index] = renamed
    receipt = {
        "kind": kind,
        "source": str(source),
        "destination": str(destination),
        "permission_changes": permission_changes,
        "changes": audit,
        "files": [
            {
                "path": str(f.relative_to(destination)),
                "original_sha256": original_hashes[f],
                "relocated_sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
            }
            for f in json_files
        ],
    }
    (destination / "relocation-audit.json").write_text(
        json.dumps(receipt, indent=2) + "\n"
    )
    journal = RecoveryJournal.model_validate_json(journal_path.read_bytes())
    require(
        journal.schema_version == 1
        and tuple(journal.state_history)
        == tuple(
            RecoveryJournal.model_validate_json(
                next((source / "recovery").glob("*/journal.json")).read_bytes()
            ).state_history
        ),
        "relocation changed schema/history",
    )

    class Hooks:
        async def prepare_for_manual_maintenance(self):
            pass

        async def drain_for_manual_maintenance(self):
            return ManualMaintenanceDrainResult()

        def resume_after_manual_maintenance(self):
            return ManualMaintenanceResumeResult()

        async def close_for_shutdown(self, *, snapshot_requested):
            pass

        async def finalize_transcript(self):
            pass

    coordinator = ReorganizationCoordinator(
        layout=layout,
        gate=MaintenanceAdmissionGate(),
        memory_participant=memory,
        transcript_participant=SQLiteTranscriptStore(layout.transcript_database_path),
        runtime_hooks=Hooks(),
        lease_registry=DarwinLayoutLeaseRegistry(
            namespace_root=destination / "leases",
            platform_name="Darwin",
            host_id="coordinator-test",
        ),
        application_version="test",
    )
    if kind == "completed":
        historical, artifact = coordinator._artifacts.read_journal(journal_path)
        require(
            historical.schema_version == 1 and historical.state.value == "complete",
            "completed v1 record unreadable",
        )
        require(
            "mutation_steps" not in json.loads(journal_path.read_text()),
            "completed v1 record gained fabricated stage counts",
        )
        return {
            "kind": kind,
            "schema_version": 1,
            "status": historical.terminal_status.value,
            "reader": "MaintenanceArtifactStore.read_journal",
            "relocations": len(audit),
            "audit": str(destination / "relocation-audit.json"),
        }
    else:
        # Unknown sidecar versions fail reporting validation but do not gate restoration.
        evidence = journal_path.parent / "evidence"
        evidence.mkdir(exist_ok=True)
        (evidence / "00000000-completed.json").write_text('{"schema_version":999}')
        from friday_chat.reorganization.contracts import MaintenanceRunEvidence

        try:
            MaintenanceRunEvidence.model_validate_json(
                (evidence / "00000000-completed.json").read_bytes()
            )
        except ValueError:
            pass
        else:
            raise RuntimeError("unknown evidence schema accepted")
        inspected = await coordinator.recover(RecoveryRequest(run_id=journal.run_id))
        require(
            inspected.status is ResultStatus.RECOVERY_REQUIRED,
            "old interrupted journal not recoverable",
        )
        result = await coordinator.recover(
            RecoveryRequest(run_id=journal.run_id, execute=True)
        )
        require(
            result.status is ResultStatus.COMPLETED_WITH_WARNINGS,
            "v1 interrupted recovery failed: " + str(result.errors),
        )
        require(
            await graph.get_node("mutation-node") is None,
            "v1 recovery retained mutation",
        )
        require(
            await SQLiteTranscriptStore(layout.transcript_database_path).count_entries(
                "session-1"
            )
            == 1,
            "v1 transcript recovery changed entries",
        )
    return {
        "kind": kind,
        "schema_version": 1,
        "status": result.status.value,
        "relocations": len(audit),
        "audit": str(destination / "relocation-audit.json"),
    }


def test_baseline_v1_journal_recovery(tmp_path):
    fixture = (
        Path(__file__).resolve().parents[3]
        / "packages/friday-chat/tests_chat/fixtures/maintenance-v1"
    )
    for kind in ["completed", "interrupted"]:
        result = asyncio.run(recover_v1_fixture(fixture, tmp_path / kind, kind))
        require(
            result["schema_version"] == 1, "v1 recovery proof lost its original schema"
        )


async def migration_only_flow(root: Path):
    from friday_memory.maintenance.pipeline import (
        MemoryMaintenanceMode,
        MemoryMaintenanceRequest,
    )
    from friday_memory.maintenance.provider_contracts import MaintenanceLlmRole

    pipeline, providers, embedding, lifecycle, collection, graph, layout = await setup(
        root
    )
    collection.add(
        ids=["legacy-meta"],
        documents=["A pre-existing synthetic meta insight"],
        metadatas=[
            {
                "type": "meta_insight",
                "source_memories": '["source-a","source-b"]',
                "maintenance_generated": True,
                "verification_status": "verified",
            }
        ],
        embeddings=[[0.25, 0.75]],
    )
    observer = Observer()
    result = await pipeline.execute(
        MemoryMaintenanceRequest(mode=MemoryMaintenanceMode.FULL, execute=True),
        operation_id="5" * 32,
        observer=observer,
    )
    require(result.succeeded, "migration-only full run failed")
    require(result.stages[3].changed_count == 1, "migration change not reported")
    require(
        result.stages[4].verification_counts.selected == 0,
        "migration count broadened generated scope",
    )
    require(
        result.stages[4].receipt.plan_id and result.stages[4].receipt.selection_sha256,
        "empty migration scope lost evidence",
    )
    require(
        not providers[MaintenanceLlmRole.SYNTHESIZER].calls,
        "migration-only plan called synthesizer",
    )
    require(
        all(
            len(providers[r].calls) == 1
            for r in [
                MaintenanceLlmRole.CLASSIFIER,
                MaintenanceLlmRole.RESEARCHER,
                MaintenanceLlmRole.JUDGE,
            ]
        ),
        "empty migration batch called verification providers",
    )
    return {
        "migration_changes": 1,
        "generated_selected": 0,
        "records": collection.count(),
    }


def test_migration_only_full_scope(tmp_path):
    result = asyncio.run(migration_only_flow(tmp_path))
    require(result["generated_selected"] == 0, "migration-only selection proof failed")


def test_force_reembed_remains_first_in_headless_flow(tmp_path):
    vectors = (
        Path(__file__).resolve().parents[3]
        / "packages/friday-memory/tests_memory/test_maintenance/fixtures/selection-digest-vectors.json"
    )
    result = asyncio.run(
        run_flow(tmp_path, vectors, allow_chat=True, force_reembed=True)
    )
    require(result["stages"][0] == "reembed", "force-reembed lost its first stage")

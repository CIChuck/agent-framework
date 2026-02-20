from datetime import datetime, timedelta, timezone

import pytest
from friday_core.interfaces import ArbitrationDecision, SharedWriteCapability
from friday_memory.models import (
    ContextPayload,
    GraphEdge,
    GraphNode,
    ProvenanceMetadata,
)
from friday_memory.multi_agent import (
    MultiAgentMemoryController,
    NamespacePolicyEngine,
    PromotionCoordinator,
    PromotionJournal,
    PromotionJournalState,
    ScratchPadStore,
    ScratchPlanItemStatus,
    build_promotion_ops_snapshot,
)


def _provenance(author_id: str = "agent-a") -> ProvenanceMetadata:
    return ProvenanceMetadata(
        source_id="src-1",
        source_type="agent",
        author_id=author_id,
        confidence=1.0,
        created_at=datetime.now(timezone.utc),
    )


class _FakeMemory:
    def __init__(self, payload: ContextPayload) -> None:
        self._payload = payload
        self.stored_nodes: list[GraphNode] = []
        self.stored_insights: list[tuple[str, dict]] = []

    async def recall(self, **kwargs) -> ContextPayload:
        return self._payload

    async def store_fact(self, node: GraphNode, edge: GraphEdge | None = None) -> bool:
        self.stored_nodes.append(node)
        return True

    async def store_insight(
        self,
        text: str,
        provenance: ProvenanceMetadata,
        extra_metadata: dict | None = None,
    ) -> bool:
        self.stored_insights.append((text, extra_metadata or {}))
        return True


class _FakeArbitrator:
    def __init__(self, decision: ArbitrationDecision) -> None:
        self._decision = decision

    async def submit_proposal(self, proposal):
        return proposal.proposal_id

    async def get_decision(self, proposal_id: str):
        return self._decision


@pytest.mark.asyncio
async def test_multi_agent_recall_filters_private_and_shared():
    own_node = GraphNode(
        id="own",
        type="fact",
        label="Own",
        properties={"namespace": "agent-a", "visibility": "private"},
        provenance=_provenance("agent-a"),
    )
    other_node = GraphNode(
        id="other",
        type="fact",
        label="Other",
        properties={"namespace": "agent-b", "visibility": "private"},
        provenance=_provenance("agent-b"),
    )
    shared_node = GraphNode(
        id="shared",
        type="fact",
        label="Shared",
        properties={"namespace": "shared", "visibility": "shared"},
        provenance=_provenance("agent-c"),
    )
    payload = ContextPayload(
        passages=[
            {
                "text": "a",
                "metadata": {"namespace": "agent-a", "visibility": "private"},
            },
            {
                "text": "b",
                "metadata": {"namespace": "agent-b", "visibility": "private"},
            },
            {"text": "s", "metadata": {"namespace": "shared", "visibility": "shared"}},
        ],
        entities=[own_node, other_node, shared_node],
    )
    controller = MultiAgentMemoryController(
        memory=_FakeMemory(payload),  # type: ignore[arg-type]
        session_id="s1",
        agent_id="agent-a",
        namespace="agent-a",
    )

    result = await controller.recall("test", include_shared=True)
    assert len(result["passages"]) == 2
    assert {e["id"] for e in result["entities"]} == {"own", "shared"}

    no_shared = await controller.recall("test", include_shared=False)
    assert len(no_shared["passages"]) == 1
    assert {e["id"] for e in no_shared["entities"]} == {"own"}


@pytest.mark.asyncio
async def test_private_write_stamps_namespace_metadata():
    payload = ContextPayload()
    memory = _FakeMemory(payload)
    controller = MultiAgentMemoryController(
        memory=memory,  # type: ignore[arg-type]
        session_id="s1",
        agent_id="agent-a",
        namespace="agent-a",
    )
    node_id = await controller.write_private_fact("my fact")
    assert node_id
    assert memory.stored_nodes
    stored = memory.stored_nodes[0]
    assert stored.properties["namespace"] == "agent-a"
    assert stored.properties["visibility"] == "private"


@pytest.mark.asyncio
async def test_shared_write_requires_valid_capability():
    payload = ContextPayload()
    memory = _FakeMemory(payload)
    controller = MultiAgentMemoryController(
        memory=memory,  # type: ignore[arg-type]
        session_id="s1",
        agent_id="agent-a",
        namespace="agent-a",
    )
    expired = SharedWriteCapability(
        token_id="t1",
        session_id="s1",
        run_id="r1",
        issued_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    with pytest.raises(PermissionError):
        await controller.write_shared_fact("shared fact", capability=expired)

    valid = SharedWriteCapability(
        token_id="t2",
        session_id="s1",
        run_id="r1",
        issued_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    node_id = await controller.write_shared_fact("shared fact", capability=valid)
    assert node_id
    stored = memory.stored_nodes[-1]
    assert stored.properties["namespace"] == "shared"
    assert stored.properties["visibility"] == "shared"


def test_promotion_coordinator_writes_pending_journal():
    journal = PromotionJournal()
    coordinator = PromotionCoordinator(journal)
    proposal = coordinator.create_proposal(
        session_id="s1",
        namespace="agent-a",
        author_id="agent-a",
        fact="candidate fact",
    )
    entry = journal.get(proposal.proposal_id)
    assert entry is not None
    assert entry.state == PromotionJournalState.PENDING


@pytest.mark.asyncio
async def test_promotion_coordinator_executes_approved_promotion():
    journal = PromotionJournal()
    coordinator = PromotionCoordinator(journal)
    coordinator.set_arbitration(_FakeArbitrator(ArbitrationDecision.APPROVED))  # type: ignore[arg-type]
    proposal = coordinator.create_proposal(
        session_id="s1",
        namespace="agent-a",
        author_id="agent-a",
        fact="candidate fact",
    )
    memory = _FakeMemory(ContextPayload())
    promoted = await coordinator.execute_promotion(
        memory=memory, proposal_id=proposal.proposal_id
    )  # type: ignore[arg-type]
    assert promoted
    assert len(memory.stored_nodes) == 1
    assert len(memory.stored_insights) == 1
    assert journal.get(proposal.proposal_id).state == PromotionJournalState.COMMITTED


@pytest.mark.asyncio
async def test_promotion_coordinator_rejects_when_arbitration_rejects():
    journal = PromotionJournal()
    coordinator = PromotionCoordinator(journal)
    coordinator.set_arbitration(_FakeArbitrator(ArbitrationDecision.REJECTED))  # type: ignore[arg-type]
    proposal = coordinator.create_proposal(
        session_id="s1",
        namespace="agent-a",
        author_id="agent-a",
        fact="candidate fact",
    )
    memory = _FakeMemory(ContextPayload())
    promoted = await coordinator.execute_promotion(
        memory=memory, proposal_id=proposal.proposal_id
    )  # type: ignore[arg-type]
    assert not promoted
    assert len(memory.stored_nodes) == 0
    assert journal.get(proposal.proposal_id).state == PromotionJournalState.FAILED


@pytest.mark.asyncio
async def test_policy_engine_session_isolation():
    policy = NamespacePolicyEngine("s1", "agent-a", "agent-a")
    assert await policy.can_read("agent-a", "agent-a", "s1")
    assert not await policy.can_read("agent-a", "agent-a", "s2")


def test_journal_replay_and_partial_commit_detection():
    journal = PromotionJournal()
    coordinator = PromotionCoordinator(journal)
    proposal = coordinator.create_proposal(
        session_id="s1",
        namespace="agent-a",
        author_id="agent-a",
        fact="candidate fact",
        metadata={"correlation_id": "corr-1", "transcript_entry_id": "entry-1"},
    )

    journal.update_state(
        proposal.proposal_id,
        PromotionJournalState.GRAPH_WRITTEN,
        details={"graph_node_id": "node-1"},
        promotion_id="node-1",
    )
    journal.update_state(
        proposal.proposal_id,
        PromotionJournalState.FAILED,
        error="simulated failure",
    )

    timeline = journal.replay(proposal.proposal_id)
    assert [event.state for event in timeline] == [
        PromotionJournalState.PENDING,
        PromotionJournalState.GRAPH_WRITTEN,
        PromotionJournalState.FAILED,
    ]
    assert timeline[0].correlation_id == "corr-1"

    candidates = journal.list_partial_commit_candidates()
    assert len(candidates) == 1
    assert candidates[0].proposal_id == proposal.proposal_id


def test_coordinator_forensics_and_session_replay():
    journal = PromotionJournal()
    coordinator = PromotionCoordinator(journal)
    proposal_a = coordinator.create_proposal(
        session_id="s1",
        namespace="agent-a",
        author_id="agent-a",
        fact="fact a",
    )
    proposal_b = coordinator.create_proposal(
        session_id="s2",
        namespace="agent-b",
        author_id="agent-b",
        fact="fact b",
    )

    journal.update_state(
        proposal_a.proposal_id,
        PromotionJournalState.GRAPH_WRITTEN,
        details={"graph_node_id": "node-a"},
        promotion_id="node-a",
    )
    coordinator.mark_failed(proposal_a.proposal_id, "failed_a")
    coordinator.mark_committed(proposal_b.proposal_id)

    forensics = coordinator.get_forensics(proposal_a.proposal_id)
    assert forensics["partial_commit"] is True
    assert len(forensics["timeline"]) >= 3

    replay_s1 = coordinator.replay_session("s1")
    replay_s2 = coordinator.replay_session("s2")
    assert replay_s1
    assert replay_s2
    assert all(event.session_id == "s1" for event in replay_s1)
    assert all(event.session_id == "s2" for event in replay_s2)


def test_build_promotion_ops_snapshot_warns_on_backlog_and_failures():
    journal = PromotionJournal()
    coordinator = PromotionCoordinator(journal)
    proposal = coordinator.create_proposal(
        session_id="s1",
        namespace="agent-a",
        author_id="agent-a",
        fact="candidate fact",
    )
    journal.update_state(
        proposal.proposal_id,
        PromotionJournalState.GRAPH_WRITTEN,
        details={"graph_node_id": "node-1"},
        promotion_id="node-1",
    )
    coordinator.mark_failed(proposal.proposal_id, "failed")

    proposal_pending = coordinator.create_proposal(
        session_id="s1",
        namespace="agent-a",
        author_id="agent-a",
        fact="pending fact",
    )
    assert journal.get(proposal_pending.proposal_id) is not None

    snapshot = build_promotion_ops_snapshot(
        journal,
        backlog_threshold=1,
        stale_pending_after_seconds=-1,
        failure_rate_threshold=0.1,
    )
    alert_codes = {alert["code"] for alert in snapshot["alerts"]}
    assert "recovery_backlog_high" in alert_codes
    assert "degraded_arbitrator_flow" in alert_codes
    assert "promotion_failure_rate_high" in alert_codes
    assert snapshot["metrics"]["partial_commit_candidates"] == 1


def test_scratchpad_store_tracks_plan_items_and_events():
    store = ScratchPadStore(ttl_seconds=60, max_entries=10)
    store.upsert_plan_item(
        scope_id="scope-1",
        task_id="task-1",
        title="Task 1",
        status=ScratchPlanItemStatus.PENDING,
    )
    store.update_plan_item_status(
        scope_id="scope-1",
        task_id="task-1",
        status=ScratchPlanItemStatus.RUNNING,
    )
    store.append_event(
        scope_id="scope-1",
        event_type="task_started",
        workflow_id="wf",
        execution_id="exec",
        task_id="task-1",
        correlation_id="corr-1",
    )

    pad = store.get_pad("scope-1")
    assert pad is not None
    assert pad.plan_items["task-1"].status == ScratchPlanItemStatus.RUNNING
    assert len(pad.events) == 1


def test_scratchpad_store_ttl_and_quota_enforcement():
    store = ScratchPadStore(ttl_seconds=1, max_entries=1)
    store.upsert_plan_item(
        scope_id="scope-1",
        task_id="task-1",
        title="Task 1",
        status=ScratchPlanItemStatus.PENDING,
    )
    store.append_event(
        scope_id="scope-1",
        event_type="evt-1",
        workflow_id="wf",
        execution_id="exec",
    )
    with pytest.raises(RuntimeError, match="quota exceeded"):
        store.append_event(
            scope_id="scope-1",
            event_type="evt-2",
            workflow_id="wf",
            execution_id="exec",
        )
    # Force expiry and purge
    now = datetime.now(timezone.utc) + timedelta(seconds=2)
    purged = store.purge_expired(now=now)
    assert purged == 1
    assert store.get_pad("scope-1") is None

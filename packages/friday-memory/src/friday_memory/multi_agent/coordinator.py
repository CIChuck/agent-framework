# mypy: ignore-errors
"""
Promotion coordinator for additive multi-agent memory mode.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from friday_core.interfaces import ArbitrationDecision, ArbitrationInterface

from friday_memory.controller import MemoryController
from friday_memory.models import GraphNode, ProvenanceMetadata
from friday_memory.multi_agent.journal import PromotionJournal
from friday_memory.multi_agent.models import (
    SHARED_NAMESPACE,
    SHARED_VISIBILITY,
    PromotionJournalEntry,
    PromotionJournalEvent,
    PromotionJournalState,
    SharedPromotionProposal,
)


class PromotionCoordinator:
    """
    Coordinates proposal creation and journal lifecycle.

    Phase 2 scope keeps this lightweight; arbitration and atomic commit
    lifecycle hardening are expanded in later subphases.
    """

    def __init__(self, journal: PromotionJournal) -> None:
        self._journal = journal
        self._proposals: dict[str, SharedPromotionProposal] = {}
        self._arbitration: ArbitrationInterface | None = None

    def set_arbitration(self, arbitration: ArbitrationInterface) -> None:
        self._arbitration = arbitration

    def create_proposal(
        self,
        session_id: str,
        namespace: str,
        author_id: str,
        fact: str,
        metadata: dict | None = None,
    ) -> SharedPromotionProposal:
        metadata_payload = metadata or {}
        correlation_id = metadata_payload.get("correlation_id")
        transcript_entry_id = metadata_payload.get("transcript_entry_id")
        proposal = SharedPromotionProposal(
            proposal_id=str(uuid.uuid4()),
            session_id=session_id,
            namespace=namespace,
            author_id=author_id,
            fact=fact,
            metadata=metadata_payload,
            correlation_id=correlation_id,
            transcript_entry_id=transcript_entry_id,
        )
        self._proposals[proposal.proposal_id] = proposal
        self._journal.append(
            PromotionJournalEntry(
                proposal_id=proposal.proposal_id,
                state=PromotionJournalState.PENDING,
                session_id=proposal.session_id,
                namespace=proposal.namespace,
                author_id=proposal.author_id,
                correlation_id=proposal.correlation_id,
                transcript_entry_id=proposal.transcript_entry_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
        return proposal

    def mark_committed(self, proposal_id: str) -> None:
        self._journal.update_state(
            proposal_id,
            PromotionJournalState.COMMITTED,
            details={"action": "commit"},
        )

    def mark_failed(self, proposal_id: str, error: str) -> None:
        self._journal.update_state(
            proposal_id,
            PromotionJournalState.FAILED,
            error=error,
            details={"action": "failure"},
        )

    def get_proposal(self, proposal_id: str) -> SharedPromotionProposal | None:
        return self._proposals.get(proposal_id)

    def get_replay_timeline(self, proposal_id: str) -> list[PromotionJournalEvent]:
        return self._journal.replay(proposal_id)

    def replay_session(self, session_id: str) -> list[PromotionJournalEvent]:
        return self._journal.replay_session(session_id)

    def get_forensics(self, proposal_id: str) -> dict[str, Any]:
        proposal = self._proposals.get(proposal_id)
        entry = self._journal.get(proposal_id)
        timeline = self._journal.replay(proposal_id)
        partial_commit = any(
            event.state
            in (
                PromotionJournalState.GRAPH_WRITTEN,
                PromotionJournalState.VECTOR_WRITTEN,
            )
            for event in timeline
        ) and (entry is not None and entry.state != PromotionJournalState.COMMITTED)
        return {
            "proposal": proposal.model_dump(mode="json") if proposal else None,
            "journal_entry": entry.model_dump(mode="json") if entry else None,
            "timeline": [event.model_dump(mode="json") for event in timeline],
            "partial_commit": partial_commit,
        }

    async def execute_promotion(
        self,
        memory: MemoryController,
        proposal_id: str,
    ) -> bool:
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            raise KeyError(f"unknown proposal_id: {proposal_id}")

        if self._arbitration is not None:
            decision = await self._arbitration.get_decision(proposal_id)
            if decision is None or decision == ArbitrationDecision.NEEDS_REVIEW:
                return False
            if decision == ArbitrationDecision.REJECTED:
                self.mark_failed(proposal_id, "arbitration rejected proposal")
                return False

        try:
            node = GraphNode(
                id=str(uuid.uuid4()),
                type="fact",
                label=proposal.fact,
                properties={
                    "namespace": SHARED_NAMESPACE,
                    "visibility": SHARED_VISIBILITY,
                    "source_namespace": proposal.namespace,
                    **proposal.metadata,
                },
                provenance=ProvenanceMetadata(
                    source_id=proposal.proposal_id,
                    source_type="agent",
                    author_id=proposal.author_id,
                    confidence=1.0,
                    created_at=datetime.now(timezone.utc),
                ),
            )
            await memory.store_fact(node)
            self._journal.update_state(
                proposal_id,
                PromotionJournalState.GRAPH_WRITTEN,
                details={"graph_node_id": node.id},
                promotion_id=node.id,
            )

            await memory.store_insight(
                proposal.fact,
                provenance=ProvenanceMetadata(
                    source_id=proposal.proposal_id,
                    source_type="agent",
                    author_id=proposal.author_id,
                    confidence=1.0,
                    created_at=datetime.now(timezone.utc),
                ),
                extra_metadata={
                    "namespace": SHARED_NAMESPACE,
                    "visibility": SHARED_VISIBILITY,
                    "source_namespace": proposal.namespace,
                },
            )
            self._journal.update_state(
                proposal_id,
                PromotionJournalState.VECTOR_WRITTEN,
                details={"vector_source_id": proposal.proposal_id},
                promotion_id=node.id,
            )
            self.mark_committed(proposal_id)
            return True
        except Exception as e:
            self.mark_failed(proposal_id, str(e))
            return False

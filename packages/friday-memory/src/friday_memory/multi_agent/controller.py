"""
Additive multi-agent memory controller.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from friday_core.interfaces import MultiAgentMemoryInterface, SharedWriteCapability

from friday_memory.controller import MemoryController
from friday_memory.models import ContextPayload, GraphNode, ProvenanceMetadata
from friday_memory.multi_agent.coordinator import PromotionCoordinator
from friday_memory.multi_agent.models import (
    PRIVATE_VISIBILITY,
    SHARED_NAMESPACE,
    SHARED_VISIBILITY,
)
from friday_memory.multi_agent.policy import NamespacePolicyEngine


class MultiAgentMemoryController(MultiAgentMemoryInterface):
    """
    Namespace-aware wrapper around `MemoryController`.
    """

    def __init__(
        self,
        memory: MemoryController,
        session_id: str,
        agent_id: str,
        namespace: str,
        policy: NamespacePolicyEngine | None = None,
        coordinator: PromotionCoordinator | None = None,
    ) -> None:
        self._memory = memory
        self._session_id = session_id
        self._agent_id = agent_id
        self._namespace = namespace
        self._policy = policy or NamespacePolicyEngine(session_id, agent_id, namespace)
        self._coordinator = coordinator

    async def set_namespace(self, namespace: str) -> None:
        self._namespace = namespace
        self._policy = NamespacePolicyEngine(
            self._session_id,
            self._agent_id,
            namespace,
        )

    async def recall(
        self, query: str, *, include_shared: bool = True, limit: int = 10
    ) -> dict[str, Any]:
        payload = await self._memory.recall(
            query=query,
            session_id=self._session_id,
            vector_results=limit,
        )
        filtered = self._filter_payload(payload, include_shared=include_shared)
        return filtered.model_dump()

    async def write_private_fact(
        self, fact: str, metadata: dict[str, Any] | None = None
    ) -> str:
        allowed = await self._policy.can_write_private(
            actor_id=self._agent_id,
            namespace=self._namespace,
            session_id=self._session_id,
        )
        if not allowed:
            raise PermissionError("private write denied by namespace policy")

        node_id = str(uuid.uuid4())
        node = GraphNode(
            id=node_id,
            type="fact",
            label=fact,
            properties={
                "namespace": self._namespace,
                "visibility": PRIVATE_VISIBILITY,
                "agent_id": self._agent_id,
                **(metadata or {}),
            },
            provenance=ProvenanceMetadata(
                source_id=node_id,
                source_type="agent",
                author_id=self._agent_id,
                confidence=1.0,
                created_at=datetime.now(timezone.utc),
            ),
        )
        await self._memory.store_fact(node)
        return node_id

    async def submit_shared_promotion(
        self, fact: str, metadata: dict[str, Any] | None = None
    ) -> str:
        if self._coordinator is None:
            raise RuntimeError("shared promotion is unavailable without coordinator")
        proposal = self._coordinator.create_proposal(
            session_id=self._session_id,
            namespace=self._namespace,
            author_id=self._agent_id,
            fact=fact,
            metadata=metadata or {},
        )
        return proposal.proposal_id

    async def write_shared_fact(
        self,
        fact: str,
        capability: SharedWriteCapability | None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        allowed = await self._policy.can_write_shared(
            actor_id=self._agent_id,
            session_id=self._session_id,
            capability=capability,
        )
        if not allowed:
            raise PermissionError("shared write denied by namespace policy")

        node_id = str(uuid.uuid4())
        node = GraphNode(
            id=node_id,
            type="fact",
            label=fact,
            properties={
                "namespace": SHARED_NAMESPACE,
                "visibility": SHARED_VISIBILITY,
                "agent_id": self._agent_id,
                **(metadata or {}),
            },
            provenance=ProvenanceMetadata(
                source_id=node_id,
                source_type="agent",
                author_id=self._agent_id,
                confidence=1.0,
                created_at=datetime.now(timezone.utc),
            ),
        )
        await self._memory.store_fact(node)
        return node_id

    def _filter_payload(
        self, payload: ContextPayload, *, include_shared: bool
    ) -> ContextPayload:
        def _is_visible(meta: dict[str, Any]) -> bool:
            visibility = meta.get("visibility")
            namespace = meta.get("namespace")
            if namespace == self._namespace:
                return True
            return include_shared and (
                visibility == SHARED_VISIBILITY or namespace == SHARED_NAMESPACE
            )

        filtered_passages = [
            item for item in payload.passages if _is_visible(item.get("metadata", {}))
        ]
        filtered_entities = [
            node for node in payload.entities if _is_visible(node.properties)
        ]
        filtered_facts = [
            edge for edge in payload.facts if _is_visible(edge.properties)
        ]

        return payload.model_copy(
            update={
                "passages": filtered_passages,
                "entities": filtered_entities,
                "facts": filtered_facts,
            }
        )

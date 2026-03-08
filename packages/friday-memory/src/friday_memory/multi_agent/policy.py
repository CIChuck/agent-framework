# mypy: ignore-errors
"""
Namespace policy engine for additive multi-agent memory mode.
"""

from __future__ import annotations

from datetime import datetime, timezone

from friday_core.interfaces import NamespacePolicyInterface, SharedWriteCapability

from friday_memory.multi_agent.models import SHARED_NAMESPACE


class NamespacePolicyEngine(NamespacePolicyInterface):
    """
    Minimal policy implementation for namespace-scoped read/write checks.
    """

    def __init__(self, session_id: str, actor_id: str, namespace: str) -> None:
        self._session_id = session_id
        self._actor_id = actor_id
        self._namespace = namespace

    async def can_read(
        self,
        actor_id: str,
        namespace: str,
        session_id: str,
    ) -> bool:
        if session_id != self._session_id:
            return False
        if namespace == SHARED_NAMESPACE:
            return True
        return actor_id == self._actor_id and namespace == self._namespace

    async def can_write_private(
        self,
        actor_id: str,
        namespace: str,
        session_id: str,
    ) -> bool:
        return (
            actor_id == self._actor_id
            and namespace == self._namespace
            and session_id == self._session_id
        )

    async def can_write_shared(
        self,
        actor_id: str,
        session_id: str,
        capability: SharedWriteCapability | None,
    ) -> bool:
        if actor_id != self._actor_id or session_id != self._session_id:
            return False
        return self._capability_is_valid(capability)

    @staticmethod
    def _capability_is_valid(capability: SharedWriteCapability | None) -> bool:
        if capability is None:
            return False
        now = datetime.now(timezone.utc)
        issued_at = capability.issued_at
        expires_at = capability.expires_at
        if issued_at.tzinfo is None:
            issued_at = issued_at.replace(tzinfo=timezone.utc)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return issued_at <= now < expires_at

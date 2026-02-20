"""
Skill reference validation and catalog helpers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

SKILL_REF_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*@[a-zA-Z0-9][a-zA-Z0-9._-]*$")


def is_valid_skill_ref(skill_ref: str) -> bool:
    """Return True when skill reference matches `skill_id@version` format."""
    return bool(SKILL_REF_PATTERN.match(skill_ref))


def validate_skill_ref(skill_ref: str) -> str:
    """Validate and normalize skill reference."""
    normalized = skill_ref.strip()
    if not is_valid_skill_ref(normalized):
        raise ValueError(
            f"Invalid skill reference '{skill_ref}'. Expected format: skill_id@version"
        )
    return normalized


@dataclass(frozen=True)
class SkillCatalogEntry:
    """Catalog entry for a resolved skill reference."""

    skill_ref: str
    source: str = "local"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized = validate_skill_ref(self.skill_ref)
        object.__setattr__(self, "skill_ref", normalized)


class SkillCatalog:
    """Local + federated skill catalog with strict skill-ref semantics."""

    def __init__(self) -> None:
        self._local: dict[str, SkillCatalogEntry] = {}
        self._federated: dict[str, dict[str, SkillCatalogEntry]] = {}

    def register_local(
        self, skill_ref: str, metadata: dict[str, Any] | None = None
    ) -> SkillCatalogEntry:
        entry = SkillCatalogEntry(
            skill_ref=skill_ref,
            source="local",
            metadata=metadata or {},
        )
        self._local[entry.skill_ref] = entry
        return entry

    def sync_federated_catalog(
        self,
        catalog_name: str,
        entries: list[str | SkillCatalogEntry],
        *,
        replace: bool = True,
    ) -> int:
        if replace or catalog_name not in self._federated:
            self._federated[catalog_name] = {}

        for raw in entries:
            entry = (
                raw
                if isinstance(raw, SkillCatalogEntry)
                else SkillCatalogEntry(
                    skill_ref=raw,
                    source=f"federated:{catalog_name}",
                )
            )
            self._federated[catalog_name][entry.skill_ref] = entry

        return len(self._federated[catalog_name])

    def resolve(self, skill_ref: str) -> SkillCatalogEntry | None:
        normalized = validate_skill_ref(skill_ref)
        if normalized in self._local:
            return self._local[normalized]
        for catalog in self._federated.values():
            if normalized in catalog:
                return catalog[normalized]
        return None

    def has_skill(self, skill_ref: str) -> bool:
        return self.resolve(skill_ref) is not None

    def list_skill_refs(self, include_federated: bool = True) -> list[str]:
        refs = set(self._local.keys())
        if include_federated:
            for catalog in self._federated.values():
                refs.update(catalog.keys())
        return sorted(refs)

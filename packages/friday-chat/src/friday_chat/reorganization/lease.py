"""Darwin-verified inter-process lease registry for maintenance layouts."""

from __future__ import annotations

import errno
import os
import platform
import re
import socket
import stat
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Protocol, cast
from uuid import uuid4

from pydantic import ValidationError

from friday_chat.reorganization.artifacts import MaintenanceArtifactStore
from friday_chat.reorganization.contracts import (
    JournalState,
    LayoutLeaseRecord,
    OperationTrigger,
    RecoveryJournal,
)
from friday_chat.reorganization.durability import (
    AtomicJsonStore,
    DurableArtifactError,
    ensure_owner_directory,
)
from friday_chat.reorganization.layout import (
    FridayChatMaintenanceLayout,
    MaintenanceLayoutError,
    live_targets_overlap,
    validate_declared_paths,
    validate_live_target_identities,
)


class _FcntlApi(Protocol):
    LOCK_EX: int
    LOCK_NB: int
    LOCK_UN: int

    def flock(self, descriptor: int, operation: int) -> None: ...


class _PasswdEntry(Protocol):
    pw_dir: str


class _PwdApi(Protocol):
    def getpwuid(self, user_id: int) -> _PasswdEntry: ...


try:
    import fcntl as _loaded_fcntl
except ImportError:  # pragma: no cover - exercised by platform capability tests
    _fcntl: _FcntlApi | None = None
else:
    _fcntl = cast(_FcntlApi, _loaded_fcntl)

try:
    import pwd as _loaded_pwd
except ImportError:  # pragma: no cover - exercised by platform capability tests
    _pwd: _PwdApi | None = None
else:
    _pwd = cast(_PwdApi, _loaded_pwd)


MAX_LEASE_BYTES = 1024 * 1024
MAX_REGISTRY_ENTRIES = 1024
MAX_REGISTRY_FILENAME_BYTES = 255
REGISTRY_LOCK_NAME = "registry.lock"


class _EvidenceKind(str, Enum):
    STALE_OWNER = "stale"
    UNFINISHED_RELEASE = "unfinished"


@dataclass(frozen=True)
class _EvidenceLease:
    kind: _EvidenceKind
    name: str
    record: LayoutLeaseRecord


@dataclass(frozen=True)
class _RegistryLease:
    name: str
    record: LayoutLeaseRecord


class MaintenancePlatformError(RuntimeError):
    """Raised before mutation when durable lease semantics are unverified."""


class LayoutLeaseError(RuntimeError):
    """Content-safe base error for lease acquisition and ownership failures."""


class LayoutLeaseContentionError(LayoutLeaseError):
    """Raised when an active or stale layout overlaps the requested targets."""


class StaleLeaseReconciliationError(LayoutLeaseError):
    """Raised when explicit stale reconciliation cannot be proven safe."""


class LayoutLeaseHandle:
    """Process-owned lease descriptor retained until verified release."""

    def __init__(
        self,
        registry: DarwinLayoutLeaseRegistry,
        record: LayoutLeaseRecord,
        path: Path,
        descriptor: int,
    ) -> None:
        self._registry = registry
        self.record = record
        self.path = path
        self._descriptor = descriptor
        self._released = False

    def release(self) -> None:
        """Verify ownership and durably remove this active lease."""
        self._registry.release(self)

    def __enter__(self) -> LayoutLeaseHandle:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.release()


class DarwinLayoutLeaseRegistry:
    """Serialize overlap checks in a recovery-root-independent namespace."""

    def __init__(
        self,
        *,
        namespace_root: Path | None = None,
        platform_name: str | None = None,
        host_id: str | None = None,
    ) -> None:
        self._platform_name = platform_name or platform.system()
        self._host_id = host_id or socket.gethostname()
        self._user_id = os.getuid() if hasattr(os, "getuid") else -1
        self._namespace_root = namespace_root or self._production_namespace()

    @property
    def namespace_root(self) -> Path:
        return self._namespace_root

    def lease_path(self, layout: FridayChatMaintenanceLayout) -> Path:
        return self._namespace_root / self._lease_name(layout.layout_fingerprint)

    def validate_capability(self, layout: FridayChatMaintenanceLayout) -> None:
        """Read-only platform and current-layout capability validation."""
        self._ensure_darwin_capability()
        self._revalidate_layout(layout)

    def acquire(
        self,
        layout: FridayChatMaintenanceLayout,
        journal: RecoveryJournal,
    ) -> LayoutLeaseHandle:
        """Acquire without ever stealing an existing active or stale lease."""
        self._ensure_darwin_capability()
        self._revalidate_layout(layout)
        self._validate_new_lease_journal(layout, journal)
        with self._registry_guard() as namespace_descriptor:
            for existing in self._scan_active_leases(namespace_descriptor):
                if live_targets_overlap(existing.live_targets, layout.live_targets):
                    raise LayoutLeaseContentionError(
                        "maintenance layout is already leased"
                    )
            for evidence in self._scan_evidence_leases(namespace_descriptor):
                if not live_targets_overlap(
                    evidence.record.live_targets,
                    layout.live_targets,
                ):
                    continue
                if not self._evidence_has_verified_terminal_journal(evidence):
                    raise LayoutLeaseContentionError(
                        "maintenance layout has retained recovery evidence"
                    )
            record = self._new_record(layout, journal)
            descriptor = self._create_active_lease(
                namespace_descriptor,
                self._lease_name(layout.layout_fingerprint),
                record,
            )
            return LayoutLeaseHandle(
                self,
                record,
                self.lease_path(layout),
                descriptor,
            )

    def reconcile_stale(
        self,
        layout: FridayChatMaintenanceLayout,
        journal: RecoveryJournal,
    ) -> LayoutLeaseHandle:
        """Replace an exact stale lease only after inode and journal proof."""
        self._ensure_darwin_capability()
        self._revalidate_layout(layout)
        lease_name = self._lease_name(layout.layout_fingerprint)
        try:
            with self._registry_guard() as namespace_descriptor:
                if self._named_file_exists(namespace_descriptor, lease_name):
                    replacement, replacement_descriptor = (
                        self._replace_stale_active_lease(
                            namespace_descriptor,
                            lease_name,
                            layout,
                            journal,
                        )
                    )
                else:
                    replacement, replacement_descriptor = (
                        self._resume_from_retained_evidence(
                            namespace_descriptor,
                            lease_name,
                            layout,
                            journal,
                        )
                    )
        except StaleLeaseReconciliationError:
            raise
        except (
            OSError,
            DurableArtifactError,
            LayoutLeaseError,
            ValidationError,
        ) as exc:
            raise StaleLeaseReconciliationError(
                "stale lease reconciliation failed closed"
            ) from exc
        return LayoutLeaseHandle(
            self,
            replacement,
            self.lease_path(layout),
            replacement_descriptor,
        )

    def retire_terminal_lease(
        self,
        layout: FridayChatMaintenanceLayout,
        journal: RecoveryJournal,
    ) -> None:
        """Explicitly retire a dead lease after its exact journal is complete."""
        self._ensure_darwin_capability()
        self._revalidate_layout(layout)
        self._validate_linked_journal(layout, journal)
        if journal.state is not JournalState.COMPLETE:
            raise StaleLeaseReconciliationError(
                "only a complete journal can authorize terminal lease retirement"
            )
        lease_name = self._lease_name(layout.layout_fingerprint)
        try:
            with self._registry_guard() as namespace_descriptor:
                entries = [
                    entry
                    for entry in self._scan_active_entries(namespace_descriptor)
                    if self._record_matches_layout(entry.record, layout)
                    and self._record_links_journal(entry.record, journal)
                ]
                if not entries:
                    evidence = [
                        item
                        for item in self._scan_evidence_leases(namespace_descriptor)
                        if self._record_matches_layout(item.record, layout)
                        and self._record_links_journal(item.record, journal)
                    ]
                    if len(evidence) != 1:
                        raise StaleLeaseReconciliationError(
                            "terminal lease evidence is absent or ambiguous"
                        )
                    return
                if len(entries) not in {1, 2}:
                    raise StaleLeaseReconciliationError(
                        "terminal release state is ambiguous"
                    )
                record = entries[0].record
                pending_name = self._release_pending_name(record)
                expected_names = {lease_name, pending_name}
                entry_names = {entry.name for entry in entries}
                if not entry_names.issubset(expected_names) or any(
                    entry.record != record for entry in entries
                ):
                    raise StaleLeaseReconciliationError(
                        "terminal release state does not match"
                    )
                if len(entries) == 2:
                    left = os.stat(
                        entries[0].name,
                        dir_fd=namespace_descriptor,
                        follow_symlinks=False,
                    )
                    right = os.stat(
                        entries[1].name,
                        dir_fd=namespace_descriptor,
                        follow_symlinks=False,
                    )
                    if (left.st_dev, left.st_ino) != (right.st_dev, right.st_ino):
                        raise StaleLeaseReconciliationError(
                            "terminal release links do not share an inode"
                        )
                source_name = entries[0].name
                descriptor = self._open_active_lease(
                    namespace_descriptor,
                    source_name,
                )
                try:
                    self._lock_stale_inode(descriptor)
                    existing = self._read_lease_descriptor(descriptor)
                    if not self._record_matches_layout(
                        existing, layout
                    ) or not self._record_links_journal(existing, journal):
                        raise StaleLeaseReconciliationError(
                            "terminal lease identity does not match"
                        )
                    active_only = entry_names == {lease_name}
                    if active_only and (
                        existing.host_id != self._host_id
                        or not self._pid_is_proven_dead(existing.process_id)
                    ):
                        raise StaleLeaseReconciliationError(
                            "terminal lease ownership is active or ambiguous"
                        )
                    evidence_descriptor = self._open_evidence_kind_directory(
                        _EvidenceKind.STALE_OWNER,
                        create=True,
                    )
                    if evidence_descriptor is None:
                        raise LayoutLeaseError(
                            "maintenance evidence directory is unavailable"
                        )
                    try:
                        evidence_name = self._evidence_name(existing)
                        self._ensure_evidence_link(
                            namespace_descriptor,
                            source_name,
                            evidence_descriptor,
                            evidence_name,
                        )
                        for entry_name in sorted(entry_names):
                            os.unlink(entry_name, dir_fd=namespace_descriptor)
                        os.fsync(namespace_descriptor)
                    finally:
                        os.close(evidence_descriptor)
                finally:
                    if _fcntl is not None:
                        with suppress(OSError):
                            _fcntl.flock(descriptor, _fcntl.LOCK_UN)
                    os.close(descriptor)
        except StaleLeaseReconciliationError:
            raise
        except (
            OSError,
            DurableArtifactError,
            LayoutLeaseError,
            ValidationError,
        ) as exc:
            raise StaleLeaseReconciliationError(
                "terminal lease retirement failed closed"
            ) from exc

    def release(self, handle: LayoutLeaseHandle) -> None:
        """Durably release, retaining evidence for every unfinished journal."""
        self._ensure_darwin_capability()
        if handle._released:
            raise LayoutLeaseError("maintenance lease is already released")
        lease_name = handle.path.name
        try:
            with self._registry_guard() as namespace_descriptor:
                held_info = os.fstat(handle._descriptor)
                if not stat.S_ISREG(held_info.st_mode):
                    raise LayoutLeaseError("maintenance lease identity changed")
                persisted = self._read_lease_descriptor(handle._descriptor)
                if persisted != handle.record:
                    raise LayoutLeaseError("maintenance lease ownership changed")
                linked_journal = self._read_record_journal(persisted)
                if self._journal_requires_retained_evidence(linked_journal):
                    retained_evidence = [
                        evidence
                        for evidence in self._scan_evidence_leases(namespace_descriptor)
                        if self._records_share_layout(
                            evidence.record,
                            persisted,
                        )
                        and self._record_links_journal(
                            evidence.record,
                            linked_journal,
                        )
                    ]
                    current_retained = any(
                        evidence.record == persisted for evidence in retained_evidence
                    )
                    historical_retained = any(
                        evidence.record != persisted for evidence in retained_evidence
                    )
                    if current_retained:
                        self._finish_unfinished_release(
                            namespace_descriptor,
                            lease_name,
                            persisted,
                            held_info,
                        )
                    elif historical_retained:
                        self._finish_exceptional_unlink(
                            namespace_descriptor,
                            lease_name,
                            persisted,
                            held_info,
                        )
                    else:
                        self._finish_unfinished_release(
                            namespace_descriptor,
                            lease_name,
                            persisted,
                            held_info,
                        )
                else:
                    self._finish_exceptional_unlink(
                        namespace_descriptor,
                        lease_name,
                        persisted,
                        held_info,
                    )
        except (OSError, LayoutLeaseError) as exc:
            raise LayoutLeaseError("maintenance lease release failed closed") from exc
        if _fcntl is not None:
            _fcntl.flock(handle._descriptor, _fcntl.LOCK_UN)
        os.close(handle._descriptor)
        handle._released = True

    def _new_record(
        self,
        layout: FridayChatMaintenanceLayout,
        journal: RecoveryJournal,
        *,
        lease_id: str | None = None,
    ) -> LayoutLeaseRecord:
        return LayoutLeaseRecord(
            lease_id=lease_id or journal.lease_id,
            ownership_nonce=uuid4().hex,
            journal_lease_nonce=journal.lease_nonce,
            run_id=journal.run_id,
            process_id=os.getpid(),
            user_id=self._user_id,
            host_id=self._host_id,
            application_id=journal.application_id,
            application_version=journal.application_version,
            layout_fingerprint=layout.layout_fingerprint,
            live_targets=layout.live_targets,
            recovery_root=layout.recovery_root,
            log_root=layout.log_root,
            journal_id=journal.journal_id,
            journal_path=journal.journal_path,
            created_at=datetime.now(timezone.utc),
        )

    def _validate_linked_journal(
        self,
        layout: FridayChatMaintenanceLayout,
        journal: RecoveryJournal,
    ) -> None:
        store = MaintenanceArtifactStore(layout)
        persisted, _ = store.read_journal(journal.journal_path)
        if persisted != journal:
            raise LayoutLeaseError("durable journal does not match lease request")

    def _validate_new_lease_journal(
        self,
        layout: FridayChatMaintenanceLayout,
        journal: RecoveryJournal,
    ) -> None:
        self._validate_linked_journal(layout, journal)
        if (
            journal.trigger is OperationTrigger.RECOVERY
            or journal.state is not JournalState.CREATED
            or journal.revision != 0
            or journal.state_history != (JournalState.CREATED,)
        ):
            raise LayoutLeaseError(
                "new maintenance lease requires an initial ordinary journal"
            )

    def _read_record_journal(self, record: LayoutLeaseRecord) -> RecoveryJournal:
        try:
            relative_path = record.journal_path.relative_to(record.recovery_root)
            journal, _ = AtomicJsonStore(record.recovery_root).read_model(
                relative_path,
                RecoveryJournal,
            )
        except (ValueError, DurableArtifactError) as exc:
            raise LayoutLeaseError("retained lease journal cannot be verified") from exc
        if not self._record_links_journal(record, journal):
            raise LayoutLeaseError("retained lease journal linkage is invalid")
        return journal

    @staticmethod
    def _record_links_journal(
        lease: LayoutLeaseRecord,
        journal: RecoveryJournal,
    ) -> bool:
        expected = (
            journal.lease_id,
            journal.lease_nonce,
            journal.run_id,
            journal.application_id,
            journal.application_version,
            journal.layout_fingerprint,
            journal.recovery_root,
            journal.journal_id,
            journal.journal_path,
        )
        actual = (
            lease.lease_id,
            lease.journal_lease_nonce,
            lease.run_id,
            lease.application_id,
            lease.application_version,
            lease.layout_fingerprint,
            lease.recovery_root,
            lease.journal_id,
            lease.journal_path,
        )
        return actual == expected

    @staticmethod
    def _journal_requires_retained_evidence(journal: RecoveryJournal) -> bool:
        return journal.state is not JournalState.COMPLETE

    def _evidence_has_verified_terminal_journal(
        self,
        evidence: _EvidenceLease,
    ) -> bool:
        try:
            journal = self._read_record_journal(evidence.record)
        except LayoutLeaseError:
            return False
        return journal.state is JournalState.COMPLETE

    def _validate_stale_journal_link(
        self,
        layout: FridayChatMaintenanceLayout,
        journal: RecoveryJournal,
        lease: LayoutLeaseRecord,
    ) -> None:
        self._validate_linked_journal(layout, journal)
        if journal.state is JournalState.COMPLETE:
            raise StaleLeaseReconciliationError(
                "completed journal cannot authorize stale recovery"
            )
        if not self._record_links_journal(lease, journal):
            raise StaleLeaseReconciliationError(
                "stale lease journal linkage does not match"
            )

    def _replace_stale_active_lease(
        self,
        namespace_descriptor: int,
        lease_name: str,
        layout: FridayChatMaintenanceLayout,
        journal: RecoveryJournal,
    ) -> tuple[LayoutLeaseRecord, int]:
        descriptor = self._open_active_lease(namespace_descriptor, lease_name)
        try:
            self._lock_stale_inode(descriptor)
            existing = self._read_lease_descriptor(descriptor)
            if not self._record_matches_layout(existing, layout):
                raise StaleLeaseReconciliationError(
                    "stale lease does not match the requested layout"
                )
            if existing.host_id != self._host_id or not self._pid_is_proven_dead(
                existing.process_id
            ):
                raise StaleLeaseReconciliationError(
                    "stale lease ownership is active or ambiguous"
                )
            self._validate_stale_journal_link(layout, journal, existing)
            evidence_descriptor = self._open_evidence_kind_directory(
                _EvidenceKind.STALE_OWNER,
                create=True,
            )
            if evidence_descriptor is None:
                raise LayoutLeaseError("maintenance evidence directory is unavailable")
            try:
                evidence_name = self._evidence_name(existing)
                self._assert_name_absent(evidence_descriptor, evidence_name)
                os.rename(
                    lease_name,
                    evidence_name,
                    src_dir_fd=namespace_descriptor,
                    dst_dir_fd=evidence_descriptor,
                )
                os.fsync(evidence_descriptor)
                os.fsync(namespace_descriptor)
            finally:
                os.close(evidence_descriptor)
            self._after_evidence_rename()
            replacement = self._new_record(
                layout,
                journal,
                lease_id=existing.lease_id,
            )
            replacement_descriptor = self._create_active_lease(
                namespace_descriptor,
                lease_name,
                replacement,
            )
            return replacement, replacement_descriptor
        finally:
            if _fcntl is not None:
                with suppress(OSError):
                    _fcntl.flock(descriptor, _fcntl.LOCK_UN)
            os.close(descriptor)

    def _resume_from_retained_evidence(
        self,
        namespace_descriptor: int,
        lease_name: str,
        layout: FridayChatMaintenanceLayout,
        journal: RecoveryJournal,
    ) -> tuple[LayoutLeaseRecord, int]:
        candidates = [
            evidence
            for evidence in self._scan_evidence_leases(namespace_descriptor)
            if self._record_matches_layout(evidence.record, layout)
            and self._record_links_journal(evidence.record, journal)
        ]
        if len(candidates) != 1:
            raise StaleLeaseReconciliationError(
                "exact retained lease evidence is absent or ambiguous"
            )
        evidence = candidates[0]
        evidence_descriptor = self._open_evidence_kind_directory(
            evidence.kind,
            create=False,
        )
        if evidence_descriptor is None:
            raise StaleLeaseReconciliationError("retained lease evidence disappeared")
        descriptor: int | None = None
        try:
            descriptor = self._open_active_lease(
                evidence_descriptor,
                evidence.name,
            )
            self._lock_stale_inode(descriptor)
            existing = self._read_lease_descriptor(descriptor)
            if existing != evidence.record:
                raise StaleLeaseReconciliationError(
                    "retained lease evidence identity changed"
                )
            if evidence.kind is _EvidenceKind.STALE_OWNER and (
                existing.host_id != self._host_id
                or not self._pid_is_proven_dead(existing.process_id)
            ):
                raise StaleLeaseReconciliationError(
                    "stale lease ownership is active or ambiguous"
                )
            self._validate_stale_journal_link(layout, journal, existing)
            replacement = self._new_record(
                layout,
                journal,
                lease_id=existing.lease_id,
            )
            replacement_descriptor = self._create_active_lease(
                namespace_descriptor,
                lease_name,
                replacement,
            )
            return replacement, replacement_descriptor
        finally:
            if descriptor is not None:
                if _fcntl is not None:
                    with suppress(OSError):
                        _fcntl.flock(descriptor, _fcntl.LOCK_UN)
                os.close(descriptor)
            os.close(evidence_descriptor)

    def _after_evidence_rename(self) -> None:
        """Fault-injection boundary after durable evidence retention."""

    @staticmethod
    def _named_file_exists(directory_descriptor: int, name: str) -> bool:
        try:
            info = os.stat(
                name,
                dir_fd=directory_descriptor,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            return False
        except OSError as exc:
            raise LayoutLeaseError("maintenance lease identity is unavailable") from exc
        if not stat.S_ISREG(info.st_mode):
            raise LayoutLeaseError("maintenance lease identity is unsafe")
        return True

    @staticmethod
    def _assert_name_absent(directory_descriptor: int, name: str) -> None:
        try:
            os.stat(
                name,
                dir_fd=directory_descriptor,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            return
        except OSError as exc:
            raise LayoutLeaseError("maintenance evidence identity is unsafe") from exc
        raise LayoutLeaseError("maintenance evidence already exists")

    @staticmethod
    def _evidence_name(record: LayoutLeaseRecord) -> str:
        return f"{record.layout_fingerprint}.{record.ownership_nonce}.lease.json"

    @staticmethod
    def _release_pending_name(record: LayoutLeaseRecord) -> str:
        return (
            f"release-pending-{record.layout_fingerprint}."
            f"{record.ownership_nonce}.lease.json"
        )

    @staticmethod
    def _ensure_evidence_link(
        namespace_descriptor: int,
        source_name: str,
        evidence_descriptor: int,
        evidence_name: str,
    ) -> None:
        source_info = os.stat(
            source_name,
            dir_fd=namespace_descriptor,
            follow_symlinks=False,
        )
        try:
            evidence_info = os.stat(
                evidence_name,
                dir_fd=evidence_descriptor,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            os.link(
                source_name,
                evidence_name,
                src_dir_fd=namespace_descriptor,
                dst_dir_fd=evidence_descriptor,
                follow_symlinks=False,
            )
            os.fsync(evidence_descriptor)
            return
        if (source_info.st_dev, source_info.st_ino) != (
            evidence_info.st_dev,
            evidence_info.st_ino,
        ):
            raise StaleLeaseReconciliationError(
                "terminal evidence inode does not match"
            )

    def _finish_unfinished_release(
        self,
        namespace_descriptor: int,
        lease_name: str,
        record: LayoutLeaseRecord,
        held_info: os.stat_result,
    ) -> None:
        evidence_descriptor = self._open_evidence_kind_directory(
            _EvidenceKind.UNFINISHED_RELEASE,
            create=True,
        )
        if evidence_descriptor is None:
            raise LayoutLeaseError("maintenance evidence directory is unavailable")
        try:
            evidence_name = self._evidence_name(record)
            active_exists = self._verify_optional_named_inode(
                namespace_descriptor,
                lease_name,
                held_info,
            )
            evidence_exists = self._verify_optional_named_inode(
                evidence_descriptor,
                evidence_name,
                held_info,
            )
            if active_exists and evidence_exists:
                raise LayoutLeaseError("unfinished release identity is ambiguous")
            if active_exists:
                os.rename(
                    lease_name,
                    evidence_name,
                    src_dir_fd=namespace_descriptor,
                    dst_dir_fd=evidence_descriptor,
                )
            elif not evidence_exists:
                raise LayoutLeaseError("unfinished release identity is unavailable")
            os.fsync(evidence_descriptor)
            self._after_unfinished_release_durability("evidence_fsynced")
            os.fsync(namespace_descriptor)
            self._after_unfinished_release_durability("namespace_fsynced")
        finally:
            os.close(evidence_descriptor)

    def _after_unfinished_release_durability(self, phase: str) -> None:
        """Fault-injection boundary for idempotent unfinished retention."""
        del phase

    def _finish_exceptional_unlink(
        self,
        namespace_descriptor: int,
        lease_name: str,
        record: LayoutLeaseRecord,
        held_info: os.stat_result,
    ) -> None:
        evidence_descriptor = self._open_evidence_kind_directory(
            _EvidenceKind.STALE_OWNER,
            create=True,
        )
        if evidence_descriptor is None:
            raise LayoutLeaseError("maintenance evidence directory is unavailable")
        evidence_name = self._evidence_name(record)
        pending_name = self._release_pending_name(record)
        try:
            active_exists = self._verify_optional_named_inode(
                namespace_descriptor,
                lease_name,
                held_info,
            )
            pending_exists = self._verify_optional_named_inode(
                namespace_descriptor,
                pending_name,
                held_info,
            )
            evidence_exists = self._verify_optional_named_inode(
                evidence_descriptor,
                evidence_name,
                held_info,
            )
            if not any((active_exists, pending_exists, evidence_exists)):
                raise LayoutLeaseError("release identity is unavailable")
            if not evidence_exists:
                source_name = lease_name if active_exists else pending_name
                self._ensure_evidence_link(
                    namespace_descriptor,
                    source_name,
                    evidence_descriptor,
                    evidence_name,
                )
            if active_exists:
                if not pending_exists:
                    os.link(
                        lease_name,
                        pending_name,
                        src_dir_fd=namespace_descriptor,
                        dst_dir_fd=namespace_descriptor,
                        follow_symlinks=False,
                    )
                    self._fsync_release_directory(
                        namespace_descriptor,
                        "pending_created",
                    )
                else:
                    os.fsync(namespace_descriptor)
                os.unlink(lease_name, dir_fd=namespace_descriptor)
                self._fsync_release_directory(
                    namespace_descriptor,
                    "active_unlinked",
                )
            else:
                os.fsync(namespace_descriptor)
            if self._verify_optional_named_inode(
                namespace_descriptor,
                pending_name,
                held_info,
            ):
                os.unlink(pending_name, dir_fd=namespace_descriptor)
                self._fsync_release_directory(
                    namespace_descriptor,
                    "pending_unlinked",
                )
            else:
                os.fsync(namespace_descriptor)
            os.unlink(evidence_name, dir_fd=evidence_descriptor)
            os.fsync(evidence_descriptor)
        finally:
            os.close(evidence_descriptor)

    @staticmethod
    def _verify_optional_named_inode(
        directory_descriptor: int,
        name: str,
        held_info: os.stat_result,
    ) -> bool:
        try:
            info = os.stat(
                name,
                dir_fd=directory_descriptor,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            return False
        if not stat.S_ISREG(info.st_mode) or (info.st_dev, info.st_ino) != (
            held_info.st_dev,
            held_info.st_ino,
        ):
            raise LayoutLeaseError("release inode identity changed")
        return True

    @staticmethod
    def _fsync_release_directory(
        namespace_descriptor: int,
        phase: str,
    ) -> None:
        del phase
        os.fsync(namespace_descriptor)

    def _revalidate_layout(self, layout: FridayChatMaintenanceLayout) -> None:
        try:
            validated = FridayChatMaintenanceLayout.model_validate(
                layout.model_dump(mode="python")
            )
            validate_live_target_identities(validated.live_targets)
            validate_declared_paths(validated.all_declared_paths)
        except (ValidationError, MaintenanceLayoutError) as exc:
            raise LayoutLeaseError("maintenance layout identity is unsafe") from exc

    def _scan_active_leases(self, namespace_descriptor: int) -> list[LayoutLeaseRecord]:
        return [
            entry.record for entry in self._scan_active_entries(namespace_descriptor)
        ]

    def _scan_active_entries(
        self,
        namespace_descriptor: int,
    ) -> list[_RegistryLease]:
        entries: list[_RegistryLease] = []
        for name in self._bounded_directory_names(namespace_descriptor):
            if name in {REGISTRY_LOCK_NAME, "evidence"}:
                continue
            if not (
                re.fullmatch(r"active-[0-9a-f]{64}\.lease\.json", name)
                or re.fullmatch(
                    r"release-pending-[0-9a-f]{64}\.[0-9a-f]{32}\.lease\.json",
                    name,
                )
            ):
                raise LayoutLeaseError(
                    "maintenance lease registry contains unexpected state"
                )
            try:
                descriptor = self._open_active_lease(namespace_descriptor, name)
                try:
                    record = self._read_lease_descriptor(descriptor)
                finally:
                    os.close(descriptor)
                validate_live_target_identities(record.live_targets)
                validate_declared_paths(
                    (
                        *(target.path for target in record.live_targets),
                        record.recovery_root,
                        record.log_root,
                    )
                )
                validate_declared_paths((record.journal_path,))
                entries.append(_RegistryLease(name=name, record=record))
            except (OSError, ValidationError, MaintenanceLayoutError) as exc:
                raise LayoutLeaseError(
                    "maintenance lease registry contains invalid active state"
                ) from exc
        return entries

    def _scan_evidence_leases(
        self,
        namespace_descriptor: int,
    ) -> list[_EvidenceLease]:
        evidence_root = self._namespace_root / "evidence"
        try:
            root_info = evidence_root.lstat()
        except FileNotFoundError:
            return []
        except OSError as exc:
            raise LayoutLeaseError("maintenance evidence cannot be inspected") from exc
        if not stat.S_ISDIR(root_info.st_mode) or stat.S_ISLNK(root_info.st_mode):
            raise LayoutLeaseError("maintenance evidence root is unsafe")
        root_descriptor = self._open_directory(evidence_root)
        try:
            root_names = self._bounded_directory_names(root_descriptor)
            allowed_names = {kind.value for kind in _EvidenceKind}
            if any(name not in allowed_names for name in root_names):
                raise LayoutLeaseError(
                    "maintenance evidence registry contains invalid state"
                )
        finally:
            os.close(root_descriptor)

        evidence_leases: list[_EvidenceLease] = []
        for kind in _EvidenceKind:
            directory_descriptor = self._open_evidence_kind_directory(
                kind,
                create=False,
            )
            if directory_descriptor is None:
                continue
            try:
                for name in self._bounded_directory_names(directory_descriptor):
                    if not re.fullmatch(
                        r"[0-9a-f]{64}\.[0-9a-f]{32}\.lease\.json",
                        name,
                    ):
                        raise LayoutLeaseError(
                            "maintenance evidence registry contains invalid state"
                        )
                    descriptor = self._open_active_lease(
                        directory_descriptor,
                        name,
                    )
                    try:
                        record = self._read_lease_descriptor(descriptor)
                    finally:
                        os.close(descriptor)
                    try:
                        validate_live_target_identities(record.live_targets)
                        validate_declared_paths(
                            (
                                *(target.path for target in record.live_targets),
                                record.recovery_root,
                                record.log_root,
                            )
                        )
                        validate_declared_paths((record.journal_path,))
                    except MaintenanceLayoutError as exc:
                        raise LayoutLeaseError(
                            "maintenance evidence registry contains unsafe state"
                        ) from exc
                    evidence_leases.append(
                        _EvidenceLease(kind=kind, name=name, record=record)
                    )
            finally:
                os.close(directory_descriptor)
        if len(evidence_leases) > MAX_REGISTRY_ENTRIES:
            raise LayoutLeaseError("maintenance evidence registry is too large")
        return evidence_leases

    @staticmethod
    def _bounded_directory_names(directory_descriptor: int) -> list[str]:
        try:
            names = os.listdir(directory_descriptor)
        except OSError as exc:
            raise LayoutLeaseError("maintenance registry cannot be scanned") from exc
        if len(names) > MAX_REGISTRY_ENTRIES:
            raise LayoutLeaseError("maintenance registry is too large")
        if any(len(os.fsencode(name)) > MAX_REGISTRY_FILENAME_BYTES for name in names):
            raise LayoutLeaseError("maintenance registry filename is too long")
        return sorted(names)

    @contextmanager
    def _registry_guard(self) -> Iterator[int]:
        self._ensure_darwin_capability()
        ensure_owner_directory(self._namespace_root)
        namespace_descriptor = self._open_directory(self._namespace_root)
        lock_descriptor: int | None = None
        try:
            lock_descriptor = self._open_registry_lock(namespace_descriptor)
            if _fcntl is None:
                raise MaintenancePlatformError("Darwin advisory locking is unavailable")
            _fcntl.flock(lock_descriptor, _fcntl.LOCK_EX)
            self._verify_named_inode(
                namespace_descriptor,
                REGISTRY_LOCK_NAME,
                lock_descriptor,
            )
            yield namespace_descriptor
        finally:
            if lock_descriptor is not None:
                if _fcntl is not None:
                    _fcntl.flock(lock_descriptor, _fcntl.LOCK_UN)
                os.close(lock_descriptor)
            os.close(namespace_descriptor)

    def _open_registry_lock(self, namespace_descriptor: int) -> int:
        flags = os.O_RDWR
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        created = False
        descriptor: int | None = None
        try:
            try:
                descriptor = os.open(
                    REGISTRY_LOCK_NAME,
                    flags | os.O_CREAT | os.O_EXCL,
                    0o600,
                    dir_fd=namespace_descriptor,
                )
                created = True
            except FileExistsError:
                descriptor = os.open(
                    REGISTRY_LOCK_NAME,
                    flags,
                    dir_fd=namespace_descriptor,
                )
            try:
                self._verify_owner_file(descriptor, allow_set_mode=created)
                if created:
                    os.fsync(namespace_descriptor)
            except BaseException:
                os.close(descriptor)
                descriptor = None
                raise
            return descriptor
        except OSError as exc:
            raise LayoutLeaseError("maintenance registry lock is unsafe") from exc

    def _create_active_lease(
        self,
        namespace_descriptor: int,
        lease_name: str,
        record: LayoutLeaseRecord,
    ) -> int:
        payload = record.model_dump_json().encode("utf-8")
        if len(payload) > MAX_LEASE_BYTES:
            raise LayoutLeaseError("maintenance lease metadata is too large")
        descriptor: int | None = None
        try:
            if LayoutLeaseRecord.model_validate_json(payload) != record:
                raise LayoutLeaseError("maintenance lease payload does not round trip")
            flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(
                lease_name,
                flags,
                0o600,
                dir_fd=namespace_descriptor,
            )
            self._verify_owner_file(descriptor, allow_set_mode=True)
            self._write_all(descriptor, payload)
            os.fsync(descriptor)
            if _fcntl is None:
                raise MaintenancePlatformError("Darwin advisory locking is unavailable")
            _fcntl.flock(descriptor, _fcntl.LOCK_EX | _fcntl.LOCK_NB)
            os.fsync(namespace_descriptor)
            self._verify_named_inode(namespace_descriptor, lease_name, descriptor)
            result = descriptor
            descriptor = None
            return result
        except FileExistsError as exc:
            raise LayoutLeaseContentionError(
                "maintenance layout lease already exists"
            ) from exc
        except Exception as exc:
            if descriptor is not None:
                try:
                    self._cleanup_partial_active_lease(
                        namespace_descriptor,
                        lease_name,
                        descriptor,
                    )
                finally:
                    if _fcntl is not None:
                        with suppress(OSError):
                            _fcntl.flock(descriptor, _fcntl.LOCK_UN)
                    os.close(descriptor)
            if isinstance(exc, LayoutLeaseError):
                raise
            raise LayoutLeaseError("maintenance lease could not be created") from exc

    def _cleanup_partial_active_lease(
        self,
        namespace_descriptor: int,
        lease_name: str,
        descriptor: int,
    ) -> None:
        try:
            self._verify_named_inode(
                namespace_descriptor,
                lease_name,
                descriptor,
            )
            os.unlink(lease_name, dir_fd=namespace_descriptor)
            self._fsync_partial_cleanup(namespace_descriptor)
        except Exception as exc:
            if not self._named_file_exists(namespace_descriptor, lease_name):
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                if hasattr(os, "O_NOFOLLOW"):
                    flags |= os.O_NOFOLLOW
                blocker = os.open(
                    lease_name,
                    flags,
                    0o600,
                    dir_fd=namespace_descriptor,
                )
                try:
                    if os.name == "posix":
                        os.fchmod(blocker, 0o600)
                    os.fsync(blocker)
                finally:
                    os.close(blocker)
                with suppress(OSError):
                    os.fsync(namespace_descriptor)
            raise LayoutLeaseError(
                "partial maintenance lease cleanup failed closed"
            ) from exc

    @staticmethod
    def _fsync_partial_cleanup(namespace_descriptor: int) -> None:
        os.fsync(namespace_descriptor)

    def _open_active_lease(self, namespace_descriptor: int, lease_name: str) -> int:
        flags = os.O_RDWR
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor: int | None = None
        try:
            before = os.stat(
                lease_name,
                dir_fd=namespace_descriptor,
                follow_symlinks=False,
            )
            descriptor = os.open(lease_name, flags, dir_fd=namespace_descriptor)
            try:
                self._verify_owner_file(descriptor)
                after = os.fstat(descriptor)
                if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
                    raise OSError("lease inode changed")
            except BaseException:
                os.close(descriptor)
                descriptor = None
                raise
            return descriptor
        except OSError as exc:
            raise LayoutLeaseError("maintenance lease cannot be opened safely") from exc

    def _read_lease_descriptor(self, descriptor: int) -> LayoutLeaseRecord:
        info = os.fstat(descriptor)
        if info.st_size > MAX_LEASE_BYTES:
            raise LayoutLeaseError("maintenance lease metadata is too large")
        os.lseek(descriptor, 0, os.SEEK_SET)
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(65536, MAX_LEASE_BYTES + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_LEASE_BYTES:
                raise LayoutLeaseError("maintenance lease metadata is too large")
            chunks.append(chunk)
        try:
            return LayoutLeaseRecord.model_validate_json(b"".join(chunks))
        except ValidationError as exc:
            raise LayoutLeaseError("maintenance lease metadata is invalid") from exc

    def _open_evidence_kind_directory(
        self,
        kind: _EvidenceKind,
        *,
        create: bool,
    ) -> int | None:
        evidence = self._namespace_root / "evidence"
        directory = evidence / kind.value
        if create:
            ensure_owner_directory(directory)
        else:
            try:
                directory.lstat()
            except FileNotFoundError:
                return None
            except OSError as exc:
                raise LayoutLeaseError(
                    "maintenance evidence directory cannot be inspected"
                ) from exc
        return self._open_directory(directory)

    def _open_directory(self, path: Path) -> int:
        before = path.lstat()
        flags = os.O_RDONLY
        if hasattr(os, "O_DIRECTORY"):
            flags |= os.O_DIRECTORY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(path, flags)
        try:
            after = os.fstat(descriptor)
            if (
                not stat.S_ISDIR(after.st_mode)
                or (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino)
                or (os.name == "posix" and stat.S_IMODE(after.st_mode) != 0o700)
                or (os.name == "posix" and after.st_uid != self._user_id)
            ):
                raise LayoutLeaseError("maintenance registry directory is unsafe")
        except BaseException:
            os.close(descriptor)
            raise
        return descriptor

    def _verify_owner_file(
        self, descriptor: int, *, allow_set_mode: bool = False
    ) -> None:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != self._user_id:
            raise OSError("lease file owner or type mismatch")
        if allow_set_mode:
            os.fchmod(descriptor, 0o600)
        elif stat.S_IMODE(info.st_mode) != 0o600:
            raise OSError("lease file is not owner-only")

    @staticmethod
    def _verify_named_inode(
        directory_descriptor: int,
        name: str,
        descriptor: int,
    ) -> None:
        path_info = os.stat(
            name,
            dir_fd=directory_descriptor,
            follow_symlinks=False,
        )
        opened_info = os.fstat(descriptor)
        if not stat.S_ISREG(path_info.st_mode) or (
            path_info.st_dev,
            path_info.st_ino,
        ) != (opened_info.st_dev, opened_info.st_ino):
            raise LayoutLeaseError("maintenance lease inode identity changed")

    def _lock_stale_inode(self, descriptor: int) -> None:
        if _fcntl is None:
            raise MaintenancePlatformError("Darwin advisory locking is unavailable")
        try:
            _fcntl.flock(descriptor, _fcntl.LOCK_EX | _fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise StaleLeaseReconciliationError(
                "maintenance lease is still actively locked"
            ) from exc

    @staticmethod
    def _write_all(descriptor: int, payload: bytes) -> None:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("lease write did not make progress")
            view = view[written:]

    @staticmethod
    def _lease_name(layout_fingerprint: str) -> str:
        return f"active-{layout_fingerprint}.lease.json"

    def _record_matches_layout(
        self,
        record: LayoutLeaseRecord,
        layout: FridayChatMaintenanceLayout,
    ) -> bool:
        return (
            record.layout_fingerprint == layout.layout_fingerprint
            and record.live_targets == layout.live_targets
            and record.recovery_root == layout.recovery_root
            and record.log_root == layout.log_root
        )

    @staticmethod
    def _records_share_layout(
        left: LayoutLeaseRecord,
        right: LayoutLeaseRecord,
    ) -> bool:
        return (
            left.layout_fingerprint == right.layout_fingerprint
            and left.live_targets == right.live_targets
            and left.recovery_root == right.recovery_root
            and left.log_root == right.log_root
        )

    @staticmethod
    def _pid_is_proven_dead(process_id: int) -> bool:
        try:
            os.kill(process_id, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            return False
        except OSError as exc:
            return exc.errno == errno.ESRCH
        return False

    def _ensure_darwin_capability(self) -> None:
        if (
            self._platform_name != "Darwin"
            or _fcntl is None
            or _pwd is None
            or self._user_id < 0
        ):
            raise MaintenancePlatformError(
                "maintenance execute durability is verified only on Darwin"
            )

    @staticmethod
    def _production_namespace() -> Path:
        if not hasattr(os, "getuid") or _pwd is None:
            return Path("/unsupported/friday-chat-maintenance-locks")
        home = Path(_pwd.getpwuid(os.getuid()).pw_dir)
        return (
            home
            / "Library"
            / "Application Support"
            / "friday-chat"
            / "maintenance-locks"
            / "v1"
        )

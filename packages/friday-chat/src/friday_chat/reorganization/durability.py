"""Owner-only atomic JSON persistence for maintenance artifacts."""

from __future__ import annotations

import hashlib
import os
import stat
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Protocol, TypeVar, cast
from uuid import uuid4

from pydantic import BaseModel, ValidationError


class _FcntlApi(Protocol):
    LOCK_EX: int
    LOCK_UN: int

    def flock(self, descriptor: int, operation: int) -> None: ...


try:
    import fcntl as _loaded_fcntl
except ImportError:  # pragma: no cover - execute capability is Darwin-only
    _fcntl: _FcntlApi | None = None
else:
    _fcntl = cast(_FcntlApi, _loaded_fcntl)


class DurableArtifactError(RuntimeError):
    """Raised when an artifact cannot be confined, persisted, or verified."""


@dataclass(frozen=True)
class DurableArtifact:
    """Verified path, checksum, and size for one persisted JSON payload."""

    path: Path
    sha256: str
    size_bytes: int


ModelT = TypeVar("ModelT", bound=BaseModel)
DEFAULT_MAX_JSON_BYTES = 16 * 1024 * 1024


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("durable JSON write did not make progress")
        view = view[written:]


def _read_all(descriptor: int, *, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = os.read(descriptor, 1024 * 1024)
        if not chunk:
            return b"".join(chunks)
        total += len(chunk)
        if total > max_bytes:
            raise DurableArtifactError("artifact exceeds its configured size limit")
        chunks.append(chunk)


def _fsync_directory(path: Path) -> None:
    _assert_no_symlink_components(path)
    try:
        before = path.lstat()
    except OSError as exc:
        raise DurableArtifactError("durable directory cannot be inspected") from exc
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISDIR(info.st_mode)
            or stat.S_ISLNK(before.st_mode)
            or (info.st_dev, info.st_ino) != (before.st_dev, before.st_ino)
        ):
            raise OSError("durable JSON parent is not a directory")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _assert_no_symlink_components(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            return
        except OSError as exc:
            raise DurableArtifactError("artifact path identity cannot be inspected") from exc
        if stat.S_ISLNK(info.st_mode):
            raise DurableArtifactError("artifact path traverses a symlink")


def _assert_owner_directory(path: Path) -> None:
    _assert_no_symlink_components(path)
    try:
        info = path.lstat()
    except OSError as exc:
        raise DurableArtifactError("artifact directory cannot be inspected") from exc
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
        raise DurableArtifactError("artifact directory is not a safe directory")
    if os.name == "posix":
        if info.st_uid != os.getuid():
            raise DurableArtifactError("artifact directory has an unexpected owner")
        if stat.S_IMODE(info.st_mode) != 0o700:
            raise DurableArtifactError("artifact directory is not owner-only")


def ensure_owner_directory(path: Path) -> None:
    """Create a directory chain without accepting symlink traversal."""
    if not path.is_absolute():
        raise DurableArtifactError("artifact directory must be absolute")
    _assert_no_symlink_components(path)
    missing: list[Path] = []
    current = path
    while True:
        try:
            info = current.lstat()
        except FileNotFoundError:
            missing.append(current)
            parent = current.parent
            if parent == current:
                raise DurableArtifactError(
                    "artifact directory has no safe anchor"
                ) from None
            current = parent
            continue
        except OSError as exc:
            raise DurableArtifactError("artifact directory cannot be inspected") from exc
        if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
            raise DurableArtifactError("artifact directory traverses an unsafe path")
        break

    for directory in reversed(missing):
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError:
            _assert_owner_directory(directory)
        else:
            if os.name == "posix":
                directory.chmod(0o700)
            _fsync_directory(directory.parent)
    _assert_owner_directory(path)
    _assert_no_symlink_components(path)


class AtomicJsonStore:
    """Persist strict Pydantic JSON below one immutable confinement root."""

    def __init__(
        self,
        root: Path,
        *,
        max_json_bytes: int = DEFAULT_MAX_JSON_BYTES,
    ) -> None:
        if not root.is_absolute():
            raise DurableArtifactError("artifact root must be absolute")
        if max_json_bytes <= 0:
            raise ValueError("max_json_bytes must be positive")
        self._root = root
        self._max_json_bytes = max_json_bytes

    @property
    def root(self) -> Path:
        return self._root

    def confined_path(self, relative_path: str | PurePath) -> Path:
        """Return a lexical child path while rejecting traversal and aliases."""
        relative = PurePath(relative_path)
        if relative.is_absolute() or not relative.parts:
            raise DurableArtifactError("artifact path must be relative")
        if any(part in {"", ".", ".."} for part in relative.parts):
            raise DurableArtifactError("artifact path escapes its confinement root")
        candidate = self._root.joinpath(*relative.parts)
        try:
            candidate.relative_to(self._root)
        except ValueError as exc:
            raise DurableArtifactError("artifact path escapes its confinement root") from exc
        _assert_no_symlink_components(candidate)
        return candidate

    def write_model(
        self,
        relative_path: str | PurePath,
        model: ModelT,
        *,
        expected_current_sha256: str | None = None,
        expected_revision: int | None = None,
        require_absent: bool = False,
    ) -> DurableArtifact:
        """Atomically persist with checksum/revision compare-and-swap guards."""
        path = self.confined_path(relative_path)
        ensure_owner_directory(path.parent)
        _assert_no_symlink_components(path)
        self._reject_unsafe_existing_file(path)
        payload = model.model_dump_json().encode("utf-8")
        expected_sha256 = hashlib.sha256(payload).hexdigest()
        try:
            parsed_payload = type(model).model_validate_json(payload)
        except ValidationError as exc:
            raise DurableArtifactError("artifact payload schema is invalid") from exc
        if parsed_payload != model:
            raise DurableArtifactError("artifact payload does not round trip")
        temp_name = f".{path.name}.{uuid4().hex}.tmp"
        parent_descriptor = self._open_parent(path.parent)
        temp_descriptor: int | None = None
        writer_lock_descriptor: int | None = None
        try:
            writer_lock_descriptor = self._lock_writer(
                parent_descriptor,
                path.name,
            )
            current_payload = self._read_named_payload(
                parent_descriptor,
                path.name,
                allow_absent=True,
                max_bytes=self._max_json_bytes,
            )
            if require_absent and current_payload is not None:
                raise DurableArtifactError("artifact already exists")
            if (
                expected_current_sha256 is not None
                and (
                    current_payload is None
                    or hashlib.sha256(
                        current_payload
                    ).hexdigest()
                    != expected_current_sha256
                )
            ):
                raise DurableArtifactError(
                    "artifact compare-and-swap checksum failed"
                )
            if expected_revision is not None:
                if current_payload is None:
                    raise DurableArtifactError("artifact compare-and-swap revision failed")
                try:
                    current_model = type(model).model_validate_json(current_payload)
                except ValidationError as exc:
                    raise DurableArtifactError("current artifact schema is invalid") from exc
                current_revision = getattr(current_model, "revision", None)
                next_revision = getattr(model, "revision", None)
                if (
                    current_revision != expected_revision
                    or next_revision != expected_revision + 1
                ):
                    raise DurableArtifactError(
                        "artifact compare-and-swap revision failed"
                    )
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            temp_descriptor = os.open(
                temp_name,
                flags,
                0o600,
                dir_fd=parent_descriptor,
            )
            if os.name == "posix":
                os.fchmod(temp_descriptor, 0o600)
            _write_all(temp_descriptor, payload)
            os.fsync(temp_descriptor)
            os.close(temp_descriptor)
            temp_descriptor = None
            os.replace(
                temp_name,
                path.name,
                src_dir_fd=parent_descriptor,
                dst_dir_fd=parent_descriptor,
            )
            os.fsync(parent_descriptor)
            verified_payload = self._read_named_payload(
                parent_descriptor,
                path.name,
                allow_absent=False,
                max_bytes=self._max_json_bytes,
            )
            if verified_payload != payload:
                raise DurableArtifactError("artifact read-back validation did not match")
        except OSError as exc:
            if temp_descriptor is not None:
                os.close(temp_descriptor)
            with suppress(OSError):
                os.unlink(temp_name, dir_fd=parent_descriptor)
            raise DurableArtifactError("artifact could not be persisted atomically") from exc
        finally:
            if writer_lock_descriptor is not None:
                if _fcntl is not None:
                    _fcntl.flock(writer_lock_descriptor, _fcntl.LOCK_UN)
                os.close(writer_lock_descriptor)
            os.close(parent_descriptor)
        return DurableArtifact(
            path=path,
            sha256=expected_sha256,
            size_bytes=len(payload),
        )

    def read_model(
        self,
        relative_path: str | PurePath,
        model_type: type[ModelT],
        *,
        expected_sha256: str | None = None,
    ) -> tuple[ModelT, DurableArtifact]:
        """Read without symlink traversal and validate checksum plus schema."""
        path = self.confined_path(relative_path)
        _assert_no_symlink_components(path)
        parent_descriptor = self._open_parent(path.parent)
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            before = os.stat(
                path.name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
            self._validate_owner_file_info(before)
            descriptor = os.open(path.name, flags, dir_fd=parent_descriptor)
            try:
                info = os.fstat(descriptor)
                if (
                    not stat.S_ISREG(info.st_mode)
                    or (info.st_dev, info.st_ino) != (before.st_dev, before.st_ino)
                ):
                    raise OSError("artifact is not regular")
                if info.st_size > self._max_json_bytes:
                    raise DurableArtifactError(
                        "artifact exceeds its configured size limit"
                    )
                if os.name == "posix":
                    if info.st_uid != os.getuid():
                        raise OSError("artifact owner mismatch")
                    if stat.S_IMODE(info.st_mode) != 0o600:
                        raise OSError("artifact is not owner-only")
                payload = _read_all(
                    descriptor,
                    max_bytes=self._max_json_bytes,
                )
            finally:
                os.close(descriptor)
        except (FileNotFoundError, OSError) as exc:
            raise DurableArtifactError("artifact cannot be read safely") from exc
        finally:
            os.close(parent_descriptor)
        digest = hashlib.sha256(payload).hexdigest()
        if expected_sha256 is not None and digest != expected_sha256:
            raise DurableArtifactError("artifact checksum does not match")
        try:
            model = model_type.model_validate_json(payload)
        except ValidationError as exc:
            raise DurableArtifactError("artifact schema is invalid") from exc
        return model, DurableArtifact(
            path=path,
            sha256=digest,
            size_bytes=len(payload),
        )

    @staticmethod
    def _open_parent(path: Path) -> int:
        _assert_no_symlink_components(path)
        _assert_owner_directory(path)
        try:
            before = path.lstat()
        except OSError as exc:
            raise DurableArtifactError("artifact parent cannot be inspected") from exc
        flags = os.O_RDONLY
        if hasattr(os, "O_DIRECTORY"):
            flags |= os.O_DIRECTORY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            descriptor = os.open(path, flags)
            try:
                info = os.fstat(descriptor)
                if (
                    not stat.S_ISDIR(info.st_mode)
                    or stat.S_ISLNK(before.st_mode)
                    or (info.st_dev, info.st_ino)
                    != (before.st_dev, before.st_ino)
                ):
                    raise OSError("artifact parent is not a directory")
            except BaseException:
                os.close(descriptor)
                raise
            return descriptor
        except OSError as exc:
            raise DurableArtifactError("artifact parent identity is unsafe") from exc

    @staticmethod
    def _reject_unsafe_existing_file(
        path: Path,
        *,
        require_present: bool = False,
    ) -> os.stat_result | None:
        try:
            info = path.lstat()
        except FileNotFoundError:
            if require_present:
                raise DurableArtifactError("artifact is absent") from None
            return None
        except OSError as exc:
            raise DurableArtifactError("artifact identity cannot be inspected") from exc
        AtomicJsonStore._validate_owner_file_info(info)
        return info

    @staticmethod
    def _validate_owner_file_info(info: os.stat_result) -> None:
        if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
            raise DurableArtifactError("artifact path is not a regular file")
        if os.name == "posix" and info.st_uid != os.getuid():
            raise DurableArtifactError("artifact has an unexpected owner")
        if os.name == "posix" and stat.S_IMODE(info.st_mode) != 0o600:
            raise DurableArtifactError("artifact is not owner-only")

    @staticmethod
    def _lock_writer(parent_descriptor: int, filename: str) -> int:
        if _fcntl is None:
            raise DurableArtifactError("artifact write locking is unavailable")
        lock_name = f".{filename}.write.lock"
        flags = os.O_RDWR
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        created = False
        try:
            try:
                descriptor = os.open(
                    lock_name,
                    flags | os.O_CREAT | os.O_EXCL,
                    0o600,
                    dir_fd=parent_descriptor,
                )
                created = True
            except FileExistsError:
                descriptor = os.open(
                    lock_name,
                    flags,
                    dir_fd=parent_descriptor,
                )
            try:
                info = os.fstat(descriptor)
                if not stat.S_ISREG(info.st_mode):
                    raise OSError("artifact lock is not regular")
                if os.name == "posix":
                    if info.st_uid != os.getuid():
                        raise OSError("artifact lock owner mismatch")
                    if created:
                        os.fchmod(descriptor, 0o600)
                    elif stat.S_IMODE(info.st_mode) != 0o600:
                        raise OSError("artifact lock is not owner-only")
                if created:
                    os.fsync(parent_descriptor)
                _fcntl.flock(descriptor, _fcntl.LOCK_EX)
            except BaseException:
                os.close(descriptor)
                raise
            return descriptor
        except OSError as exc:
            raise DurableArtifactError("artifact write lock is unsafe") from exc

    @staticmethod
    def _read_named_payload(
        parent_descriptor: int,
        filename: str,
        *,
        allow_absent: bool,
        max_bytes: int,
    ) -> bytes | None:
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            before = os.stat(
                filename,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
            AtomicJsonStore._validate_owner_file_info(before)
            descriptor = os.open(filename, flags, dir_fd=parent_descriptor)
        except FileNotFoundError:
            if allow_absent:
                return None
            raise DurableArtifactError("artifact disappeared during persistence") from None
        except OSError as exc:
            raise DurableArtifactError("artifact identity changed during persistence") from exc
        try:
            info = os.fstat(descriptor)
            AtomicJsonStore._validate_owner_file_info(info)
            if (info.st_dev, info.st_ino) != (before.st_dev, before.st_ino):
                raise DurableArtifactError(
                    "artifact identity changed during persistence"
                )
            if info.st_size > max_bytes:
                raise DurableArtifactError(
                    "artifact exceeds its configured size limit"
                )
            return _read_all(descriptor, max_bytes=max_bytes)
        finally:
            os.close(descriptor)

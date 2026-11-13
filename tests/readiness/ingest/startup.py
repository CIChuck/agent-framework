"""Explicit Python-visible guard. Native/OS containment is never claimed."""

from __future__ import annotations

import _thread
import contextvars
import os
import stat
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from ingest.environment import child_environment
from ingest.manifests import Refusal, digest, require

_original_stat = os.stat
_original_lstat = os.lstat
_original_fstat = os.fstat
_original_access = os.access
_original_open = os.open
_original_readlink = os.readlink
_original_mkfifo = os.mkfifo
_original_mknod = os.mknod
_original_thread = _thread.start_new_thread
_active: contextvars.ContextVar[Guard | None] = contextvars.ContextVar(
    "guard", default=None
)
_checking: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "checking", default=False
)
_installed = False


@dataclass(frozen=True)
class Guard:
    reads: tuple[Path, ...]
    writes: tuple[Path, ...]
    python: str | None = None
    native_git: str | None = None
    native_fixture_writes: bool = False
    python_scripts: tuple[tuple[str, str], ...] = ()

    def path(self, value: object, write: bool = False, probe: bool = False) -> None:
        if _checking.get():
            return
        token = _checking.set(True)
        try:
            if isinstance(value, int):
                info = _original_fstat(value)
                require(
                    stat.S_ISFIFO(info.st_mode) or value in {0, 1, 2},
                    "Unclassified regular file descriptor",
                )
                return
            if not isinstance(value, (str, bytes, os.PathLike)):
                raise Refusal("Unclassified file descriptor/path")
            path = Path(os.fsdecode(value)).absolute()
            canonical = path.resolve(strict=False)
            require(path == canonical, "Guarded alias/symlink path")
            roots = self.writes if write else self.reads + self.writes
            allowed = any(
                canonical == root or root in canonical.parents for root in roots
            )
            # Only path-canonicalization metadata may inspect exact ancestors.
            # Access/existence-permission probes do not receive this exception.
            if probe and not write:
                allowed = allowed or any(canonical in root.parents for root in roots)
            require(allowed, "Undeclared write" if write else "Undeclared read/probe")
        finally:
            _checking.reset(token)


def _argv(value: object) -> list[str]:
    if not isinstance(value, (list, tuple)):
        raise Refusal("Child argv required")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise Refusal("Child argv item is not text")
        result.append(item)
    return result


def _audit(event: str, args: tuple[object, ...]) -> None:
    guard = _active.get()
    if guard is None or _checking.get():
        return
    if event in {"_thread.start_new_thread", "_thread.start_joinable_thread"}:
        # CPython audits both launch paths, including saved builtin aliases and
        # threading's imported joinable-thread entrypoint, before the worker starts.
        raise Refusal("Unpropagated worker thread refused in C0")
    if event == "ctypes.dlopen":
        raise Refusal("Unqualified native library load")
    if event == "open":
        mode = args[1]
        flags = args[2]
        writing = isinstance(mode, str) and any(ch in mode for ch in "wax+")
        writing = (
            writing
            or isinstance(flags, int)
            and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
        )
        guard.path(args[0], writing)
    elif event in {
        "os.mkdir",
        "os.remove",
        "os.rmdir",
        "os.chmod",
        "os.chown",
        "os.truncate",
        "os.utime",
    }:
        positions = {
            "os.mkdir": 2,
            "os.remove": 1,
            "os.rmdir": 1,
            "os.chmod": 2,
            "os.chown": 3,
            "os.utime": 3,
        }
        if event in positions:
            position = positions[event]
            require(
                len(args) > position and args[position] in {None, -1},
                "dir_fd operation refused",
            )
        guard.path(args[0], True)
    elif event in {"os.rename", "os.link", "os.symlink"}:
        require(
            all(item in {None, -1} for item in args[2:]),
            "dir_fd rename/link refused",
        )
        guard.path(args[0], True)
        guard.path(args[1], True)
    elif event in {"os.listdir", "os.scandir", "os.chdir"}:
        guard.path(args[0])
    elif event.startswith("socket.") or event in {
        "os.system",
        "os.exec",
        "os.posix_spawn",
    }:
        raise Refusal("Network/native process effect is not C0-authorized")
    elif event == "subprocess.Popen":
        if guard.native_git is not None and args[0] == guard.native_git:
            argv = _argv(args[1])
            require(len(argv) > 1, "Native Git argv required")
            verb = argv[1]
            if len(argv) > 3 and argv[1:3] == ["-c", "core.hooksPath=/dev/null"]:
                verb = argv[3]
            allowed = {"cat-file", "rev-parse", "ls-tree"}
            if guard.native_fixture_writes:
                allowed |= {"init", "add", "commit"}
            require(verb in allowed, "Unapproved native Git verb")
            require(
                not any(
                    isinstance(item, str)
                    and item.startswith(("--git-dir", "--work-tree"))
                    for item in argv
                ),
                "Native Git repository override refused",
            )
            require(args[2] is not None, "Explicit native child cwd required")
            guard.path(args[2], verb in {"init", "add", "commit"})
            env = args[3]
            require(isinstance(env, dict), "Explicit native Git environment required")
            if isinstance(env, dict):
                for key in (
                    "GIT_DIR",
                    "GIT_OBJECT_DIRECTORY",
                    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                    "GIT_CONFIG_GLOBAL",
                    "GIT_CONFIG_SYSTEM",
                ):
                    if key in env:
                        guard.path(env[key])
            return
        require(
            guard.python is not None and args[0] == guard.python,
            "Unapproved child executable",
        )
        argv = _argv(args[1])
        require(
            all(flag in argv for flag in ("-I", "-S", "-B")),
            "Child startup flags missing",
        )
        require("-c" not in argv and "-m" not in argv, "Unbound child code refused")
        require(
            not sys.flags.optimize or "-O" in argv, "Optimized child lane omitted -O"
        )
        index = 1
        while index < len(argv) and argv[index] in {"-I", "-S", "-B", "-O"}:
            index += 1
        require(index < len(argv), "Child script missing")
        script = Path(argv[index])
        self_scripts = dict(guard.python_scripts)
        require(str(script) in self_scripts, "Unapproved Python child script")
        guard.path(script)
        require(
            digest(script.read_bytes()) == self_scripts[str(script)],
            "Child launcher digest changed",
        )
        env = args[3]
        require(isinstance(env, dict), "Explicit Python child environment required")
        if not isinstance(env, dict) or not isinstance(env.get("NETRC"), str):
            raise Refusal("Private child environment missing")
        env_root = Path(env["NETRC"]).parent
        guard.path(env_root, True)
        require(
            env == child_environment(env_root, {"HOME": os.environ.get("HOME", "")}),
            "Unexpected child environment/discovery settings",
        )
        require(args[2] is not None, "Explicit child cwd required")
        guard.path(args[2])


type FilePath = str | bytes | os.PathLike[str] | os.PathLike[bytes]


def _stat(
    path: FilePath | int, *, dir_fd: int | None = None, follow_symlinks: bool = True
) -> os.stat_result:
    guard = _active.get()
    if guard is not None:
        require(dir_fd is None, "dir_fd probe refused")
        guard.path(path, probe=True)
    return _original_stat(path, dir_fd=dir_fd, follow_symlinks=follow_symlinks)


def _lstat(path: FilePath, *, dir_fd: int | None = None) -> os.stat_result:
    guard = _active.get()
    if guard is not None:
        require(dir_fd is None, "dir_fd probe refused")
        guard.path(path, probe=True)
    return _original_lstat(path, dir_fd=dir_fd)


def _fstat(fd: int) -> os.stat_result:
    guard = _active.get()
    if guard is not None and not _checking.get():
        guard.path(fd)
    return _original_fstat(fd)


def _access(
    path: FilePath,
    mode: int,
    *,
    dir_fd: int | None = None,
    effective_ids: bool = False,
    follow_symlinks: bool = True,
) -> bool:
    guard = _active.get()
    if guard is not None and not _checking.get():
        require(dir_fd is None, "dir_fd access refused")
        guard.path(path)
    return _original_access(
        path,
        mode,
        dir_fd=dir_fd,
        effective_ids=effective_ids,
        follow_symlinks=follow_symlinks,
    )


def _open(
    path: FilePath, flags: int, mode: int = 0o777, *, dir_fd: int | None = None
) -> int:
    guard = _active.get()
    if guard is not None and not _checking.get():
        require(dir_fd is None, "dir_fd open refused")
        guard.path(
            path, bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
        )
    return _original_open(path, flags, mode, dir_fd=dir_fd)


def _readlink(path: FilePath, *, dir_fd: int | None = None) -> str | bytes:
    guard = _active.get()
    if guard is not None and not _checking.get():
        require(dir_fd is None, "dir_fd readlink refused")
        guard.path(path, probe=True)
    raw = path if isinstance(path, (str, bytes)) else path.__fspath__()
    if isinstance(raw, bytes):
        return _original_readlink(raw, dir_fd=dir_fd)
    return _original_readlink(raw, dir_fd=dir_fd)


def _mkfifo(path: FilePath, mode: int = 0o666, *, dir_fd: int | None = None) -> None:
    guard = _active.get()
    if guard is not None and not _checking.get():
        require(dir_fd is None, "dir_fd mkfifo refused")
        guard.path(path, True)
    _original_mkfifo(path, mode, dir_fd=dir_fd)


def _mknod(
    path: FilePath,
    mode: int = 0o600,
    device: int = 0,
    *,
    dir_fd: int | None = None,
) -> None:
    guard = _active.get()
    if guard is not None and not _checking.get():
        require(dir_fd is None, "dir_fd mknod refused")
        guard.path(path, True)
    _original_mknod(path, mode, device, dir_fd=dir_fd)


def _thread_start(
    function: Callable[..., object],
    args: tuple[object, ...],
    kwargs: dict[str, object] | None = None,
) -> int:
    require(_active.get() is None, "Unpropagated worker thread refused in C0")
    return _original_thread(function, args, {} if kwargs is None else kwargs)


@contextmanager
def guarded(policy: Guard) -> Iterator[None]:
    global _installed
    if not _installed:
        sys.addaudithook(_audit)
        # Instrument the declared dynamic stdlib API boundary without weakening types.
        vars(os).update(
            stat=_stat,
            lstat=_lstat,
            fstat=_fstat,
            access=_access,
            open=_open,
            readlink=_readlink,
            mkfifo=_mkfifo,
            mknod=_mknod,
        )
        vars(_thread)["start_new_thread"] = _thread_start
        _installed = True
    parent = _active.get()
    if parent is not None:
        require(
            policy.python in {None, parent.python}
            and policy.native_git in {None, parent.native_git},
            "Child guard process capability escalation",
        )
        require(
            not policy.native_fixture_writes or parent.native_fixture_writes,
            "Child guard native-write escalation",
        )
        require(
            set(policy.python_scripts) <= set(parent.python_scripts),
            "Child guard script escalation",
        )
        for root in policy.reads:
            parent.path(root)
        for root in policy.writes:
            parent.path(root, True)
    token = _active.set(policy)
    try:
        yield
    finally:
        _active.reset(token)


def harness_state() -> tuple[Path, dict[str, bytes]]:
    module = sys.modules["ingest"]
    root: object = getattr(module, "ROOT", None)
    value: object = getattr(module, "BUFFERS", None)
    require(
        isinstance(root, Path) and isinstance(value, dict),
        "Approved bootstrap state missing",
    )
    if not isinstance(root, Path) or not isinstance(value, dict):
        raise Refusal("Approved bootstrap state missing")
    buffers: dict[str, bytes] = {}
    for key, raw in value.items():
        require(
            isinstance(key, str) and isinstance(raw, bytes), "Malformed bootstrap state"
        )
        if isinstance(key, str) and isinstance(raw, bytes):
            buffers[key] = raw
    return root, buffers

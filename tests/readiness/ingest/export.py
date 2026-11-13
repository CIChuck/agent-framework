"""Read committed regular blobs through an owned bare object view; no checkout."""

from __future__ import annotations

import hashlib
import os
import selectors
import subprocess
import time
from pathlib import Path

from ingest.manifests import GIT_ID, digest, require
from ingest.paths import physical, regular_relative

FORBIDDEN = {".env", ".git", ".friday", ".friday-old", ".venv", "exports"}
LIVE_FINANCE = "packages/friday-finance/tests/test_integration_massive.py"


class ObjectView:
    def __init__(self, owned: Path, source_objects: Path, git: Path) -> None:
        self.root = physical(owned)
        self.objects = physical(source_objects)
        self.git = physical(git, owner=False)
        require(
            self.objects.is_dir() and self.git.is_file(),
            "Missing declared Git object/tool root",
        )
        for count, item in enumerate(self.objects.rglob("*"), 1):
            require(
                count <= 100000 and not item.is_symlink(),
                "Unqualified object-store metadata/symlink",
            )
        require(
            self.root != self.objects
            and self.root not in self.objects.parents
            and self.objects not in self.root.parents,
            "Object view/source overlap",
        )
        require(
            not (self.objects / "info/alternates").exists(),
            "Undeclared alternate object traversal",
        )

    def create(self) -> None:
        require(not self.root.exists(), "Object view must be absent")
        self.root.mkdir(mode=0o700)
        for relative in ("objects/info", "refs/heads", "empty-template"):
            (self.root / relative).mkdir(parents=True, mode=0o700)
        (self.root / "HEAD").write_text("ref: refs/heads/unused\n")
        (self.root / "config").write_text(
            "[core]\n bare = true\n hooksPath = /dev/null\n fsmonitor = false\n[gc]\n auto = 0\n[maintenance]\n auto = false\n[protocol]\n allow = never\n[credential]\n helper =\n"
        )
        (self.root / "empty-config").write_bytes(b"")

    def read(self, *args: str) -> bytes:
        allowed = False
        if len(args) == 3 and args[:2] in {
            ("cat-file", "-t"),
            ("cat-file", "blob"),
            ("cat-file", "commit"),
        }:
            allowed = bool(GIT_ID.fullmatch(args[2])) and len(args[2]) == 40
        elif len(args) == 2 and args[0] == "rev-parse" and args[1].endswith("^{tree}"):
            allowed = bool(GIT_ID.fullmatch(args[1][:-7])) and len(args[1][:-7]) == 40
        elif len(args) == 4 and args[:3] == ("ls-tree", "-r", "-z"):
            allowed = bool(GIT_ID.fullmatch(args[3])) and len(args[3]) == 40
        require(allowed, "Unapproved Git object operation/options")
        env = {
            "PATH": "/usr/bin:/bin",
            "GIT_DIR": str(self.root),
            "GIT_OBJECT_DIRECTORY": str(self.root / "objects"),
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(self.objects),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_SYSTEM": str(self.root / "empty-config"),
            "GIT_CONFIG_GLOBAL": str(self.root / "empty-config"),
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_PROTOCOL_FROM_USER": "0",
        }
        process = subprocess.Popen(
            [str(self.git), *args],
            cwd=self.root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        require(process.stdout is not None, "Missing Git output pipe")
        if process.stdout is None:
            raise RuntimeError("Missing Git pipe")
        output = bytearray()
        deadline = time.monotonic() + 30
        try:
            with selectors.DefaultSelector() as ready:
                ready.register(process.stdout, selectors.EVENT_READ)
                while True:
                    remaining = deadline - time.monotonic()
                    require(remaining > 0, "Git export time limit")
                    require(bool(ready.select(remaining)), "Git export time limit")
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk:
                        break
                    require(
                        len(output) + len(chunk) <= 64 * 1024 * 1024,
                        "Git output exceeds export bound",
                    )
                    output.extend(chunk)
            require(
                process.wait(timeout=max(0.001, deadline - time.monotonic())) == 0,
                "Git object read refused",
            )
            return bytes(output)
        finally:
            process.stdout.close()
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)

    def export(
        self, commit: str, selection: dict[str, str], target: Path
    ) -> dict[str, str]:
        require(
            bool(GIT_ID.fullmatch(commit)) and len(commit) == 40,
            "Full SHA1 commit required",
        )
        require(
            self.read("cat-file", "-t", commit).strip() == b"commit",
            "Not a commit object",
        )
        raw_commit = self.read("cat-file", "commit", commit)
        require(
            hashlib.sha1(
                b"commit " + str(len(raw_commit)).encode() + b"\0" + raw_commit
            ).hexdigest()
            == commit,
            "Commit bytes mismatch",
        )
        tree = self.read("rev-parse", commit + "^{tree}").strip().decode()
        listing = self.read("ls-tree", "-r", "-z", tree)
        objects: dict[str, tuple[str, str]] = {}
        for row in listing.split(b"\0"):
            if not row:
                continue
            metadata, raw_name = row.split(b"\t", 1)
            mode, kind, oid = metadata.decode().split()
            if kind == "blob":
                objects[raw_name.decode()] = (mode, oid)
        pending: dict[str, bytes] = {}
        for name, expected in selection.items():
            rel = regular_relative(name)
            require(
                not FORBIDDEN.intersection(rel.parts)
                and not any(part.startswith(".friday") for part in rel.parts)
                and name != LIVE_FINANCE,
                "Excluded source selection",
            )
            require(
                name in objects and objects[name][0] == "100644",
                "Selected source is absent/nonregular",
            )
            raw = self.read("cat-file", "blob", objects[name][1])
            require(
                hashlib.sha1(
                    b"blob " + str(len(raw)).encode() + b"\0" + raw
                ).hexdigest()
                == objects[name][1]
                and digest(raw) == expected,
                "Selected blob/hash mismatch",
            )
            pending[name] = raw
        require(not target.exists(), "Export destination must be absent")
        physical(target)
        target.mkdir(mode=0o700)
        for name, raw in pending.items():
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            path.chmod(0o444)
        return {name: digest(raw) for name, raw in pending.items()}

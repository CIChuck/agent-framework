"""Externally pinned, stdlib-only bootstrap. No sibling executes before approval."""

from __future__ import annotations

import hashlib
import importlib.abc
import importlib.machinery
import importlib.util
import json
import os
import sys
import types
from pathlib import Path, PurePosixPath

LIMIT = 1024 * 1024


def refuse(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in items:
        refuse(key not in result, "Duplicate bootstrap control key")
        result[key] = value
    return result


def argument(name: str) -> str:
    refuse(sys.argv.count(name) == 1, "Exactly one " + name + " required")
    index = sys.argv.index(name)
    refuse(index + 1 < len(sys.argv), "Missing " + name)
    return sys.argv[index + 1]


def verified_buffers(
    root: Path, manifest_path: Path, expected: str
) -> dict[str, bytes]:
    refuse(not manifest_path.is_symlink(), "Manifest symlink refused")
    with manifest_path.open("rb") as source:
        raw = source.read(LIMIT + 1)
    refuse(len(raw) <= LIMIT, "Harness manifest too large")
    refuse(
        hashlib.sha256(raw).hexdigest() == expected,
        "Unapproved harness manifest digest",
    )
    manifest: object = json.loads(raw, object_pairs_hook=pairs)
    refuse(isinstance(manifest, dict), "Harness manifest must be an object")
    if not isinstance(manifest, dict):
        raise ValueError("Manifest object required")
    refuse(
        set(manifest) == {"schema", "commit", "tree", "files"}
        and type(manifest["schema"]) is int
        and manifest["schema"] == 1,
        "Harness manifest schema",
    )
    for key in ("commit", "tree"):
        value = manifest[key]
        refuse(
            isinstance(value, str)
            and len(value) == 40
            and all(ch in "0123456789abcdef" for ch in value),
            "Missing committed harness identity",
        )
    records = manifest["files"]
    refuse(isinstance(records, list) and 1 <= len(records) <= 128, "Harness file count")
    if not isinstance(records, list):
        raise ValueError("Harness file array required")
    buffers: dict[str, bytes] = {}
    for record in records:
        refuse(isinstance(record, dict), "Harness file record")
        if not isinstance(record, dict):
            raise ValueError("Harness file record required")
        refuse(
            set(record) == {"path", "blob", "sha256", "mode"}, "Harness record fields"
        )
        name = record["path"]
        refuse(isinstance(name, str), "Harness filename must be text")
        if not isinstance(name, str):
            raise ValueError("Harness filename required")
        relative = PurePosixPath(name)
        refuse(
            name == relative.as_posix()
            and bool(relative.parts)
            and not relative.is_absolute()
            and ".." not in relative.parts
            and "\\" not in name,
            "Harness path escape",
        )
        refuse(
            name not in buffers and record["mode"] == "100644",
            "Duplicate/nonregular harness member",
        )
        path = root / relative
        for ancestor in (path, *path.parents):
            refuse(not ancestor.is_symlink(), "Harness symlink refused")
            if ancestor == root:
                break
        refuse(path.is_file(), "Harness member missing")
        with path.open("rb") as source:
            data = source.read(4 * LIMIT + 1)
        refuse(len(data) <= 4 * LIMIT, "Harness member too large")
        refuse(
            hashlib.sha256(data).hexdigest() == record["sha256"],
            "Uncommitted harness bytes",
        )
        blob = hashlib.sha1(
            b"blob " + str(len(data)).encode() + b"\0" + data
        ).hexdigest()
        refuse(blob == record["blob"], "Harness blob identity mismatch")
        buffers[name] = data
    for count, path in enumerate(root.rglob("*"), 1):
        refuse(count <= 512, "Harness enumeration bound")
        refuse(not path.is_symlink(), "Harness tree symlink")
        refuse(
            path.name != "__pycache__" and path.suffix != ".pyc",
            "Cached harness code refused",
        )
        if path.suffix == ".py":
            refuse(
                path.relative_to(root).as_posix() in buffers,
                "Extra importable harness file",
            )
    refuse(
        {"bootstrap.py", "run.py", "startup.py"} <= set(buffers),
        "Incomplete harness manifest",
    )
    return buffers


class Buffers(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, root: Path, buffers: dict[str, bytes]) -> None:
        self.root, self.buffers = root, buffers

    def find_spec(
        self, fullname: str, path: object = None, target: types.ModuleType | None = None
    ) -> importlib.machinery.ModuleSpec | None:
        if not fullname.startswith("ingest."):
            return None
        relative = fullname.removeprefix("ingest.").replace(".", "/") + ".py"
        if relative not in self.buffers:
            raise ImportError(
                "Module absent from approved harness selection: " + fullname
            )
        return importlib.util.spec_from_loader(fullname, self)

    def create_module(
        self, spec: importlib.machinery.ModuleSpec
    ) -> types.ModuleType | None:
        return None

    def exec_module(self, module: types.ModuleType) -> None:
        relative = module.__name__.removeprefix("ingest.").replace(".", "/") + ".py"
        data = self.buffers[relative]
        module.__file__ = str(self.root / relative)
        exec(
            compile(data, module.__file__, "exec", dont_inherit=True, optimize=-1),
            module.__dict__,
        )


def main() -> int:
    refuse(
        sys.implementation.name == "cpython" and sys.version_info[:3] == (3, 13, 10),
        "Qualified CPython 3.13.10 required",
    )
    refuse(
        bool(
            sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode
        ),
        "Use -I -S -B before bootstrap",
    )
    refuse(
        ".venv" not in Path(sys.executable).parts, "Working virtual environment refused"
    )
    home = os.environ.get("HOME", "")
    os.environ.clear()
    os.environ.update(
        {
            "HOME": home,
            "PATH": "/usr/bin:/bin",
            "LANG": "en_US.UTF-8",
            "LITELLM_MODE": "PRODUCTION",
            "LITELLM_LOCAL_MODEL_COST_MAP": "True",
            "GIT_OPTIONAL_LOCKS": "0",
        }
    )
    root = Path(__file__).absolute().parent
    refuse(
        root == root.resolve() and root.stat().st_uid == os.getuid(),
        "Harness alias/owner refused",
    )
    buffers = verified_buffers(
        root,
        Path(argument("--harness-manifest")),
        argument("--harness-manifest-sha256"),
    )
    package = types.ModuleType("ingest")
    package.__path__ = []
    package.__dict__["ROOT"] = root
    package.__dict__["BUFFERS"] = buffers
    sys.modules["ingest"] = package
    tests = types.ModuleType("ingest.tests")
    tests.__path__ = []
    sys.modules["ingest.tests"] = tests
    sys.meta_path.insert(0, Buffers(root, buffers))
    from ingest import stages

    return stages.main(sys.argv[1:])


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError) as exc:
        print(json.dumps({"status": "REFUSED", "reason": str(exc)}), file=sys.stderr)
        raise SystemExit(2) from exc

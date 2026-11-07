"""Build a closed, lock-derived macOS/arm64/Python 3.13.10 artifact trial."""

from __future__ import annotations

import argparse
import email
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tomllib
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.tags import sys_tags
from packaging.utils import canonicalize_name, parse_wheel_filename


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("prepared", type=Path)
    parser.add_argument("--revision", required=True)
    access = parser.add_mutually_exclusive_group(required=True)
    access.add_argument("--fetch", action="store_true")
    access.add_argument("--artifacts", type=Path)
    parser.add_argument("--require-pilot-edge", action="store_true")
    args = parser.parse_args()
    if (
        sys.version_info[:3] != (3, 13, 10)
        or sys.platform != "darwin"
        or platform.machine() != "arm64"
    ):
        raise SystemExit(
            "This profile requires the recorded macOS/arm64 Python 3.13.10 interpreter"
        )
    checkout = Path(
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
        .decode()
        .strip()
    ).resolve()
    source, output, prepared = (
        args.source.resolve(),
        args.output.resolve(),
        args.prepared.resolve(),
    )
    if (
        source.is_relative_to(checkout)
        or output.is_relative_to(checkout)
        or output.is_relative_to(source)
    ):
        raise SystemExit("Use an external clean export and separate external output")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise SystemExit("Use an empty bundle output directory")
    report = {
        "profile": "macOS/arm64/CPython-3.13.10",
        "revision": args.revision,
        "commands": [],
        "downloads": [],
        "workspace_wheels": {},
        "source_only_lineage": {},
    }
    environment = {
        key: value
        for key, value in os.environ.items()
        if not any(
            word in key.upper()
            for word in ("API_KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")
        )
        and key.upper() not in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY")
    }
    environment.update(
        UV_OFFLINE="1",
        UV_NO_INDEX="1",
        UV_FIND_LINKS=str(prepared / "wheelhouse"),
        UV_CACHE_DIR=str(output / "cache"),
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONPATH=str(prepared),
        REVIEW_REPO=str(checkout),
        REVIEW_SCRATCH=str(output),
        LITELLM_LOCAL_MODEL_COST_MAP="True",
        UV_PYTHON_DOWNLOADS="never",
    )
    environment["SOURCE_DATE_EPOCH"] = (
        subprocess.check_output(["git", "show", "-s", "--format=%ct", args.revision])
        .decode()
        .strip()
    )
    report["environment"] = {
        key: environment[key]
        for key in (
            "UV_OFFLINE",
            "UV_NO_INDEX",
            "UV_FIND_LINKS",
            "UV_CACHE_DIR",
            "UV_PYTHON_DOWNLOADS",
            "SOURCE_DATE_EPOCH",
        )
    }
    report["python"] = sys.version

    def run(label: str, command: list[str]) -> str:
        result = subprocess.run(
            command, cwd=source, env=environment, text=True, capture_output=True
        )
        text = result.stdout + result.stderr
        (output / (label + ".log")).write_text(text)
        report["commands"].append(
            {
                "label": label,
                "argv": command,
                "cwd": str(source),
                "exit": result.returncode,
            }
        )
        if result.returncode:
            raise RuntimeError(f"{label} failed: {text[-4000:]}")
        return text

    def fetch(artifact: dict[str, object]) -> Path:
        url = artifact["url"]
        if (
            urlsplit(url).scheme != "https"
            or urlsplit(url).hostname != "files.pythonhosted.org"
        ):
            raise RuntimeError("Unapproved artifact URL")
        filename = Path(unquote(urlsplit(url).path)).name
        target = output / "locked-artifacts" / filename
        target.parent.mkdir(exist_ok=True)
        if args.artifacts is not None:
            data = (args.artifacts / filename).read_bytes()
        else:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(url, timeout=60) as response:
                if urlsplit(response.url).hostname != "files.pythonhosted.org":
                    raise RuntimeError("Unapproved artifact redirect")
                data = response.read()
        expected = artifact["hash"].removeprefix("sha256:")
        if hashlib.sha256(data).hexdigest() != expected:
            raise RuntimeError("Locked artifact hash mismatch: " + filename)
        target.write_bytes(data)
        report["downloads"].append(
            {"url": url, "sha256": expected, "filename": filename}
        )
        return target

    try:
        # Protect every package build input, not just importable Python files.
        source_hashes = {}
        for entry in (
            subprocess.check_output(["git", "ls-tree", "-r", "-z", args.revision])
            .decode()
            .split("\0")
        ):
            if not entry:
                continue
            attributes, name = entry.split("\t", 1)
            if not (
                name.startswith("packages/")
                or name in ("pyproject.toml", "uv.lock", "README.md", "LICENSE")
            ):
                continue
            if attributes.split()[1] != "blob":
                continue
            path = source / name
            data = (
                os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
            )
            if (
                hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
                != attributes.split()[2]
            ):
                raise RuntimeError("Build input differs from Git: " + name)
            source_hashes[name] = hashlib.sha256(data).hexdigest()
        report["source_hashes"] = source_hashes
        report["build_tools"] = {
            p.name: digest(p) for p in (prepared / "wheelhouse").glob("*.whl")
        }
        exported = output / "locked-requirements.txt"
        run(
            "export",
            [
                "uv",
                "export",
                "--frozen",
                "--offline",
                "--no-dev",
                "--package",
                "friday-chat",
                "--no-editable",
                "--no-annotate",
                "--no-header",
                "--format",
                "requirements-txt",
                "--output-file",
                str(exported),
            ],
        )
        lock = tomllib.loads((source / "uv.lock").read_text())["package"]
        by_key = {(p["name"], p["version"]): p for p in lock}
        by_source = {
            p["source"]["editable"]: p
            for p in lock
            if "editable" in p.get("source", {})
        }
        selected, workspace, constraints = {}, {}, []
        logical = ""
        tag_order = {tag: index for index, tag in enumerate(sys_tags())}
        for line in exported.read_text().splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            logical += " " + stripped.removesuffix("\\")
            if stripped.endswith("\\"):
                continue
            row, logical = logical.strip(), ""
            if row.startswith("./"):
                package = by_source[row.removeprefix("./")]
                workspace[package["name"]] = package
                continue
            requirement_text = row.split(" --hash=", 1)[0].strip()
            constraints.append(requirement_text)
            requirement = Requirement(requirement_text)
            if requirement.marker is not None and not requirement.marker.evaluate(
                default_environment()
            ):
                continue
            versions = [
                item.version for item in requirement.specifier if item.operator == "=="
            ]
            if len(versions) != 1:
                raise RuntimeError("Expected one locked version: " + requirement_text)
            package = by_key[(canonicalize_name(requirement.name), versions[0])]
            hashes = set(re.findall(r"--hash=sha256:([0-9a-f]{64})", row))
            selected[package["name"]] = (package, hashes)
        commands = next(p for p in lock if p["name"] == "friday-framework-commands")
        workspace[commands["name"]] = (
            commands  # standalone lane, even before Chat consumes it
        )
        for package in workspace.values():
            constraints.append(package["name"] + "==" + package["version"])
        constraint_path = output / "default-version-constraints.txt"
        constraint_path.write_text("\n".join(constraints) + "\n")
        third_party = output / "third-party-wheels"
        third_party.mkdir()
        for index, (name, (package, hashes)) in enumerate(sorted(selected.items()), 1):
            compatible = []
            for wheel in package.get("wheels", []):
                filename = Path(unquote(urlsplit(wheel["url"]).path)).name
                tags = parse_wheel_filename(filename)[3]
                ranks = [tag_order[tag] for tag in tags if tag in tag_order]
                if ranks:
                    compatible.append((min(ranks), filename, wheel))
            artifact = (
                min(compatible, key=lambda row: (row[0], row[1]))[2]
                if compatible
                else package.get("sdist")
            )
            if (
                artifact is None
                or artifact["hash"].removeprefix("sha256:") not in hashes
            ):
                raise RuntimeError("No hash-bound target artifact for " + name)
            downloaded = fetch(artifact)
            if compatible:
                (third_party / downloaded.name).write_bytes(downloaded.read_bytes())
            elif name == "pypika" and package["version"] == "0.48.9":
                run(
                    "build-pypika",
                    [
                        "uv",
                        "build",
                        "--wheel",
                        "--offline",
                        "--no-python-downloads",
                        "--out-dir",
                        str(third_party),
                        str(downloaded),
                    ],
                )
                built = list(third_party.glob("*0.48.9*.whl"))
                if len(built) != 1:
                    raise RuntimeError("Expected one PyPika wheel")
                report["source_only_lineage"][name] = {
                    "locked_sdist_sha256": digest(downloaded),
                    "wheel": built[0].name,
                    "wheel_sha256": digest(built[0]),
                    "build_tools": report["build_tools"],
                }
            else:
                raise RuntimeError("Unapproved source-only dependency: " + name)
            if index % 20 == 0:
                print(
                    f"Verified {index}/{len(selected)} locked dependency artifacts",
                    flush=True,
                )
        main_dist, other_dist = output / "g5-dist", output / "workspace-wheels"
        main_dist.mkdir()
        other_dist.mkdir()
        for name, package in sorted(workspace.items()):
            destination = (
                main_dist
                if name in ("friday-chat", "friday-framework-commands")
                else other_dist
            )
            run(
                "build-" + name,
                [
                    "uv",
                    "build",
                    "--offline",
                    "--no-python-downloads",
                    "--package",
                    name,
                    "--out-dir",
                    str(destination),
                ],
            )
            wheels = list(destination.glob(name.replace("-", "_") + "-*.whl"))
            if len(wheels) != 1:
                raise RuntimeError("Expected one workspace wheel: " + name)
            report["workspace_wheels"][name] = {
                "path": str(wheels[0]),
                "sha256": digest(wheels[0]),
                "source": package["source"]["editable"],
            }
        if args.require_pilot_edge:
            chat_wheel = Path(report["workspace_wheels"]["friday-chat"]["path"])
            with zipfile.ZipFile(chat_wheel) as archive:
                metadata = archive.read(
                    next(
                        n
                        for n in archive.namelist()
                        if n.endswith(".dist-info/METADATA")
                    )
                ).decode()
            requirements = [
                Requirement(value)
                for value in email.message_from_string(metadata).get_all(
                    "Requires-Dist", []
                )
            ]
            if not any(
                canonicalize_name(value.name) == "friday-framework-commands"
                and str(value.specifier) == "==0.1.0a4"
                and not value.extras
                and value.marker is None
                for value in requirements
            ):
                raise RuntimeError(
                    "Required unconditional pilot dependency edge missing"
                )
        (output / "default-root.in").write_text("friday-chat==0.1.0a4\n")
        profile = output / "default-profile.txt"
        links = [
            "--find-links",
            str(main_dist),
            "--find-links",
            str(other_dist),
            "--find-links",
            str(third_party),
        ]
        run(
            "compile-profile",
            [
                "uv",
                "pip",
                "compile",
                "--offline",
                "--no-index",
                "--only-binary",
                ":all:",
                "--python",
                sys.executable,
                "--python-version",
                "3.13.10",
                "--generate-hashes",
                "--no-header",
                "--no-annotate",
                *links,
                "--constraint",
                str(constraint_path),
                "--output-file",
                str(profile),
                str(output / "default-root.in"),
            ],
        )
        report["profile_sha256"] = digest(profile)
        for lane in ("neutral", "chat"):
            prefix = output / ("installed-" + lane)
            interpreter = str(prefix / "bin/python")
            run(
                "venv-" + lane,
                [
                    "uv",
                    "venv",
                    "--offline",
                    "--no-python-downloads",
                    "--python",
                    sys.executable,
                    str(prefix),
                ],
            )
            lane_profile = profile
            if lane == "neutral":
                wheel = Path(
                    report["workspace_wheels"]["friday-framework-commands"]["path"]
                )
                lane_profile = output / "neutral-profile.txt"
                lane_profile.write_text(
                    "friday-framework-commands==0.1.0a4 --hash=sha256:"
                    + digest(wheel)
                    + "\n"
                )
            run(
                "install-" + lane,
                [
                    "uv",
                    "pip",
                    "install",
                    "--offline",
                    "--no-index",
                    "--require-hashes",
                    "--no-deps",
                    "--python",
                    interpreter,
                    *links,
                    "-r",
                    str(lane_profile),
                ],
            )
            run(
                "check-" + lane,
                ["uv", "pip", "check", "--offline", "--python", interpreter],
            )
            code = (
                "import sys,runpy\nsys.path.insert(0,"
                + repr(str(prepared))
                + ");runpy.run_path("
                + repr(str(prepared / "sitecustomize.py"))
                + ");sys.path.pop(0)\n"
            )
            if lane == "neutral":
                code += (
                    "import friday_commands; print('isolated neutral import passed')\n"
                )
            else:
                code += "import friday_tools,friday_finance\nfrom friday_chat.commands.registry import build_default_registry\nr=build_default_registry()\nif len(r.canonical_names())!=41 or len(r.command_names())!=44: raise RuntimeError('surface changed')\nprint('isolated default imports and 41/3 catalog passed')\n"
            code += "from pathlib import Path\nfor n,m in tuple(sys.modules.items()):\n if n.startswith('friday') and m is not None and getattr(m,'__file__',None) and not Path(m.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()): raise RuntimeError('installed origin escaped: '+n)\n"
            run("probe-" + lane, [interpreter, "-I", "-c", code])
        report["artifacts"] = {
            str(p.relative_to(output)): digest(p)
            for directory in (main_dist, other_dist, third_party)
            for p in directory.iterdir()
            if p.is_file()
        }
        report["status"] = "passed"
        print(
            f"Closed bundle passed: {len(workspace)} workspace builds, {len(selected)} locked third-party artifacts, both isolated installs",
            flush=True,
        )
    except BaseException as error:
        report["status"] = "failed"
        report["error"] = str(error)
        raise
    finally:
        (output / "bundle-report.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()

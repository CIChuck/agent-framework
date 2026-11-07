"""Prepare an isolated, hash-pinned diagnostic runner; never modify product files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

BASE = "7b80ca01489a52608aafb54b626b74fbb36efbe3"
BUNDLE = "docs/planning/active/command-refactor/validation/retirement/receipts.json"
BUNDLE_HASH = "7d0d557f7e4593110b3eb75a6e191dfa3119a8c980947cf4e57360192adab767"
PINS = {
    "run.py": "409769f1c17a63fcbd7ea2bd3d079af315dcc9afabca8bd35602033c198124af",
    "controls.py": "d62238fd3fac3188f9464604cf091ed2eeb4d9ad76ef21f1f796b3b7af0ba20d",
    "sitecustomize.py": "8365940b2d00a21061c00f671304b29f4c4ba1e9b344a1f4c38c5365de41631f",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scratch", type=Path)
    bootstrap = parser.add_mutually_exclusive_group(required=True)
    bootstrap.add_argument("--fetch-build-tools", action="store_true")
    bootstrap.add_argument("--wheelhouse", type=Path)
    args = parser.parse_args()
    root = Path.cwd().resolve()
    scratch = args.scratch.resolve()
    if scratch == root or scratch.is_relative_to(root):
        raise SystemExit("Scratch must be outside the repository")
    scratch.mkdir(parents=True, exist_ok=True)
    if any(scratch.iterdir()):
        raise SystemExit("Use a fresh, empty scratch directory")
    bundle = (root / BUNDLE).read_bytes()
    if hashlib.sha256(bundle).hexdigest() != BUNDLE_HASH:
        raise SystemExit("Frozen helper receipt changed")
    files = json.loads(bundle)["files"]
    for name, expected in PINS.items():
        content = files[name]["text"].encode()
        if hashlib.sha256(content).hexdigest() != expected:
            raise SystemExit(f"Helper hash mismatch: {name}")
        (scratch / name).write_bytes(content)
    for name in ("config.example.yaml", "models-config.example.yaml"):
        content = subprocess.check_output(
            ["git", "show", f"{BASE}:packages/friday-chat/{name}"]
        )
        (scratch / name).write_bytes(content)
    requirements = Path(__file__).with_name("build-requirements.txt")
    (scratch / "build-requirements.txt").write_bytes(requirements.read_bytes())
    # Keep a closed wheelhouse: uv hash-verified install cache entries alone do
    # not necessarily satisfy an unconstrained, isolated editable-build lookup.
    manifest = Path(__file__).with_name("build-tools.json")
    wheels = json.loads(manifest.read_text())
    wheelhouse = scratch / "wheelhouse"
    wheelhouse.mkdir()
    for wheel in wheels:
        url = wheel["url"]
        if (
            urlsplit(url).scheme != "https"
            or urlsplit(url).hostname != "files.pythonhosted.org"
        ):
            raise SystemExit("Unexpected build-wheel host")
        filename = wheel["filename"]
        if Path(filename).name != filename or not filename.endswith(".whl"):
            raise SystemExit("Invalid build-wheel filename")
        if args.wheelhouse is not None:
            content = (args.wheelhouse / filename).read_bytes()
        else:
            with urllib.request.urlopen(url, timeout=30) as response:
                if urlsplit(response.url).hostname != "files.pythonhosted.org":
                    raise SystemExit("Unexpected build-wheel redirect")
                content = response.read()
        if hashlib.sha256(content).hexdigest() != wheel["sha256"]:
            raise SystemExit(f"Build-wheel hash mismatch: {filename}")
        (wheelhouse / filename).write_bytes(content)
    # Leave the historical runner unchanged. Its wrapper exports an explicit
    # wheel source and disables indexes for every subsequent offline build.
    wrapper = (
        "import os, pathlib, runpy\n"
        "scratch = pathlib.Path(__file__).resolve().parent\n"
        "os.environ['UV_FIND_LINKS'] = str(scratch / 'wheelhouse')\n"
        "os.environ['UV_NO_INDEX'] = '1'\n"
        "os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'\n"
        "runpy.run_path(str(scratch / 'run.py'), run_name='__main__')\n"
    )
    (scratch / "pilot_run.py").write_text(wrapper)
    environment = {
        key: value
        for key, value in os.environ.items()
        if not any(
            word in key.upper()
            for word in ("API_KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")
        )
        and key.upper() not in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY")
    }
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    receipt = {
        "wheel_fetches": wheels,
        "registry_access": args.fetch_build_tools,
        "requirements_sha256": hashlib.sha256(requirements.read_bytes()).hexdigest(),
        "build_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "wrapper_sha256": hashlib.sha256(wrapper.encode()).hexdigest(),
        "helper_hashes": PINS,
    }
    (scratch / "bootstrap.json").write_text(json.dumps(receipt, indent=2) + "\n")
    startup = subprocess.run(
        [
            sys.executable,
            "-B",
            str(scratch / "pilot_run.py"),
            "offline-startup",
            "python",
            "-B",
            "-c",
            "import friday_commands; print('offline editable startup passed')",
        ],
        env=environment,
        check=False,
    )
    if startup.returncode:
        raise SystemExit(startup.returncode)
    print(f"Prepared {scratch}; subsequent runner commands are offline")


if __name__ == "__main__":
    main()

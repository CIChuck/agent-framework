"""Explicit child settings and startup-site qualification, without HOME changes."""

from __future__ import annotations

from pathlib import Path

from ingest.manifests import digest, require
from ingest.paths import physical


def child_environment(root: Path, inherited: dict[str, str]) -> dict[str, str]:
    root = physical(root)
    result = {
        "HOME": inherited.get("HOME", ""),
        "PATH": "/usr/bin:/bin",
        "LANG": "en_US.UTF-8",
        "LC_ALL": "en_US.UTF-8",
        "LITELLM_MODE": "PRODUCTION",
        "LITELLM_LOCAL_MODEL_COST_MAP": "True",
        "GIT_OPTIONAL_LOCKS": "0",
        "UV_NO_CONFIG": "1",
        "UV_NO_ENV_FILE": "1",
        "UV_NO_PYTHON_DOWNLOADS": "1",
        "UV_KEYRING_PROVIDER": "disabled",
        "HF_HUB_DISABLE_TELEMETRY": "1",
        "DO_NOT_TRACK": "1",
    }
    for name, relative in {
        "TMPDIR": "tmp",
        "UV_CACHE_DIR": "uv",
        "UV_CONFIG_DIR": "uv-config",
        "UV_CREDENTIALS_DIR": "credentials",
        "XDG_CACHE_HOME": "xdg-cache",
        "XDG_CONFIG_HOME": "xdg-config",
        "XDG_DATA_HOME": "xdg-data",
        "HF_HOME": "hf",
        "TORCH_HOME": "torch",
        "MYPY_CACHE_DIR": "mypy",
        "NETRC": "empty-netrc",
    }.items():
        result[name] = str(root / relative)
    return result


def startup_inventory(root: Path, site_enabled: bool) -> tuple[dict[str, str], ...]:
    root = physical(root)
    records: list[dict[str, str]] = []
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), "Startup site symlink")
        if not path.is_file() or not (
            path.suffix in {".pth", ".egg-link"}
            or path.name.startswith(("sitecustomize.", "usercustomize."))
        ):
            continue
        raw = path.read_bytes()
        require(len(raw) <= 1024 * 1024, "Startup file exceeds bound")
        classification = "nonexecuted_guarded_data"
        if site_enabled:
            require(path.suffix == ".pth", "Site customization blocks native child")
            for line in raw.decode().splitlines():
                if not line.strip() or line.startswith("#"):
                    continue
                require(
                    not line.startswith(("import ", "import\t")),
                    "Executable startup file blocks native child",
                )
                candidate = (path.parent / line).resolve()
                require(
                    candidate == root or root in candidate.parents,
                    "Startup path leaves owned site",
                )
            classification = "inert_or_owned_path_only"
        records.append(
            {
                "path": str(path.relative_to(root)),
                "sha256": digest(raw),
                "classification": classification,
            }
        )
    return tuple(records)

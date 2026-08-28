"""Regression coverage for lock-step Friday release helpers."""

from __future__ import annotations

import runpy
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import cast

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
METADATA_HELPER = REPOSITORY_ROOT / "scripts" / "check-package-metadata.py"
ARTIFACT_HELPER = REPOSITORY_ROOT / "scripts" / "check-package-artifacts.py"
CHAT_PYPROJECT = REPOSITORY_ROOT / "packages" / "friday-chat" / "pyproject.toml"

CHAT_REQUIREMENTS = (
    "friday-framework-core==0.1.0a1",
    "friday-framework-runtime==0.1.0a1",
    "friday-framework-memory==0.1.0a1",
    "friday-framework-llm==0.1.0a1",
    "friday-framework-agent==0.1.0a1",
    "friday-framework-tools==0.1.0a1",
    "friday-framework-transcript==0.1.0a1",
    "friday-framework-cli==0.1.0a1",
    "friday-framework-speech==0.1.0a1; extra == 'speech'",
    "friday-framework-finance==0.1.0a1; extra == 'finance'",
    "friday-framework-tools[finance]==0.1.0a1; extra == 'finance'",
    "friday-framework-sandbox==0.1.0a1; extra == 'sandbox'",
    "friday-framework-tools[sandbox]==0.1.0a1; extra == 'sandbox'",
    "friday-framework-moltbook==0.1.0a1; extra == 'moltbook'",
    "friday-framework-tools[moltbook]==0.1.0a1; extra == 'moltbook'",
    "friday-framework-finance==0.1.0a1; extra == 'full'",
    "friday-framework-moltbook==0.1.0a1; extra == 'full'",
    "friday-framework-sandbox==0.1.0a1; extra == 'full'",
    "friday-framework-speech==0.1.0a1; extra == 'full'",
    "friday-framework-tools[finance]==0.1.0a1; extra == 'full'",
    "friday-framework-tools[moltbook]==0.1.0a1; extra == 'full'",
    "friday-framework-tools[sandbox]==0.1.0a1; extra == 'full'",
)


def _metadata_validator() -> Callable[..., list[str]]:
    module = runpy.run_path(str(METADATA_HELPER), run_name="release_helper_test")
    return cast(Callable[..., list[str]], module["validate_project"])


def _artifact_validator() -> Callable[..., list[str]]:
    module = runpy.run_path(str(ARTIFACT_HELPER), run_name="release_helper_test")
    return cast(Callable[..., list[str]], module["validate_wheel"])


def _internal_requirement_validator() -> Callable[..., list[str]]:
    module = runpy.run_path(str(ARTIFACT_HELPER), run_name="release_helper_test")
    return cast(
        Callable[..., list[str]],
        module["validate_internal_requirements"],
    )


def test_metadata_helper_accepts_chat_lockstep_matrix() -> None:
    errors = _metadata_validator()(
        CHAT_PYPROJECT,
        expected_version="0.1.0a1",
        internal_version="0.1.0a1",
        internal_pins={},
    )

    assert errors == []


def test_metadata_helper_rejects_wrong_llm_and_self_pins(tmp_path: Path) -> None:
    package = tmp_path / "friday-chat"
    package.mkdir()
    (package / "README.md").write_text("test", encoding="utf-8")
    metadata = CHAT_PYPROJECT.read_text(encoding="utf-8").replace(
        "friday-framework-llm==0.1.0a1",
        "friday-framework-llm==0.1.0a0",
    ).replace(
        "friday-chat[finance,moltbook,sandbox,speech]==0.1.0a1",
        "friday-chat[finance,moltbook,sandbox,speech]==0.1.0a0",
    )
    candidate = package / "pyproject.toml"
    candidate.write_text(metadata, encoding="utf-8")

    errors = _metadata_validator()(
        candidate,
        expected_version="0.1.0a1",
        internal_version="0.1.0a1",
        internal_pins={},
    )

    assert any("friday-framework-llm==0.1.0a0" in error for error in errors)
    assert any("friday-chat[finance" in error for error in errors)


def _write_wheel(
    directory: Path,
    *,
    requirements: tuple[str, ...] = CHAT_REQUIREMENTS,
    entry_point: str = "friday-chat = friday_chat.cli:app\n",
) -> None:
    wheel = directory / "friday_chat-0.1.0a1-py3-none-any.whl"
    requirement_lines = "".join(
        f"Requires-Dist: {requirement}\n" for requirement in requirements
    )
    metadata = (
        "Metadata-Version: 2.4\n"
        "Name: friday-chat\n"
        "Version: 0.1.0a1\n"
        "License: MIT\n"
        "Description-Content-Type: text/markdown\n"
        "Project-URL: Repository, https://github.com/CIChuck/agent-framework\n"
        f"{requirement_lines}\nFriday Chat test artifact.\n"
    )
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("friday_chat/__init__.py", "__version__ = '0.1.0a1'\n")
        archive.writestr(
            "friday_chat/config_templates/config.example.yaml",
            "llm:\n  model: openai/test\n",
        )
        archive.writestr(
            "friday_chat/config_templates/cli-config.example.yaml",
            "banner:\n  enabled: true\n",
        )
        archive.writestr("friday_chat-0.1.0a1.dist-info/METADATA", metadata)
        archive.writestr(
            "friday_chat-0.1.0a1.dist-info/entry_points.txt",
            f"[console_scripts]\n{entry_point}",
        )


def _validate_wheel(directory: Path) -> list[str]:
    return _artifact_validator()(
        "friday_chat",
        "friday_chat",
        directory,
        "0.1.0a1",
    )


def test_artifact_helper_accepts_chat_dependencies_resources_and_entry_point(
    tmp_path: Path,
) -> None:
    _write_wheel(tmp_path)

    assert _validate_wheel(tmp_path) == []


def test_artifact_helper_rejects_wrong_llm_pin_and_entry_point(
    tmp_path: Path,
) -> None:
    requirements = tuple(
        requirement.replace(
            "friday-framework-llm==0.1.0a1",
            "friday-framework-llm==0.1.0a0",
        )
        for requirement in CHAT_REQUIREMENTS
    )
    _write_wheel(tmp_path, requirements=requirements, entry_point="")

    errors = _validate_wheel(tmp_path)

    assert any("friday-framework-llm==0.1.0a1" in error for error in errors)
    assert any("console entry point missing" in error for error in errors)


def test_artifact_helper_rejects_stale_pin_for_any_internal_requirement() -> None:
    errors = _internal_requirement_validator()(
        "synthetic.whl",
        {
            "friday-framework-memory==0.1.0a0",
            "friday-framework-tools[finance]==0.1.0a1; extra == 'finance'",
            "pydantic>=2.0",
        },
        "0.1.0a1",
    )

    assert errors == [
        "synthetic.whl: internal dependency is not pinned to 0.1.0a1: "
        "friday-framework-memory==0.1.0a0"
    ]

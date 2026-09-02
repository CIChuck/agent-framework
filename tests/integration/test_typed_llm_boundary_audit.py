"""Checked allowlist for compatibility-only Friday LLM call boundaries."""

from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPOSITORY_ROOT / "packages"

ALLOWED_DIRECT_CONSTRUCTORS = Counter(
    {
        ("packages/friday-chat/src/friday_chat/adapters.py", "LiteLLMService"): 7,
        (
            "packages/friday-chat/src/friday_chat/adapters.py",
            "LiteLLMEmbeddingService",
        ): 1,
        (
            "packages/friday-chat/src/friday_chat/reorganization/mutation.py",
            "LiteLLMService",
        ): 1,
        (
            "packages/friday-chat/src/friday_chat/reorganization/mutation.py",
            "LiteLLMEmbeddingService",
        ): 1,
        (
            "packages/friday-memory/src/friday_memory/ingestion/large_file_processor.py",
            "LiteLLMService",
        ): 1,
        (
            "packages/friday-memory/src/friday_memory/maintenance/__main__.py",
            "LiteLLMService",
        ): 1,
        ("packages/friday-runtime/src/friday_runtime/di.py", "LiteLLMService"): 1,
        (
            "packages/friday-runtime/src/friday_runtime/di.py",
            "LiteLLMEmbeddingService",
        ): 1,
    }
)

ALLOWED_LEGACY_CALLS = Counter(
    {
        ("packages/friday-agent/src/friday_agent/llm_completion.py", "chat_completion"): 1,
        ("packages/friday-chat/src/friday_chat/adapters.py", "chat_completion"): 1,
        (
            "packages/friday-memory/src/friday_memory/llm_completion.py",
            "chat_completion",
        ): 2,
        ("packages/friday-tools/src/friday_tools/codegen/tool.py", "chat_completion"): 1,
    }
)


def test_direct_provider_construction_is_confined_to_compatibility_paths() -> None:
    calls = _source_calls({"LiteLLMService", "LiteLLMEmbeddingService"})

    assert calls == ALLOWED_DIRECT_CONSTRUCTORS


def test_legacy_chat_completion_is_confined_to_compatibility_adapters() -> None:
    calls = _source_calls({"chat_completion"})

    assert calls == ALLOWED_LEGACY_CALLS


def _source_calls(names: set[str]) -> Counter[tuple[str, str]]:
    calls: Counter[tuple[str, str]] = Counter()
    for path in sorted(SOURCE_ROOT.glob("*/src/**/*.py")):
        if "friday-llm" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            call_name = _call_name(node)
            if call_name in names:
                calls[(relative, call_name)] += 1
    return calls


def _call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""

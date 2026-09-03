"""Strict local-file loading for Friday LLM model libraries."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from friday_llm import ModelLibrary

MAX_MODEL_LIBRARY_BYTES = 1024 * 1024
MAX_MODEL_LIBRARY_DEPTH = 12
MAX_MODEL_LIBRARY_NODES = 10_000
MAX_MODEL_LIBRARY_STRING = 4096


class ModelLibraryLoadError(ValueError):
    """Raised when a model-library file violates Runtime loading policy."""


@dataclass(frozen=True, slots=True)
class LoadedModelLibrary:
    """Validated catalog and the canonical path used to load it."""

    path: Path
    library: ModelLibrary


class _StrictLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""

    def construct_mapping(
        self,
        node: yaml.MappingNode,
        deep: bool = False,
    ) -> dict[object, object]:
        seen: set[object] = set()
        for key_node, _ in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                raise ModelLibraryLoadError("YAML merge keys are not allowed")
            key = self.construct_object(key_node, deep=False)
            try:
                duplicate = key in seen
            except TypeError as error:
                raise ModelLibraryLoadError("mapping keys must be scalar") from error
            if duplicate:
                raise ModelLibraryLoadError(f"duplicate YAML mapping key: {key!r}")
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


def load_model_library(
    configured_path: str,
    *,
    runtime_config_path: str | Path,
    environment: Mapping[str, str],
    allow_env_override: bool,
) -> LoadedModelLibrary:
    """Load one bounded local model library relative to its Runtime YAML."""

    selected_path = configured_path
    if allow_env_override:
        override = environment.get("FRIDAY_MODELS_CONFIG")
        if override is not None and override.strip():
            selected_path = override
    resolved_path = _resolve_catalog_path(
        selected_path,
        runtime_config_path=Path(runtime_config_path),
    )
    try:
        file_size = resolved_path.stat().st_size
    except OSError as error:
        raise ModelLibraryLoadError(
            f"unable to inspect model library: {resolved_path}"
        ) from error
    if file_size > MAX_MODEL_LIBRARY_BYTES:
        raise ModelLibraryLoadError(
            f"model library exceeds {MAX_MODEL_LIBRARY_BYTES} bytes"
        )
    try:
        document = resolved_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ModelLibraryLoadError(
            f"unable to read model library: {resolved_path}"
        ) from error
    _reject_yaml_references(document)
    try:
        payload = yaml.load(document, Loader=_StrictLoader)
    except ModelLibraryLoadError:
        raise
    except yaml.YAMLError as error:
        raise ModelLibraryLoadError("invalid model-library YAML") from error
    if not isinstance(payload, dict):
        raise ModelLibraryLoadError("model library must be a YAML mapping")
    _validate_structure_bounds(payload)
    try:
        library = ModelLibrary.model_validate(payload)
    except ValueError as error:
        raise ModelLibraryLoadError("invalid model-library schema") from error
    return LoadedModelLibrary(path=resolved_path, library=library)


def _resolve_catalog_path(
    configured_path: str,
    *,
    runtime_config_path: Path,
) -> Path:
    if not configured_path.strip():
        raise ModelLibraryLoadError("model_library.path must be non-empty")
    parsed = urlsplit(configured_path)
    if parsed.scheme or parsed.netloc:
        raise ModelLibraryLoadError("model_library.path must be a local file path")
    raw_path = Path(configured_path).expanduser()
    candidate = (
        raw_path
        if raw_path.is_absolute()
        else runtime_config_path.expanduser().resolve().parent / raw_path
    )
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise ModelLibraryLoadError(
            f"model library does not exist: {candidate}"
        ) from error
    if not resolved.is_file():
        raise ModelLibraryLoadError(
            f"model library is not a regular file: {resolved}"
        )
    return resolved


def _reject_yaml_references(document: str) -> None:
    try:
        events = yaml.parse(document, Loader=yaml.SafeLoader)
        for event in events:
            if isinstance(event, yaml.AliasEvent) or getattr(event, "anchor", None):
                raise ModelLibraryLoadError(
                    "YAML anchors and aliases are not allowed"
                )
    except ModelLibraryLoadError:
        raise
    except yaml.YAMLError as error:
        raise ModelLibraryLoadError("invalid model-library YAML") from error


def _validate_structure_bounds(payload: dict[object, object]) -> None:
    nodes = 0
    pending: list[tuple[object, int]] = [(payload, 1)]
    while pending:
        value, depth = pending.pop()
        nodes += 1
        if nodes > MAX_MODEL_LIBRARY_NODES:
            raise ModelLibraryLoadError(
                f"model library exceeds {MAX_MODEL_LIBRARY_NODES} YAML nodes"
            )
        if depth > MAX_MODEL_LIBRARY_DEPTH:
            raise ModelLibraryLoadError(
                f"model library exceeds YAML depth {MAX_MODEL_LIBRARY_DEPTH}"
            )
        if isinstance(value, str) and len(value) > MAX_MODEL_LIBRARY_STRING:
            raise ModelLibraryLoadError(
                f"model library string exceeds {MAX_MODEL_LIBRARY_STRING} characters"
            )
        if isinstance(value, dict):
            for key, child in value.items():
                pending.append((key, depth + 1))
                pending.append((child, depth + 1))
        elif isinstance(value, list):
            for child in value:
                pending.append((child, depth + 1))

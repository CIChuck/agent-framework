"""Checked MCP consumer output and request copies; raw inputs stay transient."""

from __future__ import annotations

import html
import json
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any, Literal
from uuid import uuid4

from friday_core.mcp import MCPSafeIdentifier, MCPToolCallProvenance, MCPToolMetadata
from friday_core.security import SanitizationConfig, ToolOutputSanitizer
from pydantic import TypeAdapter, ValidationError

from friday_chat.tools.schemas import ToolCallRecord

FailureCode = Literal[
    "tool_error", "invalid_result", "execution_error", "timeout", "output_rejected"
]
_OPEN = '<untrusted_content source="mcp">\n'
_CLOSE = "\n</untrusted_content>"
_NOTICE = "\n[MCP result truncated]"
_FAILURE = "[MCP execution failed]"
_BLOCKED = "[MCP output blocked]"
_REDACTED = "[REDACTED]"
_ID = TypeAdapter(MCPSafeIdentifier)


class MCPResultLimitError(RuntimeError):
    """A requested call cannot produce a complete safe result at this cap."""

    def __init__(self) -> None:
        super().__init__("MCP result limit is too small for safe execution.")


def safe_mcp_call_id(call_id: str | None, used: set[str]) -> str:
    """Preserve only validated, unique IDs; never echo invalid input."""
    try:
        candidate = _ID.validate_python(call_id)
    except ValidationError:
        candidate = ""
    while not candidate or candidate in used:
        candidate = "mcp-" + uuid4().hex
    used.add(candidate)
    return candidate


def reconcile_mcp_call_ids(
    records: list[ToolCallRecord],
    messages: list[dict[str, Any]],
    native_ids: set[str],
    used: set[str],
) -> None:
    """Rebind completed MCP facts when a later native request claims their ID.

    Only turn-owned safe history is changed; completed tools are never rerun.
    Native IDs are retained, and records plus request/result copies move together
    before the next model invocation or persistence. Prior wire requests were
    paired at submission time and cannot be retroactively changed.
    """
    used.update(native_ids)
    used.update(record.call_id for record in records if record.call_id is not None)
    replacements: dict[tuple[str, str], str] = {}
    for index, record in enumerate(records):
        facts = record.mcp_provenance
        if facts is None or facts.call_id not in native_ids:
            continue
        identifier = safe_mcp_call_id(None, used)
        replacements[(record.name, facts.call_id)] = identifier
        records[index] = replace(
            record,
            call_id=identifier,
            mcp_provenance=MCPToolCallProvenance.model_validate(
                {**facts.model_dump(), "call_id": identifier}
            ),
        )
    if not replacements:
        return
    for message in messages:
        if message.get("role") == "tool":
            name = message.get("name")
            message_id = message.get("tool_call_id")
            if isinstance(name, str) and isinstance(message_id, str):
                replacement = replacements.get((name, message_id))
                if replacement is not None:
                    message["tool_call_id"] = replacement
        elif message.get("role") == "assistant":
            calls = message.get("tool_calls")
            if not isinstance(calls, list):
                continue
            for call in calls:
                if not isinstance(call, dict):
                    continue
                function = call.get("function")
                name = (
                    function.get("name")
                    if isinstance(function, Mapping)
                    else call.get("name")
                )
                request_id = call.get("id")
                if isinstance(name, str) and isinstance(request_id, str):
                    replacement = replacements.get((name, request_id))
                    if replacement is not None:
                        call["id"] = replacement


class MCPOutputPolicy:
    """Uses the public sanitizer, then bounds the complete escaped envelope."""

    def __init__(self, max_result_bytes: int) -> None:
        self.max_result_bytes = max_result_bytes
        capacity = max(1000, max_result_bytes * 4)
        self._sanitizer = ToolOutputSanitizer(
            SanitizationConfig.model_validate(
                {
                    "enabled": True,
                    "detection": {
                        "enabled": True,
                        "sensitivity": "high",
                        "max_scan_length": capacity,
                    },
                    "normalization": {
                        "enabled": True,
                        "max_normalize_length": capacity,
                    },
                    "wrapping": {"enabled": False},
                    "quarantine": {
                        "action": "block",
                        "redaction_text": _BLOCKED,
                        "log_detections": False,
                    },
                    "storage_policy": {
                        "store_raw_on_detection": False,
                        "raw_store_mode": "drop",
                    },
                }
            )
        )
        # Canonicalize transient argument tokens solely for removal. This
        # helper never produces model-facing output or safety claims.
        configuration = self._sanitizer.config
        self._argument_normalizer = ToolOutputSanitizer(
            configuration.model_copy(
                update={
                    "detection": configuration.detection.model_copy(
                        update={"enabled": False}
                    ),
                }
            )
        )

    def require_usable_limit(self) -> None:
        """Check before RPC; no record is fabricated for a rejected request."""
        minimum = len((_OPEN + _FAILURE + _NOTICE + _CLOSE).encode("utf-8"))
        if self.max_result_bytes < minimum:
            raise MCPResultLimitError()

    def failed_record(
        self, tool: MCPToolMetadata, call_id: str, failure_code: FailureCode
    ) -> ToolCallRecord:
        """Failure records have fixed content and no exception/peer payload."""
        self.require_usable_limit()
        blocked = failure_code == "output_rejected"
        result = _OPEN + (_BLOCKED if blocked else _FAILURE) + _CLOSE
        provenance = MCPToolCallProvenance(
            tool=tool,
            call_id=call_id,
            status="blocked" if blocked else "failed",
            output_sanitization_state="rejected" if blocked else "sanitized",
            model_result_size_bytes=len(result.encode("utf-8")),
            failure_code=failure_code,
        )
        return ToolCallRecord(tool.canonical_name, {}, result, call_id, provenance)

    def checked_record(
        self,
        tool: MCPToolMetadata,
        call_id: str,
        output: str,
        arguments: Mapping[str, Any],
    ) -> ToolCallRecord:
        """Scan all retained text, redact argument echoes, and bound final text."""
        self.require_usable_limit()
        try:
            encoded = output.encode("utf-8")
        except UnicodeError:
            return self.failed_record(tool, call_id, "invalid_result")
        original_size = len(encoded)
        retained = encoded[: self.max_result_bytes].decode("utf-8", errors="ignore")
        truncated = len(retained.encode("utf-8")) < original_size
        # Raw-bearing sanitizer facts are local only, never retained in the record.
        checked = self._sanitizer.sanitize(retained, tool.canonical_name, "mcp")
        rejected = bool(checked.detections)
        normalized = checked.sanitized_content
        del checked
        if not rejected:
            normalized = self._redact_argument_echoes(normalized, arguments, truncated)
        result, final_cut = self._envelope(normalized, truncated)
        provenance = MCPToolCallProvenance(
            tool=tool,
            call_id=call_id,
            status="blocked" if rejected else "succeeded",
            output_sanitization_state="rejected" if rejected else "sanitized",
            result_truncated=truncated or final_cut,
            result_size_bytes=original_size,
            model_result_size_bytes=len(result.encode("utf-8")),
            failure_code="output_rejected" if rejected else None,
        )
        return ToolCallRecord(tool.canonical_name, {}, result, call_id, provenance)

    def _redact_argument_echoes(
        self,
        text: str,
        arguments: Mapping[str, Any],
        truncated: bool,
    ) -> str:
        """Drop known argument keys/values echoed by a peer, without retaining them."""
        tokens: set[str] = set()

        def collect(value: object) -> None:
            if isinstance(value, Mapping):
                for key, item in value.items():
                    collect(key)
                    collect(item)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    collect(item)
            elif isinstance(value, (str, int, float, bool)) or value is None:
                literal = value if isinstance(value, str) else json.dumps(value)
                if literal:
                    normalized = self._argument_normalizer.sanitize(
                        literal, "mcp", "mcp"
                    )
                    tokens.add(literal)
                    tokens.add(json.dumps(literal, ensure_ascii=True)[1:-1])
                    if normalized.sanitized_content:
                        tokens.add(normalized.sanitized_content)
                    del normalized

        collect(arguments)
        # A byte cut may leave only the beginning of an echoed long argument.
        # Remove that suffix before full-token replacement; the fixed replacement
        # is never recursively treated as an argument token.
        overlap = (
            max((self._partial_suffix(text, token) for token in tokens), default=0)
            if truncated
            else 0
        )
        suffix = _REDACTED if overlap else ""
        if overlap:
            text = text[:-overlap]
        # One substitution pass prevents the fixed replacement becoming input to
        # a later token replacement (and avoids recursive replacement growth).
        if tokens:
            import re

            pattern = "|".join(
                re.escape(token)
                for token in sorted(tokens, key=len, reverse=True)
                if len(token) <= len(text)
            )
            if pattern:
                text = re.sub(pattern, lambda _: _REDACTED, text)
        return text + suffix

    @staticmethod
    def _partial_suffix(text: str, token: str) -> int:
        """Linear bounded suffix/prefix match, including escaped JSON tokens."""
        sequence: list[str | None] = [*token[: len(text)], None, *text]
        lengths = [0] * len(sequence)
        for index in range(1, len(sequence)):
            matched = lengths[index - 1]
            while matched and sequence[index] != sequence[matched]:
                matched = lengths[matched - 1]
            if sequence[index] == sequence[matched]:
                matched += 1
            lengths[index] = matched
        return lengths[-1]

    def _envelope(self, text: str, truncated: bool) -> tuple[str, bool]:
        escaped = html.escape(text)
        full = _OPEN + escaped + (_NOTICE if truncated else "") + _CLOSE
        if len(full.encode("utf-8")) <= self.max_result_bytes:
            return full, False
        budget = self.max_result_bytes - len((_OPEN + _NOTICE + _CLOSE).encode("utf-8"))
        chunks: list[str] = []
        used = 0
        for character in text:
            chunk = html.escape(character)
            size = len(chunk.encode("utf-8"))
            if used + size > budget:
                break
            chunks.append(chunk)
            used += size
        return _OPEN + "".join(chunks) + _NOTICE + _CLOSE, True


def redact_tool_request_message(
    message: Mapping[str, Any],
    records: Sequence[ToolCallRecord],
    mcp_names: set[str],
) -> dict[str, Any]:
    """Copy a model request for continuation/capture, matching records by order."""
    raw_calls = message.get("tool_calls", [])
    if not isinstance(raw_calls, list):
        return dict(message)
    pending: dict[str, list[ToolCallRecord]] = {}
    for record in records:
        if record.mcp_provenance is not None:
            pending.setdefault(record.name, []).append(record)
    safe_calls: list[object] = []
    mcp_request = False
    used = {record.call_id for record in records if record.call_id is not None}
    for raw in raw_calls:
        if not isinstance(raw, Mapping):
            safe_calls.append(raw)
            continue
        function = raw.get("function")
        name = (
            function.get("name") if isinstance(function, Mapping) else raw.get("name")
        )
        if not isinstance(name, str) or name not in mcp_names:
            safe_calls.append(raw)
            continue
        mcp_request = True
        call: dict[str, Any] = {}
        matched = pending.get(str(name), [])
        if matched:
            call["id"] = matched.pop(0).call_id
        else:
            raw_id = raw.get("id")
            call["id"] = safe_mcp_call_id(
                raw_id if isinstance(raw_id, str) else None, used
            )
        if isinstance(function, Mapping):
            call["type"] = "function"
            call["function"] = {"name": name, "arguments": "{}"}
        else:
            call["name"] = name
            call["arguments"] = {}
        safe_calls.append(call)
    if mcp_request:
        # Model request prose/reasoning may contain the same raw arguments.
        return {"role": "assistant", "content": "", "tool_calls": safe_calls}
    return dict(message)

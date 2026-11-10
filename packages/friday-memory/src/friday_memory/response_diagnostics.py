"""Bounded structured-response evidence without provider content or reasoning."""

from __future__ import annotations

import re
from dataclasses import dataclass

from pydantic import BaseModel, ValidationError

_FINISH_REASONS = frozenset(
    {
        "stop",
        "length",
        "max_tokens",
        "model_length",
        "content_filter",
        "tool_calls",
        "function_call",
    }
)
_ISSUE_CODES = frozenset(
    {
        "missing",
        "extra_forbidden",
        "enum",
        "float_type",
        "float_parsing",
        "int_type",
        "int_parsing",
        "bool_type",
        "string_type",
        "string_too_short",
        "string_too_long",
        "tuple_type",
        "list_type",
        "dict_type",
        "too_long",
        "too_short",
        "greater_than_equal",
        "less_than_equal",
        "value_error",
    }
)


@dataclass(frozen=True, slots=True)
class ResponseValidationIssue:
    """Only trusted schema field names, array positions and categorical codes."""

    path: tuple[str | int, ...]
    code: str


@dataclass(frozen=True, slots=True)
class ResponseDiagnostic:
    """Safe evidence assembled by response_diagnostic at a provider boundary."""

    role: str
    configured_model: str
    schema: str
    finish_reason: str
    issues: tuple[ResponseValidationIssue, ...] = ()

    def summary(self) -> str:
        fields = (
            f"role={self.role}; model={self.configured_model}; "
            f"schema={self.schema}; finish_reason={self.finish_reason}"
        )
        if self.issues:
            details = ",".join(
                f"{'.'.join(str(part) for part in issue.path) or '$'}:{issue.code}"
                for issue in self.issues
            )
            fields += f"; issues={details}"
        return fields


def _identifier(value: str, limit: int) -> str:
    if len(value) <= limit and re.fullmatch(r"[A-Za-z0-9_./:+@-]+", value):
        return value
    return "unavailable"


def _schema_node(node: object, root: dict[str, object]) -> dict[str, object]:
    """Follow local schema references only; unknown paths stay redacted."""
    seen: set[str] = set()
    while isinstance(node, dict):
        reference = node.get("$ref")
        if reference is None:
            return node
        if (
            not isinstance(reference, str)
            or not reference.startswith("#/")
            or reference in seen
        ):
            break
        seen.add(reference)
        node = root
        for part in reference[2:].split("/"):
            if not isinstance(node, dict):
                return {}
            node = node.get(part.replace("~1", "/").replace("~0", "~"))
    return {}


def _validation_path(
    location: tuple[str | int, ...], root: dict[str, object]
) -> tuple[str | int, ...]:
    node: object = root
    path: list[str | int] = []
    for part in location[:6]:
        current = _schema_node(node, root)
        if isinstance(part, str):
            properties = current.get("properties")
            if isinstance(properties, dict) and part in properties:
                path.append(
                    part if _identifier(part, 64) != "unavailable" else "<field>"
                )
                node = properties[part]
            else:
                path.append("<field>")
                node = current.get("additionalProperties")
        else:
            prefixes = current.get("prefixItems")
            if isinstance(prefixes, list) and 0 <= part < len(prefixes):
                node = prefixes[part]
            else:
                node = current.get("items")
            is_array = current.get("type") == "array"
            path.append(part if is_array and 0 <= part <= 100_000 else "<index>")
    return tuple(path)


def response_diagnostic(
    *,
    role: str,
    configured_model: str,
    response_model: type[BaseModel],
    finish_reason: str | None,
    error: ValidationError | None = None,
) -> ResponseDiagnostic:
    """Redact unknown response keys and omit validation inputs/messages/context."""
    schema = response_model.model_json_schema()
    issues = []
    if error is not None:
        for issue in error.errors(
            include_input=False, include_context=False, include_url=False
        )[:5]:
            path = _validation_path(issue["loc"], schema)
            code = issue["type"]
            issues.append(
                ResponseValidationIssue(
                    path, code if code in _ISSUE_CODES else "validation_error"
                )
            )
    reason = (
        finish_reason.strip().lower() if finish_reason is not None else "unavailable"
    )
    return ResponseDiagnostic(
        role=_identifier(role, 32),
        configured_model=_identifier(configured_model, 192),
        schema=_identifier(response_model.__name__, 64),
        finish_reason=reason
        if reason in _FINISH_REASONS
        else ("unavailable" if finish_reason is None else "other"),
        issues=tuple(issues),
    )

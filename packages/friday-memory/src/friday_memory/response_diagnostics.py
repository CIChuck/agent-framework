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


def response_diagnostic(
    *,
    role: str,
    configured_model: str,
    response_model: type[BaseModel],
    finish_reason: str | None,
    error: ValidationError | None = None,
) -> ResponseDiagnostic:
    """Redact unknown response keys and omit validation inputs/messages/context."""
    allowed_fields: set[str] = set()

    def collect_fields(node: object) -> None:
        if isinstance(node, dict):
            properties = node.get("properties")
            if isinstance(properties, dict):
                allowed_fields.update(properties)
            for child in node.values():
                collect_fields(child)
        elif isinstance(node, list):
            for child in node:
                collect_fields(child)

    collect_fields(response_model.model_json_schema())
    issues = []
    if error is not None:
        for issue in error.errors(
            include_input=False, include_context=False, include_url=False
        )[:5]:
            path = tuple(
                (part if 0 <= part <= 100_000 else "<index>")
                if isinstance(part, int)
                else (
                    part
                    if part in allowed_fields and _identifier(part, 64) != "unavailable"
                    else "<field>"
                )
                for part in issue["loc"][:6]
            )
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

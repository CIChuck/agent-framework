"""Safe projection at the dynamic LiteLLM boundary; no raw payload is delivered."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import litellm
from friday_telemetry.helpers.safe_llm import RequestTracker, SafeLLMTelemetry
from friday_telemetry.interface import TelemetryInterface
from friday_telemetry.models.llm_events import (
    LLMAPI,
    CostMetrics,
    ErrorCategory,
    FinishReason,
    ServiceRole,
    UsageMetrics,
)

from friday_llm.exceptions import (
    CircuitBreakerOpenError,
    LLMConfigurationError,
    LLMRetryExhaustedError,
    LLMTimeoutError,
)
from friday_llm.pricing import CostCalculator


def classify_error(error: BaseException) -> ErrorCategory:
    """Classify known types without messages, arbitrary class names or properties."""
    # Only our exact wrapper class has trusted metadata; never inspect a foreign
    # exception's last_error/property merely to report it.
    if type(error) is LLMRetryExhaustedError:
        return classify_error(error.last_error)
    if isinstance(error, (TimeoutError, LLMTimeoutError, litellm.Timeout)):
        return "timeout"
    if isinstance(error, CircuitBreakerOpenError):
        return "circuit_open"
    if isinstance(error, litellm.RateLimitError):
        return "rate_limit"
    if isinstance(error, litellm.AuthenticationError):
        return "authentication"
    if isinstance(error, (LLMConfigurationError, litellm.BadRequestError)):
        return "invalid_request"
    if isinstance(error, litellm.APIConnectionError):
        return "network"
    if isinstance(error, (litellm.ServiceUnavailableError, litellm.InternalServerError)):
        return "model"
    return "unknown"


def usage_from_raw(raw: Any, *, embedding: bool = False) -> UsageMetrics:
    """Preserve presence at this dynamic SDK boundary, before application defaults."""
    if raw is None:
        return UsageMetrics()
    names = {"input_tokens": "prompt_tokens", "total_tokens": "total_tokens"}
    if not embedding:
        names["output_tokens"] = "completion_tokens"
    try:
        counts: dict[str, int] = {}
        for target, source in names.items():
            value = raw.get(source) if isinstance(raw, Mapping) else getattr(raw, source, None)
            if value is None:
                continue
            if type(value) is not int or not 0 <= value <= 2**63 - 1:
                return UsageMetrics(usage_state="invalid")
            counts[target] = value
        if not embedding:
            details = (raw.get("completion_tokens_details") if isinstance(raw, Mapping)
                       else getattr(raw, "completion_tokens_details", None))
            value = (details.get("reasoning_tokens") if isinstance(details, Mapping)
                     else getattr(details, "reasoning_tokens", None))
            if value is not None:
                if type(value) is not int or not 0 <= value <= 2**63 - 1:
                    return UsageMetrics(usage_state="invalid")
                counts["reasoning_tokens"] = value
        if (all(key in counts for key in ("input_tokens", "output_tokens", "total_tokens"))
                and counts["input_tokens"] + counts["output_tokens"] != counts["total_tokens"]):
            return UsageMetrics(usage_state="invalid")
        if counts.get("reasoning_tokens", 0) > counts.get("output_tokens", 2**63 - 1):
            return UsageMetrics(usage_state="invalid")
        if (embedding and all(k in counts for k in ("input_tokens", "total_tokens"))
                and counts["total_tokens"] < counts["input_tokens"]):
            return UsageMetrics(usage_state="invalid")
        return UsageMetrics(usage_state="reported" if counts else "unavailable",
                            input_tokens=counts.get("input_tokens"),
                            output_tokens=counts.get("output_tokens"),
                            total_tokens=counts.get("total_tokens"),
                            reasoning_tokens=counts.get("reasoning_tokens"))
    except Exception:
        return UsageMetrics(usage_state="invalid")


def response_usage(response: Any, *, embedding: bool = False) -> UsageMetrics:
    try:
        return usage_from_raw(getattr(response, "usage", None), embedding=embedding)
    except Exception:
        return UsageMetrics(usage_state="invalid")


def finish_reason(value: object) -> FinishReason | None:
    if value is None:
        return None
    if isinstance(value, str):
        if value == "stop":
            return "stop"
        if value == "length":
            return "length"
        if value == "tool_calls":
            return "tool_calls"
        if value == "content_filter":
            return "content_filter"
    return "other"


class LiteLLMMetrics:
    def __init__(self, telemetry: TelemetryInterface | None, calculator: CostCalculator,
                 model: str, *, service_role: ServiceRole = "unspecified") -> None:
        self.safe = SafeLLMTelemetry(telemetry, service_role=service_role)
        self.calculator = calculator
        self.model = model

    def request(self, api: LLMAPI) -> RequestTracker:
        def estimate(usage: UsageMetrics) -> CostMetrics:
            if usage.input_tokens is None:
                return CostMetrics()
            output = 0 if api.startswith("embedding_") else usage.output_tokens
            if output is None:
                return CostMetrics()
            return self.calculator.estimate_with_provenance(self.model, usage.input_tokens, output)
        return self.safe.request(api, classify=classify_error, estimate=estimate)

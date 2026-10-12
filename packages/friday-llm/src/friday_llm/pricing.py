"""
Model Pricing Configuration and Cost Calculator.

Provides configurable pricing lookup and per-request cost estimation.

Ref: Batch 3 Specification - Telemetry
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite

from friday_telemetry.models.llm_events import CostMetrics, PriceMatch, PriceSource
from pydantic import BaseModel, Field

from friday_llm.telemetry_models import CostEstimate


@dataclass(frozen=True)
class ModelPricing:
    """Pricing for a specific model."""

    input_cost_per_1k: float  # USD per 1000 input tokens
    output_cost_per_1k: float  # USD per 1000 output tokens
    context_window: int | None = None
    notes: str | None = None


# Default pricing as of early 2025 (easily overridable)
DEFAULT_MODEL_PRICING: dict[str, ModelPricing] = {
    # OpenAI Chat Models
    "gpt-4": ModelPricing(0.03, 0.06, 8192),
    "gpt-4-32k": ModelPricing(0.06, 0.12, 32768),
    "gpt-4-turbo": ModelPricing(0.01, 0.03, 128000),
    "gpt-4-turbo-preview": ModelPricing(0.01, 0.03, 128000),
    "gpt-4o": ModelPricing(0.005, 0.015, 128000),
    "gpt-4o-mini": ModelPricing(0.00015, 0.0006, 128000),
    "gpt-3.5-turbo": ModelPricing(0.0005, 0.0015, 16385),
    "gpt-3.5-turbo-16k": ModelPricing(0.001, 0.002, 16385),
    # Anthropic Chat Models
    "claude-3-opus": ModelPricing(0.015, 0.075, 200000),
    "claude-3-opus-20240229": ModelPricing(0.015, 0.075, 200000),
    "claude-3-sonnet": ModelPricing(0.003, 0.015, 200000),
    "claude-3-sonnet-20240229": ModelPricing(0.003, 0.015, 200000),
    "claude-3-haiku": ModelPricing(0.00025, 0.00125, 200000),
    "claude-3-haiku-20240307": ModelPricing(0.00025, 0.00125, 200000),
    "claude-3-5-sonnet": ModelPricing(0.003, 0.015, 200000),
    "claude-3-5-sonnet-20240620": ModelPricing(0.003, 0.015, 200000),
    "claude-3-5-haiku": ModelPricing(0.001, 0.005, 200000),
    # OpenAI Embedding Models
    "text-embedding-3-small": ModelPricing(0.00002, 0.0, None),
    "text-embedding-3-large": ModelPricing(0.00013, 0.0, None),
    "text-embedding-ada-002": ModelPricing(0.0001, 0.0, None),
    # Cohere Embedding Models
    "embed-english-v3.0": ModelPricing(0.0001, 0.0, None),
    "embed-multilingual-v3.0": ModelPricing(0.0001, 0.0, None),
    # Local models (free)
    "ollama": ModelPricing(0.0, 0.0, None, "Local Ollama models"),
    "lmstudio": ModelPricing(0.0, 0.0, None, "Local LM Studio models"),
}


class PricingConfig(BaseModel):
    """
    Configurable pricing settings.

    Allows custom pricing overrides and unknown model handling.

    Example:
        config = PricingConfig(
            custom_pricing={
                "my-fine-tuned-model": {
                    "input_cost_per_1k": 0.02,
                    "output_cost_per_1k": 0.04,
                }
            }
        )
    """

    custom_pricing: dict[str, dict[str, float]] = Field(
        default_factory=dict,
        description="Custom pricing: {model: {input_cost_per_1k, output_cost_per_1k}}",
    )
    estimate_unknown: bool = Field(
        default=True,
        description="Estimate cost for unknown models using fallback",
    )
    fallback_input_cost: float = Field(
        default=0.01,
        ge=0.0,
        description="Fallback input cost per 1k tokens for unknown models",
    )
    fallback_output_cost: float = Field(
        default=0.03,
        ge=0.0,
        description="Fallback output cost per 1k tokens for unknown models",
    )
    enabled: bool = Field(default=True, description="Enable cost estimation")


class CostCalculator:
    """
    Calculates cost estimates for LLM operations.

    Uses a built-in pricing table with support for custom overrides.

    Example:
        calculator = CostCalculator()
        cost = calculator.calculate(
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500,
        )
        print(f"Total: ${cost.total_cost:.4f}")

        # With custom pricing
        config = PricingConfig(
            custom_pricing={"my-model": {"input_cost_per_1k": 0.01}}
        )
        calculator = CostCalculator(config)
    """

    def __init__(
        self,
        config: PricingConfig | None = None,
        pricing_table: dict[str, ModelPricing] | None = None,
    ) -> None:
        """
        Initialize cost calculator.

        Args:
            config: Pricing configuration with custom overrides
            pricing_table: Optional custom pricing table (replaces defaults)
        """
        self.config = config or PricingConfig()
        self._pricing = (
            pricing_table.copy() if pricing_table else DEFAULT_MODEL_PRICING.copy()
        )
        source: PriceSource = "supplied_table" if pricing_table else "builtin_2025"
        self._price_sources: dict[str, PriceSource] = dict.fromkeys(self._pricing, source)

        # Apply custom overrides from config
        for model, prices in self.config.custom_pricing.items():
            self._price_sources[model] = "custom_config"
            self._pricing[model] = ModelPricing(
                input_cost_per_1k=prices.get("input_cost_per_1k", 0.01),
                output_cost_per_1k=prices.get("output_cost_per_1k", 0.03),
            )

    def get_pricing(self, model: str) -> ModelPricing | None:
        """
        Get pricing for a model, handling provider prefixes.

        Args:
            model: Model name (e.g., "gpt-4", "openai/gpt-4", "ollama/llama2")

        Returns:
            ModelPricing if found, None otherwise
        """
        found = self._lookup_with_provenance(model)
        return found[0] if found is not None else None

    def _lookup_with_provenance(
        self, model: str,
    ) -> tuple[ModelPricing, PriceSource, PriceMatch] | None:
        # Preserve the legacy matching order and effective numeric prices.
        if model in self._pricing:
            return self._pricing[model], self._price_sources[model], "exact"

        # Try without provider prefix (e.g., "openai/gpt-4" -> "gpt-4")
        if "/" in model:
            parts = model.split("/")
            provider = parts[0].lower()
            base_model = parts[1] if len(parts) > 1 else ""

            # Check for provider-level pricing (e.g., "ollama" for all Ollama models)
            if provider in self._pricing:
                return self._pricing[provider], self._price_sources[provider], "provider"

            # Check base model
            if base_model in self._pricing:
                return self._pricing[base_model], self._price_sources[base_model], "base_model"

        # Try partial match for versioned models (e.g., "gpt-4-0613" matches "gpt-4")
        model_lower = model.lower()
        for key in sorted(self._pricing.keys(), key=len, reverse=True):
            if model_lower.startswith(key.lower()):
                return self._pricing[key], self._price_sources[key], "prefix"

        return None

    def estimate_with_provenance(
        self, model: str, input_tokens: int, output_tokens: int = 0,
    ) -> CostMetrics:
        """A local estimate with historical/config provenance, never actual billing.

        Unavailable and invalid estimates carry no fabricated zero cost. Raw model
        and pricing-table keys do not appear in this public safe projection.
        """
        if not self.config.enabled:
            return CostMetrics()
        if any(type(n) is not int or not 0 <= n <= 2**63 - 1
               for n in (input_tokens, output_tokens)):
            return CostMetrics(cost_state="invalid")
        found = self._lookup_with_provenance(model)
        if found is None:
            if not self.config.estimate_unknown:
                return CostMetrics()
            rates = ModelPricing(self.config.fallback_input_cost, self.config.fallback_output_cost)
            source: PriceSource = "fallback"
            match: PriceMatch = "fallback"
        else:
            rates, source, match = found
        pair = (rates.input_cost_per_1k, rates.output_cost_per_1k)
        if any(not isfinite(rate) or rate < 0 for rate in pair):
            return CostMetrics(cost_state="invalid")
        input_cost = (input_tokens / 1000) * pair[0]
        output_cost = (output_tokens / 1000) * pair[1]
        total = input_cost + output_cost
        if not all(isfinite(value) for value in (input_cost, output_cost, total)):
            return CostMetrics(cost_state="invalid")
        # Hash only numeric rates and closed categories, never a model/config name.
        reference = sha256(f"{pair[0]!r}:{pair[1]!r}:{source}:{match}".encode()).hexdigest()[:16]
        return CostMetrics(cost_state="estimated", input_cost_usd=round(input_cost, 8),
                           output_cost_usd=round(output_cost, 8), total_cost_usd=round(total, 8),
                           currency="USD", price_source=source, price_match=match,
                           pricing_ref=reference)

    def calculate(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int = 0,
    ) -> CostEstimate:
        """
        Calculate cost estimate for token usage.

        Args:
            model: Model name/identifier
            input_tokens: Number of input/prompt tokens
            output_tokens: Number of output/completion tokens

        Returns:
            CostEstimate with breakdown
        """
        if not self.config.enabled:
            return CostEstimate()

        pricing = self.get_pricing(model)

        if pricing:
            input_cost = (input_tokens / 1000) * pricing.input_cost_per_1k
            output_cost = (output_tokens / 1000) * pricing.output_cost_per_1k
            pricing_model = model
        elif self.config.estimate_unknown:
            input_cost = (input_tokens / 1000) * self.config.fallback_input_cost
            output_cost = (output_tokens / 1000) * self.config.fallback_output_cost
            pricing_model = f"{model} (estimated)"
        else:
            return CostEstimate()

        return CostEstimate(
            input_cost=round(input_cost, 8),
            output_cost=round(output_cost, 8),
            total_cost=round(input_cost + output_cost, 8),
            currency="USD",
            pricing_model=pricing_model,
        )

    def get_available_models(self) -> list[str]:
        """Get list of models with known pricing."""
        return sorted(self._pricing.keys())

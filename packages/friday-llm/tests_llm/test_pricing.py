"""
Tests for LLM Pricing and Cost Calculator.

Tests cost estimation with built-in and custom pricing.
"""

import pytest
from friday_llm.pricing import (
    DEFAULT_MODEL_PRICING,
    CostCalculator,
    ModelPricing,
    PricingConfig,
)


class TestModelPricing:
    """Tests for ModelPricing dataclass."""

    def test_creation(self):
        """Test creating model pricing."""
        pricing = ModelPricing(
            input_cost_per_1k=0.03,
            output_cost_per_1k=0.06,
            context_window=8192,
        )
        assert pricing.input_cost_per_1k == 0.03
        assert pricing.output_cost_per_1k == 0.06
        assert pricing.context_window == 8192
        assert pricing.notes is None

    def test_immutable(self):
        """Test that ModelPricing is immutable (frozen)."""
        pricing = ModelPricing(0.03, 0.06)
        with pytest.raises(AttributeError):
            pricing.input_cost_per_1k = 0.05


class TestPricingConfig:
    """Tests for PricingConfig model."""

    def test_default_values(self):
        """Test default pricing config values."""
        config = PricingConfig()
        assert config.custom_pricing == {}
        assert config.estimate_unknown is True
        assert config.fallback_input_cost == 0.01
        assert config.fallback_output_cost == 0.03
        assert config.enabled is True

    def test_custom_pricing(self):
        """Test setting custom pricing."""
        config = PricingConfig(
            custom_pricing={
                "my-model": {
                    "input_cost_per_1k": 0.02,
                    "output_cost_per_1k": 0.04,
                }
            }
        )
        assert "my-model" in config.custom_pricing
        assert config.custom_pricing["my-model"]["input_cost_per_1k"] == 0.02

    def test_disabled_estimation(self):
        """Test disabling unknown model estimation."""
        config = PricingConfig(estimate_unknown=False)
        assert config.estimate_unknown is False


class TestDefaultPricing:
    """Tests for built-in pricing table."""

    def test_openai_models_present(self):
        """Test OpenAI models are in default pricing."""
        assert "gpt-4" in DEFAULT_MODEL_PRICING
        assert "gpt-4o" in DEFAULT_MODEL_PRICING
        assert "gpt-4o-mini" in DEFAULT_MODEL_PRICING
        assert "gpt-3.5-turbo" in DEFAULT_MODEL_PRICING

    def test_anthropic_models_present(self):
        """Test Anthropic models are in default pricing."""
        assert "claude-3-opus" in DEFAULT_MODEL_PRICING
        assert "claude-3-sonnet" in DEFAULT_MODEL_PRICING
        assert "claude-3-haiku" in DEFAULT_MODEL_PRICING
        assert "claude-3-5-sonnet" in DEFAULT_MODEL_PRICING

    def test_embedding_models_present(self):
        """Test embedding models are in default pricing."""
        assert "text-embedding-3-small" in DEFAULT_MODEL_PRICING
        assert "text-embedding-3-large" in DEFAULT_MODEL_PRICING

    def test_local_models_free(self):
        """Test local models have zero cost."""
        assert DEFAULT_MODEL_PRICING["ollama"].input_cost_per_1k == 0.0
        assert DEFAULT_MODEL_PRICING["ollama"].output_cost_per_1k == 0.0
        assert DEFAULT_MODEL_PRICING["lmstudio"].input_cost_per_1k == 0.0


class TestCostCalculator:
    """Tests for CostCalculator."""

    def test_exact_model_match(self):
        """Test cost calculation with exact model match."""
        calculator = CostCalculator()
        cost = calculator.calculate(
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500,
        )

        # gpt-4: $0.03/1k input, $0.06/1k output
        expected_input = 1.0 * 0.03  # 0.03
        expected_output = 0.5 * 0.06  # 0.03
        assert cost.input_cost == pytest.approx(expected_input, rel=1e-6)
        assert cost.output_cost == pytest.approx(expected_output, rel=1e-6)
        assert cost.total_cost == pytest.approx(
            expected_input + expected_output, rel=1e-6
        )
        assert cost.currency == "USD"
        assert cost.pricing_model == "gpt-4"

    def test_provider_prefix_stripped(self):
        """Test model names with provider prefix."""
        calculator = CostCalculator()

        # openai/gpt-4 should match gpt-4
        cost = calculator.calculate(
            model="openai/gpt-4",
            input_tokens=1000,
            output_tokens=0,
        )
        assert cost.pricing_model == "openai/gpt-4"  # Uses exact input
        assert cost.input_cost == pytest.approx(0.03, rel=1e-6)

    def test_ollama_provider_match(self):
        """Test Ollama models match provider-level pricing."""
        calculator = CostCalculator()

        cost = calculator.calculate(
            model="ollama/llama2",
            input_tokens=10000,
            output_tokens=5000,
        )
        # Ollama is free
        assert cost.total_cost == 0.0

    def test_versioned_model_match(self):
        """Test versioned model names match base model."""
        calculator = CostCalculator()

        cost = calculator.calculate(
            model="gpt-4-0613",
            input_tokens=1000,
            output_tokens=500,
        )
        # Should match gpt-4 pricing
        assert cost.pricing_model == "gpt-4-0613"

    def test_unknown_model_with_estimation(self):
        """Test unknown model uses fallback pricing."""
        calculator = CostCalculator()

        cost = calculator.calculate(
            model="some-unknown-model",
            input_tokens=1000,
            output_tokens=500,
        )

        # Uses fallback: $0.01/1k input, $0.03/1k output
        assert cost.input_cost == pytest.approx(0.01, rel=1e-6)
        assert cost.output_cost == pytest.approx(0.015, rel=1e-6)
        assert "estimated" in cost.pricing_model.lower()

    def test_unknown_model_without_estimation(self):
        """Test unknown model returns empty cost when estimation disabled."""
        config = PricingConfig(estimate_unknown=False)
        calculator = CostCalculator(config)

        cost = calculator.calculate(
            model="some-unknown-model",
            input_tokens=1000,
            output_tokens=500,
        )

        # Returns empty cost
        assert cost.total_cost == 0.0
        assert cost.pricing_model is None

    def test_disabled_calculator(self):
        """Test disabled calculator returns empty cost."""
        config = PricingConfig(enabled=False)
        calculator = CostCalculator(config)

        cost = calculator.calculate(
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500,
        )

        assert cost.total_cost == 0.0

    def test_custom_pricing_override(self):
        """Test custom pricing overrides defaults."""
        config = PricingConfig(
            custom_pricing={
                "gpt-4": {
                    "input_cost_per_1k": 0.05,  # Override default
                    "output_cost_per_1k": 0.10,
                }
            }
        )
        calculator = CostCalculator(config)

        cost = calculator.calculate(
            model="gpt-4",
            input_tokens=1000,
            output_tokens=1000,
        )

        assert cost.input_cost == pytest.approx(0.05, rel=1e-6)
        assert cost.output_cost == pytest.approx(0.10, rel=1e-6)

    def test_custom_model_pricing(self):
        """Test adding custom model pricing."""
        config = PricingConfig(
            custom_pricing={
                "my-fine-tuned-model": {
                    "input_cost_per_1k": 0.02,
                    "output_cost_per_1k": 0.04,
                }
            }
        )
        calculator = CostCalculator(config)

        cost = calculator.calculate(
            model="my-fine-tuned-model",
            input_tokens=1000,
            output_tokens=1000,
        )

        assert cost.input_cost == pytest.approx(0.02, rel=1e-6)
        assert cost.output_cost == pytest.approx(0.04, rel=1e-6)
        assert cost.pricing_model == "my-fine-tuned-model"

    def test_get_pricing_exact_match(self):
        """Test get_pricing with exact match."""
        calculator = CostCalculator()
        pricing = calculator.get_pricing("gpt-4")

        assert pricing is not None
        assert pricing.input_cost_per_1k == 0.03
        assert pricing.output_cost_per_1k == 0.06

    def test_get_pricing_not_found(self):
        """Test get_pricing returns None for unknown model."""
        calculator = CostCalculator()
        pricing = calculator.get_pricing("nonexistent-model")

        assert pricing is None

    def test_get_available_models(self):
        """Test listing available models."""
        calculator = CostCalculator()
        models = calculator.get_available_models()

        assert len(models) > 0
        assert "gpt-4" in models
        assert "claude-3-opus" in models
        assert models == sorted(models)  # Should be sorted

    def test_embedding_model_pricing(self):
        """Test embedding model cost calculation."""
        calculator = CostCalculator()

        cost = calculator.calculate(
            model="text-embedding-3-small",
            input_tokens=10000,
            output_tokens=0,  # Embeddings have no output
        )

        # text-embedding-3-small: $0.00002/1k input
        expected = 10.0 * 0.00002
        assert cost.input_cost == pytest.approx(expected, rel=1e-6)
        assert cost.output_cost == 0.0

    def test_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        calculator = CostCalculator()

        cost = calculator.calculate(
            model="gpt-4",
            input_tokens=0,
            output_tokens=0,
        )

        assert cost.total_cost == 0.0

    def test_custom_pricing_table(self):
        """Test using completely custom pricing table."""
        custom_table = {
            "model-a": ModelPricing(0.01, 0.02),
            "model-b": ModelPricing(0.02, 0.04),
        }
        calculator = CostCalculator(pricing_table=custom_table)

        # Custom table is used
        cost = calculator.calculate("model-a", 1000, 1000)
        assert cost.input_cost == pytest.approx(0.01, rel=1e-6)
        assert cost.output_cost == pytest.approx(0.02, rel=1e-6)

        # Default models not available
        pricing = calculator.get_pricing("gpt-4")
        assert pricing is None

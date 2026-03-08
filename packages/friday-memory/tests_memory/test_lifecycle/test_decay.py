# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
# mypy: disallow-untyped-defs=False
"""
Tests for DecayConfig and DecayCalculator.

Tests cover:
- DecayConfig model validation
- DecayConfig promotion weight validation
- DecayCalculator exponential decay formula
- Access boost calculation
- Threshold checks (promotion and decay)
- Eligibility calculations
- Hours until decay estimation
"""

from datetime import datetime, timedelta

import pytest
from friday_memory.lifecycle.decay import DecayCalculator, DecayConfig


class TestDecayConfig:
    """Test DecayConfig model."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = DecayConfig()
        assert config.enabled
        assert config.decay_rate == 0.01
        assert config.access_boost == 0.2
        assert config.promotion_threshold == 0.7
        assert config.decay_threshold == 0.2
        assert config.short_term_min_age_hours == 24
        assert config.decay_check_interval_hours == 24
        assert config.decayed_retention_days == 30

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = DecayConfig(
            enabled=False,
            decay_rate=0.02,
            access_boost=0.3,
            promotion_threshold=0.8,
            decay_threshold=0.1,
            short_term_min_age_hours=48,
        )
        assert not config.enabled
        assert config.decay_rate == 0.02
        assert config.access_boost == 0.3
        assert config.promotion_threshold == 0.8
        assert config.decay_threshold == 0.1
        assert config.short_term_min_age_hours == 48

    def test_decay_rate_bounds(self) -> None:
        """Test decay_rate has valid bounds."""
        # Valid bounds
        config = DecayConfig(decay_rate=0.001)
        assert config.decay_rate == 0.001

        config = DecayConfig(decay_rate=0.5)
        assert config.decay_rate == 0.5

        # Invalid - too low
        with pytest.raises(ValueError):
            DecayConfig(decay_rate=0.0)

        # Invalid - too high
        with pytest.raises(ValueError):
            DecayConfig(decay_rate=0.6)

    def test_access_boost_bounds(self) -> None:
        """Test access_boost has valid bounds."""
        # Valid bounds
        config = DecayConfig(access_boost=0.0)
        assert config.access_boost == 0.0

        config = DecayConfig(access_boost=0.5)
        assert config.access_boost == 0.5

        # Invalid - too high
        with pytest.raises(ValueError):
            DecayConfig(access_boost=0.6)

    def test_promotion_weight_defaults(self) -> None:
        """Test default promotion weights."""
        config = DecayConfig()
        assert config.promotion_weight_age == 0.2
        assert config.promotion_weight_access == 0.4
        assert config.promotion_weight_confidence == 0.2
        assert config.promotion_weight_connection == 0.2

    def test_promotion_weights_must_sum_to_one(self) -> None:
        """Test that promotion weights must sum to 1.0."""
        # Valid - sums to 1.0
        config = DecayConfig(
            promotion_weight_age=0.25,
            promotion_weight_access=0.25,
            promotion_weight_confidence=0.25,
            promotion_weight_connection=0.25,
        )
        assert config.promotion_weight_age == 0.25

        # Invalid - sums to less than 1.0
        with pytest.raises(ValueError, match="must sum to 1.0"):
            DecayConfig(
                promotion_weight_age=0.1,
                promotion_weight_access=0.1,
                promotion_weight_confidence=0.1,
                promotion_weight_connection=0.1,  # Sum = 0.4
            )

        # Invalid - sums to more than 1.0
        with pytest.raises(ValueError, match="must sum to 1.0"):
            DecayConfig(
                promotion_weight_age=0.4,
                promotion_weight_access=0.4,
                promotion_weight_confidence=0.4,
                promotion_weight_connection=0.4,  # Sum = 1.6
            )

    def test_get_promotion_weights(self) -> None:
        """Test get_promotion_weights returns dictionary."""
        config = DecayConfig()
        weights = config.get_promotion_weights()

        assert weights == {
            "age": 0.2,
            "access": 0.4,
            "confidence": 0.2,
            "connection": 0.2,
        }


class TestDecayCalculator:
    """Test DecayCalculator class."""

    @pytest.fixture
    def config(self):
        """Create default decay config."""
        return DecayConfig()

    @pytest.fixture
    def calculator(self, config):
        """Create calculator with default config."""
        return DecayCalculator(config)

    @pytest.fixture
    def now(self):
        """Fixed timestamp for testing."""
        return datetime(2024, 1, 15, 12, 0, 0)

    def test_config_property(self, calculator, config) -> None:
        """Test config property returns configuration."""
        assert calculator.config is config

    def test_calculate_decay_fresh_memory(self, calculator, now) -> None:
        """Fresh memory should have minimal decay."""
        last_accessed = now - timedelta(hours=1)
        score = calculator.calculate_decay(1.0, last_accessed, now)

        # At 1 hour with decay_rate=0.01: exp(-0.01 * 1) ≈ 0.99
        assert 0.98 < score < 1.0

    def test_calculate_decay_day_old_memory(self, calculator, now) -> None:
        """Day-old memory should have moderate decay."""
        last_accessed = now - timedelta(hours=24)
        score = calculator.calculate_decay(1.0, last_accessed, now)

        # At 24 hours with decay_rate=0.01: exp(-0.01 * 24) ≈ 0.79
        assert 0.78 < score < 0.80

    def test_calculate_decay_week_old_memory(self, calculator, now) -> None:
        """Week-old memory should have significant decay."""
        last_accessed = now - timedelta(hours=168)  # 7 days
        score = calculator.calculate_decay(1.0, last_accessed, now)

        # At 168 hours with decay_rate=0.01: exp(-0.01 * 168) ≈ 0.19
        assert 0.18 < score < 0.20

    def test_calculate_decay_from_partial_score(self, calculator, now) -> None:
        """Decay should apply to current score, not just 1.0."""
        last_accessed = now - timedelta(hours=24)

        # Starting from 0.5
        score = calculator.calculate_decay(0.5, last_accessed, now)

        # 0.5 * exp(-0.01 * 24) ≈ 0.5 * 0.79 ≈ 0.395
        assert 0.38 < score < 0.40

    def test_calculate_decay_disabled(self, now) -> None:
        """When decay is disabled, score should not change."""
        config = DecayConfig(enabled=False)
        calculator = DecayCalculator(config)

        last_accessed = now - timedelta(days=30)
        score = calculator.calculate_decay(0.8, last_accessed, now)

        assert score == 0.8

    def test_calculate_decay_clamps_to_valid_range(self, calculator, now) -> None:
        """Decay should keep score in [0.0, 1.0] range."""
        last_accessed = now - timedelta(days=365)  # Very old

        # Should not go below 0.0
        score = calculator.calculate_decay(1.0, last_accessed, now)
        assert score >= 0.0
        assert score <= 1.0

    def test_calculate_decay_default_now(self, calculator) -> None:
        """Test decay uses current time when now is not provided."""
        # This should not raise an error
        score = calculator.calculate_decay(1.0, datetime.now() - timedelta(hours=1))
        assert score > 0.0

    def test_apply_access_boost(self, calculator) -> None:
        """Access boost should increase score."""
        original = 0.5
        boosted = calculator.apply_access_boost(original)

        # 0.5 + 0.2 (default boost) = 0.7
        assert boosted == 0.7

    def test_apply_access_boost_caps_at_one(self, calculator) -> None:
        """Access boost should not exceed 1.0."""
        original = 0.9
        boosted = calculator.apply_access_boost(original)

        # Would be 1.1 but capped at 1.0
        assert boosted == 1.0

    def test_apply_access_boost_disabled(self) -> None:
        """When decay is disabled, boost should not apply."""
        config = DecayConfig(enabled=False)
        calculator = DecayCalculator(config)

        boosted = calculator.apply_access_boost(0.5)
        assert boosted == 0.5

    def test_should_promote_above_threshold(self, calculator) -> None:
        """Score >= promotion_threshold should promote."""
        assert calculator.should_promote(0.7)
        assert calculator.should_promote(0.8)
        assert calculator.should_promote(1.0)

    def test_should_promote_below_threshold(self, calculator) -> None:
        """Score < promotion_threshold should not promote."""
        assert not calculator.should_promote(0.69)
        assert not calculator.should_promote(0.5)
        assert not calculator.should_promote(0.0)

    def test_should_decay_below_threshold(self, calculator) -> None:
        """Score < decay_threshold should decay."""
        assert calculator.should_decay(0.19)
        assert calculator.should_decay(0.1)
        assert calculator.should_decay(0.0)

    def test_should_decay_above_threshold(self, calculator) -> None:
        """Score >= decay_threshold should not decay."""
        assert not calculator.should_decay(0.2)
        assert not calculator.should_decay(0.5)
        assert not calculator.should_decay(1.0)

    def test_is_eligible_for_promotion_check_young(self, calculator, now) -> None:
        """Memory younger than min_age should not be eligible."""
        created_at = now - timedelta(hours=12)  # Only 12 hours old

        assert not calculator.is_eligible_for_promotion_check(created_at, now)

    def test_is_eligible_for_promotion_check_old_enough(self, calculator, now) -> None:
        """Memory older than min_age should be eligible."""
        created_at = now - timedelta(hours=25)  # 25 hours old

        assert calculator.is_eligible_for_promotion_check(created_at, now)

    def test_is_eligible_for_promotion_check_exactly_at_threshold(
        self, calculator, now
    ) -> None:
        """Memory exactly at min_age should be eligible."""
        created_at = now - timedelta(hours=24)  # Exactly 24 hours

        assert calculator.is_eligible_for_promotion_check(created_at, now)

    def test_is_eligible_for_promotion_check_default_now(self, calculator) -> None:
        """Test eligibility uses current time when now is not provided."""
        created_at = datetime.now() - timedelta(hours=25)

        # Should not raise an error
        result = calculator.is_eligible_for_promotion_check(created_at)
        assert result is True

    def test_calculate_hours_until_decay_above_threshold(self, calculator, now) -> None:
        """Should return hours until decay threshold is reached."""
        last_accessed = now - timedelta(hours=1)

        hours = calculator.calculate_hours_until_decay(1.0, last_accessed, now)

        # Should be a positive number
        assert hours is not None
        assert hours > 0

    def test_calculate_hours_until_decay_already_below(self, calculator, now) -> None:
        """Should return None if already below threshold."""
        last_accessed = now - timedelta(hours=1)

        hours = calculator.calculate_hours_until_decay(0.1, last_accessed, now)

        # Already below 0.2 threshold
        assert hours is None

    def test_calculate_hours_until_decay_disabled(self, now) -> None:
        """Should return None when decay is disabled."""
        config = DecayConfig(enabled=False)
        calculator = DecayCalculator(config)

        hours = calculator.calculate_hours_until_decay(
            1.0, now - timedelta(hours=1), now
        )
        assert hours is None

    def test_calculate_hours_until_decay_mathematical_accuracy(self, now) -> None:
        """Test the mathematical accuracy of hours until decay."""
        # Use specific decay rate for easier calculation
        config = DecayConfig(decay_rate=0.01, decay_threshold=0.2)
        calculator = DecayCalculator(config)

        last_accessed = now  # Just accessed now
        hours = calculator.calculate_hours_until_decay(1.0, last_accessed, now)

        # Solve: 1.0 * exp(-0.01 * t) = 0.2
        # t = -ln(0.2) / 0.01 ≈ 160.9 hours
        assert hours is not None
        assert 160 < hours < 162


class TestDecayCalculatorEdgeCases:
    """Test edge cases for DecayCalculator."""

    def test_very_high_decay_rate(self) -> None:
        """Test with maximum allowed decay rate."""
        config = DecayConfig(decay_rate=0.5)
        calculator = DecayCalculator(config)
        now = datetime.now()

        # After just 1 hour: exp(-0.5 * 1) ≈ 0.61
        score = calculator.calculate_decay(1.0, now - timedelta(hours=1), now)
        assert 0.6 < score < 0.62

    def test_very_low_decay_rate(self) -> None:
        """Test with minimum allowed decay rate."""
        config = DecayConfig(decay_rate=0.001)
        calculator = DecayCalculator(config)
        now = datetime.now()

        # After 24 hours: exp(-0.001 * 24) ≈ 0.976
        score = calculator.calculate_decay(1.0, now - timedelta(hours=24), now)
        assert 0.97 < score < 0.98

    def test_custom_thresholds(self) -> None:
        """Test with custom promotion and decay thresholds."""
        config = DecayConfig(
            promotion_threshold=0.9,  # Higher bar
            decay_threshold=0.3,  # Higher floor
        )
        calculator = DecayCalculator(config)

        # Promotion requires higher score
        assert not calculator.should_promote(0.85)
        assert calculator.should_promote(0.9)

        # Decay threshold is higher
        assert calculator.should_decay(0.25)
        assert not calculator.should_decay(0.3)

    def test_zero_access_boost(self) -> None:
        """Test with zero access boost."""
        config = DecayConfig(access_boost=0.0)
        calculator = DecayCalculator(config)

        boosted = calculator.apply_access_boost(0.5)
        assert boosted == 0.5

    def test_custom_min_age_hours(self) -> None:
        """Test with custom minimum age for promotion."""
        config = DecayConfig(short_term_min_age_hours=48)  # 2 days
        calculator = DecayCalculator(config)
        now = datetime.now()

        # 36 hours old - not eligible
        assert not calculator.is_eligible_for_promotion_check(
            now - timedelta(hours=36), now
        )

        # 48 hours old - eligible
        assert calculator.is_eligible_for_promotion_check(
            now - timedelta(hours=48), now
        )

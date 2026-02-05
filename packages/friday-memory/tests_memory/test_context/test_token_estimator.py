"""Tests for token estimator selection and approximation."""

import math

from friday_memory.context.token_estimator import (
    ApproxTokenEstimator,
    TiktokenEstimator,
    build_token_estimator,
)


def test_build_token_estimator_defaults_to_approx() -> None:
    estimator = build_token_estimator(None, model_name="gpt-4")
    assert isinstance(estimator, ApproxTokenEstimator)


def test_approx_estimator_counts_with_overhead() -> None:
    estimator = ApproxTokenEstimator(chars_per_token=4.0, overhead_pct=0.15)
    expected = math.ceil((4 / 4.0) * 1.15)
    assert estimator.count("abcd") == expected
    assert estimator.count("") == 0


def test_build_token_estimator_tiktoken() -> None:
    estimator = build_token_estimator({"strategy": "tiktoken"}, model_name="gpt-4")
    assert isinstance(estimator, TiktokenEstimator)

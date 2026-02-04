"""
Security utilities for prompt injection mitigation.

This module provides:
- ToolOutputSanitizer: Main class for sanitizing tool outputs
- SanitizationConfig: Configuration for sanitization behavior
- InjectionPatternLibrary: Detection patterns for known attacks
- UntrustedContentMarker: Content wrapping utilities
- QuarantineStore: Raw output quarantine storage
"""

from .config import (
    CategoryRiskMapping,
    DetectionConfig,
    NormalizationConfig,
    QuarantineConfig,
    RiskLevel,
    SanitizationConfig,
    StoragePolicyConfig,
    WrappingConfig,
    DEFAULT_SANITIZATION_CONFIG,
)
from .markers import ContentMetadata, UntrustedContentMarker
from .patterns import InjectionPattern, InjectionPatternLibrary
from .quarantine import QuarantineRecord, QuarantineStore
from .sanitizer import SanitizationResult, ToolOutputSanitizer

__all__ = [
    # Config
    "SanitizationConfig",
    "DetectionConfig",
    "NormalizationConfig",
    "WrappingConfig",
    "QuarantineConfig",
    "StoragePolicyConfig",
    "CategoryRiskMapping",
    "RiskLevel",
    "DEFAULT_SANITIZATION_CONFIG",
    # Patterns
    "InjectionPattern",
    "InjectionPatternLibrary",
    # Markers
    "ContentMetadata",
    "UntrustedContentMarker",
    # Quarantine
    "QuarantineStore",
    "QuarantineRecord",
    # Sanitizer
    "ToolOutputSanitizer",
    "SanitizationResult",
]

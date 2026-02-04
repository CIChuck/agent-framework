"""
Prompt injection sanitization configuration models.

Defines Pydantic models for configuring detection, normalization,
wrapping, quarantine actions, and storage policies.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class RiskLevel(str, Enum):
    """Risk level classification for tools and content."""

    CRITICAL = "critical"  # External untrusted: web, shell output
    HIGH = "high"          # External: filesystem reads
    MEDIUM = "medium"      # Mixed: git, database queries
    LOW = "low"            # Internal: text manipulation
    MINIMAL = "minimal"    # Pure internal: datetime, echo


class CategoryRiskMapping(BaseModel):
    """Maps tool categories to default risk levels."""

    web: RiskLevel = Field(default=RiskLevel.CRITICAL)
    shell: RiskLevel = Field(default=RiskLevel.CRITICAL)
    filesystem: RiskLevel = Field(default=RiskLevel.HIGH)
    git: RiskLevel = Field(default=RiskLevel.MEDIUM)
    code: RiskLevel = Field(default=RiskLevel.MEDIUM)
    data: RiskLevel = Field(default=RiskLevel.MEDIUM)
    text: RiskLevel = Field(default=RiskLevel.LOW)
    utility: RiskLevel = Field(default=RiskLevel.MINIMAL)
    uncategorized: RiskLevel = Field(default=RiskLevel.HIGH)


class DetectionConfig(BaseModel):
    """Configuration for injection pattern detection."""

    enabled: bool = Field(default=True)
    sensitivity: Literal["low", "medium", "high", "paranoid"] = Field(default="medium")
    max_scan_length: int = Field(default=100_000, ge=1000)
    custom_patterns: list[str] = Field(default_factory=list)
    allowlist_patterns: list[str] = Field(default_factory=list)


class NormalizationConfig(BaseModel):
    """Configuration for content normalization before scanning."""

    enabled: bool = Field(default=True)
    max_normalize_length: int = Field(default=200_000, ge=1000)
    strip_zero_width: bool = Field(default=True)
    decode_html_entities: bool = Field(default=True)
    strip_html_comments: bool = Field(default=True)
    collapse_whitespace: bool = Field(default=True)


class WrappingConfig(BaseModel):
    """Configuration for content wrapping/marking."""

    enabled: bool = Field(default=True)
    marker_style: Literal["xml", "fence", "prefix"] = Field(default="xml")
    include_metadata: bool = Field(default=True)


class StoragePolicyConfig(BaseModel):
    """Policy for storing tool outputs when detections occur."""

    store_sanitized: bool = Field(default=True)
    store_raw_on_detection: bool = Field(default=False)
    raw_store_mode: Literal["quarantine", "drop"] = Field(default="quarantine")
    quarantine_path: str | None = Field(
        default=None,
        description="Optional JSONL file path for quarantined raw outputs",
    )


class QuarantineConfig(BaseModel):
    """Configuration for detected injection handling."""

    action: Literal["warn", "redact", "block", "log_only"] = Field(default="warn")
    redaction_text: str = Field(
        default="[CONTENT REDACTED: Potential injection detected]"
    )
    log_detections: bool = Field(default=True)


class SanitizationConfig(BaseModel):
    """
    Complete sanitization configuration.

    Example YAML:
        security:
          sanitization:
            enabled: true
            detection:
              sensitivity: "medium"
            wrapping:
              marker_style: "xml"
            quarantine:
              action: "warn"
    """

    enabled: bool = Field(default=True)
    detection: DetectionConfig = Field(default_factory=DetectionConfig)
    normalization: NormalizationConfig = Field(default_factory=NormalizationConfig)
    wrapping: WrappingConfig = Field(default_factory=WrappingConfig)
    quarantine: QuarantineConfig = Field(default_factory=QuarantineConfig)
    storage_policy: StoragePolicyConfig = Field(default_factory=StoragePolicyConfig)
    category_risks: CategoryRiskMapping = Field(default_factory=CategoryRiskMapping)
    tool_overrides: dict[str, RiskLevel] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_storage_policy(self) -> "SanitizationConfig":
        """Validate storage policy requirements for quarantine."""
        policy = self.storage_policy
        if (
            policy.store_raw_on_detection
            and policy.raw_store_mode == "quarantine"
            and not policy.quarantine_path
        ):
            raise ValueError(
                "storage_policy.quarantine_path is required when "
                "store_raw_on_detection is true and raw_store_mode is 'quarantine'."
            )
        return self

    @classmethod
    def from_dict(cls, data: dict | None) -> "SanitizationConfig":
        """Load from dictionary (e.g., YAML section)."""
        if not data:
            return cls()
        return cls(
            enabled=data.get("enabled", True),
            detection=DetectionConfig(**data.get("detection", {})),
            normalization=NormalizationConfig(**data.get("normalization", {})),
            wrapping=WrappingConfig(**data.get("wrapping", {})),
            quarantine=QuarantineConfig(**data.get("quarantine", {})),
            storage_policy=StoragePolicyConfig(**data.get("storage_policy", {})),
            category_risks=CategoryRiskMapping(**data.get("category_risks", {})),
            tool_overrides={
                k: RiskLevel(v) for k, v in data.get("tool_overrides", {}).items()
            },
        )


DEFAULT_SANITIZATION_CONFIG = SanitizationConfig()

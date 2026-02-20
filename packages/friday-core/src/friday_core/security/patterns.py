"""
Injection pattern library for prompt injection detection.

Patterns are grouped by attack type and filtered by sensitivity threshold.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class InjectionPattern:
    """A single injection detection pattern."""

    name: str
    pattern: str
    severity: Literal["low", "medium", "high", "critical"]
    category: str
    description: str
    sensitivity_threshold: Literal["low", "medium", "high", "paranoid"] = "medium"

    _compiled: re.Pattern = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._compiled = re.compile(self.pattern, re.IGNORECASE | re.MULTILINE)

    def matches(self, content: str) -> list[re.Match]:
        """Find all matches in content."""
        return list(self._compiled.finditer(content))


class InjectionPatternLibrary:
    """Collection of known prompt injection patterns."""

    # === INSTRUCTION INJECTION ===
    INSTRUCTION_PATTERNS = [
        InjectionPattern(
            name="ignore_instructions",
            pattern=r"(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|prior|above|earlier)\s+(?:instructions?|prompts?|context)",
            severity="critical",
            category="instruction",
            description="Attempts to override system instructions",
            sensitivity_threshold="low",
        ),
        InjectionPattern(
            name="new_instructions",
            pattern=r"(?:new|updated?|changed?|revised?)\s+(?:instructions?|directives?|rules?)[\s:]+",
            severity="high",
            category="instruction",
            description="Attempts to inject new instructions",
            sensitivity_threshold="medium",
        ),
        InjectionPattern(
            name="system_prompt_override",
            pattern=r"(?:system\s*prompt|system\s*message|base\s*instructions?)[\s:]*(?:is|are|should\s+be|now)",
            severity="critical",
            category="instruction",
            description="Attempts to redefine system prompt",
            sensitivity_threshold="low",
        ),
        InjectionPattern(
            name="assistant_identity",
            pattern=r"you\s+are\s+(?:now|actually|really)\s+(?:a|an|the)\s+\w+",
            severity="high",
            category="roleplay",
            description="Attempts to change assistant identity",
            sensitivity_threshold="medium",
        ),
        InjectionPattern(
            name="important_override",
            pattern=r"(?:IMPORTANT|CRITICAL|URGENT|PRIORITY)[\s:]+(?:ignore|disregard|override|new)",
            severity="high",
            category="instruction",
            description="Urgency-based instruction override",
            sensitivity_threshold="low",
        ),
    ]

    # === DELIMITER INJECTION ===
    DELIMITER_PATTERNS = [
        InjectionPattern(
            name="xml_system_tags",
            pattern=r"</?(?:system|user|assistant|human|ai|tool|function|message|prompt)[\s>]",
            severity="high",
            category="delimiter",
            description="XML-style role delimiter injection",
            sensitivity_threshold="low",
        ),
        InjectionPattern(
            name="markdown_hidden_block",
            pattern=r"```(?:system|assistant|hidden|secret|internal|prompt)",
            severity="medium",
            category="delimiter",
            description="Markdown fence delimiter escape",
            sensitivity_threshold="medium",
        ),
        InjectionPattern(
            name="llama_role_markers",
            pattern=r"\[/?(?:SYSTEM|USER|ASSISTANT|INST|\/INST)\]",
            severity="high",
            category="delimiter",
            description="Llama-style role marker injection",
            sensitivity_threshold="low",
        ),
        InjectionPattern(
            name="anthropic_markers",
            pattern=r"(?:Human|Assistant|System):\s*$",
            severity="medium",
            category="delimiter",
            description="Anthropic-style role markers",
            sensitivity_threshold="medium",
        ),
    ]

    # === DATA EXFILTRATION ===
    EXFIL_PATTERNS = [
        InjectionPattern(
            name="reveal_prompt",
            pattern=r"(?:reveal|show|display|print|output|leak|expose)\s+(?:your\s+)?(?:system\s+)?(?:prompt|instructions?|rules?|guidelines?)",
            severity="high",
            category="data_exfil",
            description="Attempts to reveal system prompt",
            sensitivity_threshold="medium",
        ),
        InjectionPattern(
            name="repeat_context",
            pattern=r"(?:repeat|echo|output|print)\s+(?:everything|all)\s+(?:above|you(?:'ve)?\s+(?:seen|read|received))",
            severity="medium",
            category="data_exfil",
            description="Attempts to extract full context",
            sensitivity_threshold="medium",
        ),
        InjectionPattern(
            name="verbatim_request",
            pattern=r"(?:word\s*for\s*word|verbatim|exactly\s+as)\s+(?:the|your)\s+(?:system|original|initial)",
            severity="medium",
            category="data_exfil",
            description="Requests verbatim system content",
            sensitivity_threshold="high",
        ),
    ]

    # === TOOL ABUSE ===
    TOOL_ABUSE_PATTERNS = [
        InjectionPattern(
            name="tool_call_instruction",
            pattern=r"(?:call|execute|run|invoke|use)\s+(?:the\s+)?(?:tool|function)\s+['\"]?\w+['\"]?",
            severity="medium",
            category="tool_abuse",
            description="Attempts to trigger specific tool calls",
            sensitivity_threshold="high",
        ),
        InjectionPattern(
            name="json_function_injection",
            pattern=r'\{\s*"(?:function|tool|action|name)":\s*["\{]',
            severity="medium",
            category="tool_abuse",
            description="JSON-style function call injection",
            sensitivity_threshold="high",
        ),
        InjectionPattern(
            name="read_sensitive_files",
            pattern=r"(?:read|cat|open|access|get)\s+(?:the\s+)?(?:file\s+)?(?:[~\/]|\.\.\/|\/etc\/|\.ssh|\.env|password|secret|credential|token|key)",
            severity="critical",
            category="tool_abuse",
            description="Attempts to read sensitive files",
            sensitivity_threshold="low",
        ),
    ]

    # === JAILBREAK ===
    JAILBREAK_PATTERNS = [
        InjectionPattern(
            name="dan_jailbreak",
            pattern=(
                r"(?:(?-i:\bDAN\b)"
                r"|(?i:\bD[\.\-_\s]*A[\.\-_\s]*N\b)(?=\s+(?:mode|jailbreak|prompt|persona|instructions?))"
                r"|do\s+anything\s+now|developer\s+mode|god\s+mode|sudo\s+mode)"
            ),
            severity="critical",
            category="jailbreak",
            description="Known jailbreak patterns (DAN, etc.)",
            sensitivity_threshold="low",
        ),
        InjectionPattern(
            name="guardrails_override",
            pattern=(
                r"(?:ignore|bypass|disable|override|disregard)\s+"
                r"(?:the\s+)?(?:safety|guardrails?|policies|alignment|content\s+rules?)"
            ),
            severity="high",
            category="jailbreak",
            description="Attempts to bypass safety or guardrails",
            sensitivity_threshold="medium",
        ),
        InjectionPattern(
            name="hypothetical_bypass",
            pattern=r"(?:hypothetically|pretend|imagine|roleplay|act\s+as\s+if|in\s+a\s+story)\s+(?:you\s+)?(?:could|can|were\s+able|had\s+no\s+(?:rules|limits))",
            severity="medium",
            category="jailbreak",
            description="Hypothetical scenario bypass",
            sensitivity_threshold="high",
        ),
        InjectionPattern(
            name="opposite_day",
            pattern=r"(?:opposite\s+day|bizarro|reverse\s+mode|do\s+the\s+opposite)",
            severity="medium",
            category="jailbreak",
            description="Opposite/reverse instruction attacks",
            sensitivity_threshold="medium",
        ),
    ]

    # === ENCODING TRICKS ===
    ENCODING_PATTERNS = [
        InjectionPattern(
            name="base64_instruction",
            pattern=r"(?:decode|base64|b64)\s*[:=]\s*[A-Za-z0-9+/=]{20,}",
            severity="medium",
            category="encoding",
            description="Base64-encoded instruction injection",
            sensitivity_threshold="high",
        ),
        InjectionPattern(
            name="zero_width_chars",
            pattern=r"[\u200b\u200c\u200d\u2060\ufeff]{2,}",
            severity="low",
            category="encoding",
            description="Zero-width character sequences",
            sensitivity_threshold="paranoid",
        ),
        InjectionPattern(
            name="homoglyph_system",
            pattern=r"[\u0455\u0443\u0455\u0442\u0435\u043c]",  # Cyrillic "system"
            severity="medium",
            category="encoding",
            description="Homoglyph character substitution",
            sensitivity_threshold="paranoid",
        ),
    ]

    def __init__(self) -> None:
        self._all_patterns: list[InjectionPattern] = []
        self._all_patterns.extend(self.INSTRUCTION_PATTERNS)
        self._all_patterns.extend(self.DELIMITER_PATTERNS)
        self._all_patterns.extend(self.EXFIL_PATTERNS)
        self._all_patterns.extend(self.TOOL_ABUSE_PATTERNS)
        self._all_patterns.extend(self.JAILBREAK_PATTERNS)
        self._all_patterns.extend(self.ENCODING_PATTERNS)

    def get_patterns_for_sensitivity(
        self,
        sensitivity: Literal["low", "medium", "high", "paranoid"],
    ) -> list[InjectionPattern]:
        """Get patterns appropriate for the given sensitivity level."""
        threshold_order = ["low", "medium", "high", "paranoid"]
        threshold_index = threshold_order.index(sensitivity)

        return [
            p
            for p in self._all_patterns
            if threshold_order.index(p.sensitivity_threshold) <= threshold_index
        ]

    def add_custom_pattern(self, pattern: InjectionPattern) -> None:
        """Add a custom detection pattern."""
        self._all_patterns.append(pattern)

    @property
    def all_patterns(self) -> list[InjectionPattern]:
        """Get all patterns regardless of sensitivity."""
        return self._all_patterns.copy()

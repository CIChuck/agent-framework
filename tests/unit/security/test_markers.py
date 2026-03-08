# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for content marker utilities."""

from friday_core.security import ContentMetadata, RiskLevel, UntrustedContentMarker


def test_wrap_xml_includes_metadata():
    metadata = ContentMetadata(
        tool_name="web_reader",
        tool_category="web",
        risk_level=RiskLevel.CRITICAL,
        content_length=10,
    )
    wrapped = UntrustedContentMarker.wrap_xml("hello", metadata, include_metadata=True)
    assert "<untrusted_content" in wrapped
    assert 'source="web_reader"' in wrapped


def test_wrap_xml_excludes_metadata():
    metadata = ContentMetadata(
        tool_name="web_reader",
        tool_category="web",
        risk_level=RiskLevel.CRITICAL,
        content_length=10,
    )
    wrapped = UntrustedContentMarker.wrap_xml("hello", metadata, include_metadata=False)
    assert "<untrusted_content>" in wrapped
    assert "source=" not in wrapped

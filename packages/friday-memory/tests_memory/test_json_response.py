from friday_memory.json_response import (
    json_parse_warning_detail,
    json_response_text,
    parse_json_object_from_text,
    strip_llm_reasoning,
)


def test_parse_json_object_after_think_block() -> None:
    content = """
<think>
I should inspect the turn first. This is not JSON.
</think>
{"entities": [], "relationships": [], "insights": [], "summary": ""}
"""

    assert parse_json_object_from_text(content) == {
        "entities": [],
        "relationships": [],
        "insights": [],
        "summary": "",
    }


def test_parse_json_object_ignores_braces_inside_reasoning() -> None:
    content = """
<think>
Candidate shape might be {"invalid": true, and this is deliberately malformed.
</think>
The answer is:
{"falsifiable": true, "reasoning": "claim can be checked"}
"""

    assert parse_json_object_from_text(content) == {
        "falsifiable": True,
        "reasoning": "claim can be checked",
    }


def test_parse_json_object_from_markdown_after_reasoning_prefix() -> None:
    content = """
Reasoning: I need to produce the requested object.
```json
{"meta_insight": "The user is debugging extraction.", "confidence": 0.8}
```
"""

    assert parse_json_object_from_text(content) == {
        "meta_insight": "The user is debugging extraction.",
        "confidence": 0.8,
    }


def test_strip_llm_reasoning_removes_common_xml_blocks() -> None:
    content = "<analysis>private reasoning</analysis>{\"ok\": true}"

    assert strip_llm_reasoning(content) == '{"ok": true}'


def test_json_parse_warning_detail_reports_empty_content() -> None:
    assert json_parse_warning_detail("memory extraction", "") == (
        "Could not parse JSON from memory extraction response "
        "(raw_chars=0, reasoning_chars=0, sanitized_chars=0, preview='')"
    )


def test_json_response_text_never_promotes_reasoning_to_final_content() -> None:
    class Response:
        content = ""
        reasoning_content = '{"entities": []}'

    assert json_response_text(Response()) == ""


def test_json_parse_warning_detail_suppresses_reasoning_preview() -> None:
    assert json_parse_warning_detail(
        "memory extraction",
        "",
        reasoning_content="private chain of thought",
    ) == (
        "Could not parse JSON from memory extraction response "
        "(raw_chars=0, reasoning_chars=24, sanitized_chars=24, "
        "preview=<content empty; reasoning_content present>)"
    )

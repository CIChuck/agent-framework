"""Dated wire/header/SSE boundaries, including schema annotation adversaries."""

import base64

import pytest

from friday_mcp.client.http_policy import HTTPEndpoint, HTTPEndpointPolicy
from friday_mcp.client.http_protocol import (
    HeaderBinding,
    HTTPLimits,
    SSEDecoder,
    compatibility_result,
    content_type,
    header_bindings,
    header_value,
    response_headers,
    session_id,
)
from friday_mcp.client.protocol import ProtocolFailure, ProtocolLimits


@pytest.mark.parametrize("value", ["hello", "", "true", "-42", "a\tb"])
def test_plain_header_values(value):
    assert header_value(value) == value.encode()


@pytest.mark.parametrize(
    "value", [" padded ", "雪", "line\r\nnext", "\x00", "=?base64?literal?=", "\tfirst"]
)
def test_exact_base64_utf8_header_values(value):
    assert (
        header_value(value) == b"=?base64?" + base64.b64encode(value.encode()) + b"?="
    )


def test_header_value_surrogate_is_fixed_failure():
    with pytest.raises(ProtocolFailure):
        header_value("\ud800")


@pytest.mark.parametrize(
    "kind,value,expected",
    [
        ("integer", -(2**53) + 1, b"-9007199254740991"),
        ("integer", 2**53 - 1, b"9007199254740991"),
        ("integer", 42.0, b"42"),
        ("boolean", True, b"true"),
        ("boolean", False, b"false"),
        ("string", "雪", b"=?base64?6Zuq?="),
    ],
)
def test_nested_exact_property_path_types(kind, value, expected):
    bindings = header_bindings(
        {
            "type": "object",
            "properties": {
                "nested": {
                    "type": "object",
                    "properties": {"v": {"type": kind, "x-mcp-header": "V"}},
                }
            },
        }
    )
    assert bindings[0].path == ("nested", "v")
    assert bindings[0].extract({"nested": {"v": value}}) == expected
    for arguments in ({}, {"nested": {}}, {"nested": None}, {"nested": {"v": None}}):
        assert bindings[0].extract(arguments) is None


@pytest.mark.parametrize(
    "kind,value",
    [
        ("integer", True),
        ("integer", 1.5),
        ("integer", 2**53),
        ("integer", -(2**53)),
        ("integer", 2**4095),
        ("integer", "2"),
        ("string", 3),
        ("boolean", 1),
        ("boolean", "true"),
    ],
)
def test_invalid_supplied_header_argument(kind, value):
    with pytest.raises(ProtocolFailure):
        HeaderBinding("V", ("v",), kind).extract({"v": value})


@pytest.mark.parametrize("name", ["", "a b", "a:b", "a\r\nb", "雪", 4, None, True])
def test_invalid_annotation_name(name):
    with pytest.raises(ProtocolFailure):
        header_bindings({"properties": {"v": {"type": "string", "x-mcp-header": name}}})


@pytest.mark.parametrize(
    "kind", ["number", "object", "array", ["string", "null"], None]
)
def test_invalid_annotation_type(kind):
    with pytest.raises(ProtocolFailure):
        header_bindings({"properties": {"v": {"type": kind, "x-mcp-header": "V"}}})


@pytest.mark.parametrize(
    "keyword",
    [
        "items",
        "contains",
        "not",
        "if",
        "then",
        "else",
        "additionalProperties",
        "propertyNames",
    ],
)
def test_unreachable_annotation_schema_child(keyword):
    with pytest.raises(ProtocolFailure):
        header_bindings(
            {keyword: {"properties": {"v": {"type": "string", "x-mcp-header": "V"}}}}
        )


@pytest.mark.parametrize("keyword", ["oneOf", "anyOf", "allOf", "prefixItems"])
def test_unreachable_annotation_composition(keyword):
    with pytest.raises(ProtocolFailure):
        header_bindings(
            {keyword: [{"properties": {"v": {"type": "string", "x-mcp-header": "V"}}}]}
        )


def test_unreachable_defs_annotation_collision_root_and_opaque_examples():
    node = {"type": "string", "x-mcp-header": "V"}
    for schema in (
        node,
        {"$defs": {"s": node}},
        {"properties": {"v": node, "w": {"type": "boolean", "x-mcp-header": "v"}}},
    ):
        with pytest.raises(ProtocolFailure):
            header_bindings(schema)
    assert not header_bindings(
        {
            "type": "object",
            "examples": [{"x-mcp-header": "ordinary JSON"}],
            "const": {"x-mcp-header": "also data"},
        }
    )


@pytest.mark.parametrize("width", [1, 2, 3, 7, 10000])
@pytest.mark.parametrize("newline", [b"\n", b"\r\n", b"\r"])
def test_sse_chunk_utf8_multiline_comments_and_priming(width, newline):
    source = newline.join(
        [
            b"\xef\xbb\xbf: keepalive",
            b"",
            b"id: no-replay",
            b"data:",
            b"",
            b"event: message",
            b'data: {"a":',
            'data: "雪"}'.encode(),
            b"",
            b"",
        ]
    )
    decoder = SSEDecoder(HTTPLimits())
    received = []
    for pos in range(0, len(source), width):
        received.extend(decoder.feed(source[pos : pos + width]))
    received.extend(decoder.finish())
    assert received == ['{"a":\n"雪"}'.encode()]


@pytest.mark.parametrize("raw", [b"data: x", b"data: x\n", b"data: \xff\n\n"])
def test_sse_truncation_and_invalid_utf8(raw):
    decoder = SSEDecoder(HTTPLimits())
    with pytest.raises(ProtocolFailure):
        decoder.feed(raw)
        decoder.finish()


@pytest.mark.parametrize(
    "limits,raw",
    [
        (HTTPLimits(sse_events=1), b": a\n: b\n"),
        (HTTPLimits(sse_line_bytes=3), b"abcd"),
        (HTTPLimits(sse_event_bytes=3), b"data: abc\n\n"),
        (HTTPLimits(wire_bytes=3), b"abcd"),
    ],
)
def test_sse_pre_retention_caps(limits, raw):
    with pytest.raises(ProtocolFailure) as failure:
        SSEDecoder(limits).feed(raw)
    assert failure.value.failure_code == "limit_exceeded"


@pytest.mark.parametrize(
    "field",
    ["header_bytes", "wire_bytes", "sse_events", "sse_line_bytes", "sse_event_bytes"],
)
@pytest.mark.parametrize("value", [True, 0, -1, 1048577, "4"])
def test_http_limits_are_lower_only(field, value):
    with pytest.raises(ValueError):
        HTTPLimits(**{field: value})


@pytest.mark.parametrize("value", [b"", b"a b", b"\r", b"\xff", b"a" * 257])
def test_session_id_is_bounded_visible_ascii(value):
    with pytest.raises(ProtocolFailure):
        session_id(value)


def test_response_header_case_duplicates_charset_and_size():
    assert session_id(b"session-1") == b"session-1"
    assert (
        content_type(
            response_headers(
                [(b"Content-Type", b"application/json; charset=utf-8")], HTTPLimits()
            )
        )
        == b"application/json"
    )
    for headers in (
        [
            (b"Content-Type", b"application/json"),
            (b"content-type", b"text/event-stream"),
        ],
        [(b"MCP-Session-Id", b"a"), (b"mcp-session-id", b"b")],
    ):
        with pytest.raises(ProtocolFailure):
            response_headers(headers, HTTPLimits())
    with pytest.raises(ProtocolFailure):
        content_type({b"content-type": b"application/json; charset=utf-16"})
    with pytest.raises(ProtocolFailure):
        response_headers([(b"a", b"b" * 10)], HTTPLimits(header_bytes=5))


@pytest.mark.parametrize(
    "url",
    [
        "http://public.example/mcp",
        "https://user:secret@public.example/mcp",
        "https://public.example/mcp?token=secret",
        "https://public.example/mcp#fragment",
        "https://127.0.0.1/mcp",
        "https://169.254.169.254/mcp",
        "https://public.example:444/mcp",
        "https://public.example/\r\nx",
        "https://public.example/雪",
        "https://[::ffff:127.0.0.1]/mcp",
    ],
)
def test_endpoint_rejection_is_pre_io_and_fixed(url):
    with pytest.raises(ValueError, match="^Invalid MCP HTTP endpoint$"):
        HTTPEndpoint.parse(url, HTTPEndpointPolicy())


def test_explicit_fixture_and_production_private_endpoint_policies():
    fixture = HTTPEndpointPolicy(("127.0.0.1",), (12345,), True)
    assert HTTPEndpoint.parse("http://127.0.0.1:12345/mcp", fixture).port == 12345
    assert (
        HTTPEndpoint.parse(
            "https://10.0.0.1/mcp", HTTPEndpointPolicy(("10.0.0.1",))
        ).scheme
        == "https"
    )
    with pytest.raises(ValueError):
        HTTPEndpoint.parse(
            "http://10.0.0.1/mcp", HTTPEndpointPolicy(("10.0.0.1",), (80,), True)
        )


@pytest.mark.parametrize(
    "result,method",
    [
        ({"content": ["2024 bare text"]}, "tools/call"),
        (
            {
                "tools": [
                    {"name": "a", "inputSchema": {"type": "object"}, "execution": None}
                ]
            },
            "tools/list",
        ),
        (
            {
                "tools": [
                    {
                        "name": "a",
                        "inputSchema": {"type": "object"},
                        "outputSchema": None,
                    }
                ]
            },
            "tools/list",
        ),
        ({"content": [], "structuredContent": None}, "tools/call"),
        ({"content": [], "structuredContent": 2}, "tools/call"),
        (
            {
                "content": [
                    {"type": "text", "text": "x", "annotations": {"priority": True}}
                ]
            },
            "tools/call",
        ),
        (
            {
                "tools": [
                    {
                        "name": "a",
                        "inputSchema": {"type": "object"},
                        "outputSchema": {"type": "integer"},
                    }
                ]
            },
            "tools/list",
        ),
        (
            {
                "protocolVersion": "2025-11-25",
                "serverInfo": {"name": "x", "version": "1"},
                "capabilities": {"tools": {"listChanged": 2}},
            },
            "initialize",
        ),
    ],
)
def test_2025_schema_restrictions_do_not_use_2024_permissive_defaults(result, method):
    with pytest.raises(ProtocolFailure):
        compatibility_result(result, method, ProtocolLimits())


def test_2025_structured_object_and_opaque_era_metadata():
    compatibility_result(
        {
            "content": [
                {
                    "type": "text",
                    "text": "ok",
                    "_meta": {
                        "io.modelcontextprotocol/serverInfo": "opaque in this era"
                    },
                }
            ],
            "structuredContent": {"v": 1},
        },
        "tools/call",
        ProtocolLimits(),
    )

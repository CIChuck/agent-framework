# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for WebReaderTool."""

import socket

import pytest
import respx
from httpx import Response

from friday_tools.web import WebConfig, WebReaderInput, WebReaderTool, web_reader


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "host", ["192.168.1.1", "169.254.169.254", "[fc00::1]", "[fe80::1]", "[ff02::1]"],
)
async def test_private_literal_rejected_before_transport(host, monkeypatch):
    def prohibit(*args, **kwargs):
        pytest.fail("Rejected literals must not use DNS or create a transport")

    monkeypatch.setattr(socket, "getaddrinfo", prohibit)
    monkeypatch.setattr("friday_tools.web.reader.create_http_client", prohibit)
    result = await WebReaderTool().run(WebReaderInput(url=f"http://{host}/"))
    assert result.error is not None
    assert "private IP" in result.content


@pytest.fixture
def reader():
    """Create a WebReaderTool with default config."""
    return WebReaderTool()


@pytest.fixture
def reader_allow_private():
    """Create a WebReaderTool that allows private IPs."""
    config = WebConfig.from_dict({"security": {"allow_private_ips": True}})
    return WebReaderTool(config=config)


class TestWebReaderToolInit:
    """Tests for WebReaderTool initialization."""

    def test_default_config(self):
        reader = WebReaderTool()
        assert reader._config.client.timeout == 30.0
        assert reader._config.security.allow_private_ips is False

    def test_config_from_dict(self):
        reader = WebReaderTool(config={"client": {"timeout": 60.0}})
        assert reader._config.client.timeout == 60.0

    def test_config_from_webconfig(self):
        config = WebConfig.from_dict({"client": {"timeout": 45.0}})
        reader = WebReaderTool(config=config)
        assert reader._config.client.timeout == 45.0


class TestWebReaderToolSchema:
    """Tests for WebReaderTool schema."""

    def test_name(self, reader):
        assert reader.name == "web_reader"

    def test_category(self, reader):
        assert reader.category == "web"

    def test_tags(self, reader):
        assert "read-only" in reader.tags
        assert "async" in reader.tags

    def test_description(self, reader):
        assert "web pages" in reader.description.lower()


class TestURLValidation:
    """Tests for URL validation in WebReaderTool."""

    @pytest.mark.asyncio
    async def test_rejects_private_ip(self, reader):
        args = WebReaderInput(url="http://192.168.1.1/")
        result = await reader.run(args)
        assert result.error is not None
        assert "private IP" in result.content

    @pytest.mark.asyncio
    async def test_rejects_localhost(self, reader):
        args = WebReaderInput(url="http://localhost/")
        result = await reader.run(args)
        assert result.error is not None
        assert "Localhost" in result.content

    @pytest.mark.asyncio
    async def test_rejects_invalid_scheme(self, reader):
        args = WebReaderInput(url="ftp://example.com/")
        result = await reader.run(args)
        assert result.error is not None
        assert "not allowed" in result.content

    @pytest.mark.asyncio
    @respx.mock
    async def test_allows_public_url(self, reader):
        respx.get("https://example.com/").mock(
            return_value=Response(200, text="<html><body>Hello</body></html>")
        )
        args = WebReaderInput(url="https://example.com/")
        result = await reader.run(args)
        assert result.error is None
        assert "Hello" in result.content


class TestHTMLParsing:
    """Tests for HTML content parsing."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_html_to_markdown(self, reader):
        html = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Hello World</h1>
            <p>This is a paragraph.</p>
        </body>
        </html>
        """
        respx.get("https://example.com/").mock(
            return_value=Response(200, text=html, headers={"content-type": "text/html"})
        )
        args = WebReaderInput(url="https://example.com/")
        result = await reader.run(args)
        assert result.error is None
        assert "Hello World" in result.content
        assert "paragraph" in result.content

    @pytest.mark.asyncio
    @respx.mock
    async def test_removes_script_tags(self, reader):
        html = """
        <html><body>
            <p>Content</p>
            <script>alert('evil');</script>
        </body></html>
        """
        respx.get("https://example.com/").mock(
            return_value=Response(200, text=html, headers={"content-type": "text/html"})
        )
        args = WebReaderInput(url="https://example.com/")
        result = await reader.run(args)
        assert "alert" not in result.content
        assert "Content" in result.content

    @pytest.mark.asyncio
    @respx.mock
    async def test_removes_nav_footer(self, reader):
        html = """
        <html><body>
            <nav>Navigation</nav>
            <main>Main Content</main>
            <footer>Footer</footer>
        </body></html>
        """
        respx.get("https://example.com/").mock(
            return_value=Response(200, text=html, headers={"content-type": "text/html"})
        )
        args = WebReaderInput(url="https://example.com/")
        result = await reader.run(args)
        assert "Main Content" in result.content
        # Nav and footer should be removed
        assert "Navigation" not in result.content
        assert "Footer" not in result.content


class TestJSONParsing:
    """Tests for JSON content parsing."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_json_pretty_printed(self, reader):
        json_content = '{"name": "test", "value": 123}'
        respx.get("https://api.example.com/data").mock(
            return_value=Response(
                200, text=json_content, headers={"content-type": "application/json"}
            )
        )
        args = WebReaderInput(url="https://api.example.com/data")
        result = await reader.run(args)
        assert result.error is None
        assert '"name": "test"' in result.content
        assert result.metadata["output_format"] == "json"


class TestContentTruncation:
    """Tests for content length limiting."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_truncates_long_content(self, reader):
        # Create content longer than max_length
        long_content = "<html><body>" + "x" * 60000 + "</body></html>"
        respx.get("https://example.com/").mock(
            return_value=Response(
                200, text=long_content, headers={"content-type": "text/html"}
            )
        )
        args = WebReaderInput(url="https://example.com/", max_length=1000)
        result = await reader.run(args)
        assert len(result.content) <= 1100  # 1000 + truncation message
        assert "truncated" in result.content.lower()
        assert result.metadata["truncated"] is True


class TestMetadataExtraction:
    """Tests for page metadata extraction."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_extracts_title(self, reader):
        html = """
        <html>
        <head><title>My Page Title</title></head>
        <body><p>Content</p></body>
        </html>
        """
        respx.get("https://example.com/").mock(
            return_value=Response(200, text=html, headers={"content-type": "text/html"})
        )
        args = WebReaderInput(url="https://example.com/", include_metadata=True)
        result = await reader.run(args)
        assert result.metadata["page"]["title"] == "My Page Title"

    @pytest.mark.asyncio
    @respx.mock
    async def test_extracts_description(self, reader):
        html = """
        <html>
        <head>
            <meta name="description" content="Page description here">
        </head>
        <body><p>Content</p></body>
        </html>
        """
        respx.get("https://example.com/").mock(
            return_value=Response(200, text=html, headers={"content-type": "text/html"})
        )
        args = WebReaderInput(url="https://example.com/", include_metadata=True)
        result = await reader.run(args)
        assert result.metadata["page"]["description"] == "Page description here"

    @pytest.mark.asyncio
    @respx.mock
    async def test_extracts_og_tags(self, reader):
        html = """
        <html>
        <head>
            <meta property="og:title" content="OG Title">
            <meta property="og:image" content="https://example.com/image.jpg">
        </head>
        <body><p>Content</p></body>
        </html>
        """
        respx.get("https://example.com/").mock(
            return_value=Response(200, text=html, headers={"content-type": "text/html"})
        )
        args = WebReaderInput(url="https://example.com/", include_metadata=True)
        result = await reader.run(args)
        assert result.metadata["page"]["og_title"] == "OG Title"
        assert result.metadata["page"]["og_image"] == "https://example.com/image.jpg"


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_handles_404(self, reader):
        respx.get("https://example.com/notfound").mock(return_value=Response(404))
        args = WebReaderInput(url="https://example.com/notfound")
        result = await reader.run(args)
        assert result.error is not None
        assert "404" in result.content or "Failed" in result.content

    @pytest.mark.asyncio
    @respx.mock
    async def test_handles_500(self, reader):
        respx.get("https://example.com/error").mock(return_value=Response(500))
        args = WebReaderInput(url="https://example.com/error")
        result = await reader.run(args)
        assert result.error is not None


class TestOutputFormats:
    """Tests for different output formats."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_text_format(self, reader):
        html = "<html><body><h1>Title</h1><p>Paragraph</p></body></html>"
        respx.get("https://example.com/").mock(
            return_value=Response(200, text=html, headers={"content-type": "text/html"})
        )
        args = WebReaderInput(url="https://example.com/", output_format="text")
        result = await reader.run(args)
        assert "Title" in result.content
        assert "Paragraph" in result.content
        # Should not have markdown formatting
        assert "#" not in result.content

    @pytest.mark.asyncio
    @respx.mock
    async def test_html_format(self, reader):
        html = "<html><body><h1>Title</h1></body></html>"
        respx.get("https://example.com/").mock(
            return_value=Response(200, text=html, headers={"content-type": "text/html"})
        )
        args = WebReaderInput(url="https://example.com/", output_format="html")
        result = await reader.run(args)
        # Should preserve HTML tags
        assert "<h1>" in result.content or "Title" in result.content


class TestConvenienceInstance:
    """Tests for the web_reader convenience instance."""

    def test_exists(self):
        assert web_reader is not None
        assert isinstance(web_reader, WebReaderTool)

    def test_has_default_config(self):
        assert web_reader._config.client.timeout == 30.0

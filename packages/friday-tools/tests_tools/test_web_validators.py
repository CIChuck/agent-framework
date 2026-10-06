# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for URL validation and SSRF protection."""

import socket

import pytest

from friday_tools.web import URLValidationError, is_safe_url, validate_url


@pytest.fixture(autouse=True)
def public_domain_answers(monkeypatch):
    """Keep ordinary domain validation deterministic and offline."""
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 0))
        ],
    )


def _prohibit_literal_dns(monkeypatch):
    def resolve(*args, **kwargs):
        pytest.fail("Literal addresses must be classified without DNS")

    monkeypatch.setattr(socket, "getaddrinfo", resolve)


@pytest.mark.parametrize(
    "host",
    [
        "10.0.0.1", "172.16.0.1", "192.168.1.1", "169.254.169.254",
        "[fc00::1]", "[fe80::1]", "[ff02::1]", "[::1]", "127.0.0.2",
        "240.0.0.1", "224.0.0.1",
    ],
)
def test_private_literals_rejected_without_resolver(host, monkeypatch):
    _prohibit_literal_dns(monkeypatch)
    with pytest.raises(URLValidationError):
        validate_url(f"http://{host}/synthetic")


@pytest.mark.parametrize("host", ["8.8.8.8", "[2606:4700:4700::1111]"])
def test_public_literals_accepted_without_resolver(host, monkeypatch):
    _prohibit_literal_dns(monkeypatch)
    url = f"https://{host}/synthetic"
    assert validate_url(url) == url


@pytest.mark.parametrize("host", ["192.168.1.1", "[fc00::1]", "[ff02::1]"])
def test_private_literal_override_preserved_without_resolver(host, monkeypatch):
    _prohibit_literal_dns(monkeypatch)
    url = f"http://{host}/synthetic"
    assert validate_url(url, allow_private_ips=True) == url
    with pytest.raises(URLValidationError, match="blocked"):
        validate_url(url, allow_private_ips=True, blocked_hosts={host.strip("[]")})
    with pytest.raises(URLValidationError, match="not allowed"):
        validate_url(url.replace("http:", "ftp:"), allow_private_ips=True)


@pytest.mark.parametrize("private", ["192.168.1.1", "fc00::1", "fe80::1", "ff02::1"])
@pytest.mark.parametrize("private_first", [False, True])
def test_domain_mixed_answers_reject_any_private_address(
    private, private_first, monkeypatch,
):
    public = (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 0))
    family = socket.AF_INET6 if ":" in private else socket.AF_INET
    unsafe = (family, socket.SOCK_STREAM, 6, "", (private, 0))
    answers = [unsafe, public] if private_first else [public, unsafe]
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: answers)
    with pytest.raises(URLValidationError, match="private IP"):
        validate_url("https://synthetic.example/")


@pytest.mark.parametrize(
    "failure", [socket.gaierror("synthetic DNS failure"), RuntimeError("guard")],
)
def test_domain_resolver_failure_policy_preserved(failure, monkeypatch):
    def resolve(*args, **kwargs):
        raise failure

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    assert validate_url("https://synthetic.example/") == "https://synthetic.example/"


class TestValidateUrl:
    """Tests for validate_url function."""

    def test_valid_https_url(self):
        url = "https://example.com/path?query=value"
        result = validate_url(url)
        assert result == url

    def test_valid_http_url(self):
        url = "http://example.com/"
        result = validate_url(url)
        assert result == url

    def test_missing_scheme(self):
        with pytest.raises(URLValidationError, match="must include a scheme"):
            validate_url("example.com")

    def test_invalid_scheme_ftp(self):
        with pytest.raises(URLValidationError, match="not allowed"):
            validate_url("ftp://example.com/file.txt")

    def test_invalid_scheme_file(self):
        with pytest.raises(URLValidationError, match="not allowed"):
            validate_url("file:///etc/passwd")

    def test_invalid_scheme_javascript(self):
        with pytest.raises(URLValidationError, match="not allowed"):
            validate_url("javascript:alert(1)")

    def test_missing_hostname(self):
        with pytest.raises(URLValidationError, match="must include a hostname"):
            validate_url("http://")


class TestSSRFProtection:
    """Tests for SSRF protection."""

    def test_blocks_localhost(self):
        with pytest.raises(URLValidationError, match="Localhost"):
            validate_url("http://localhost/admin")

    def test_blocks_localhost_variations(self):
        localhost_urls = [
            "http://127.0.0.1/",
            "http://localhost/",
            "http://localhost.localdomain/",
            "http://0.0.0.0/",
        ]
        for url in localhost_urls:
            with pytest.raises(URLValidationError):
                validate_url(url)

    def test_allows_localhost_when_enabled(self):
        result = validate_url("http://localhost/", allow_private_ips=True)
        assert result == "http://localhost/"

    def test_blocks_private_ip_10_x(self):
        with pytest.raises(URLValidationError, match="private IP"):
            validate_url("http://10.0.0.1/internal")

    def test_blocks_private_ip_172_16_x(self):
        with pytest.raises(URLValidationError, match="private IP"):
            validate_url("http://172.16.0.1/internal")

    def test_blocks_private_ip_192_168_x(self):
        with pytest.raises(URLValidationError, match="private IP"):
            validate_url("http://192.168.1.1/router")

    def test_blocks_link_local(self):
        with pytest.raises(URLValidationError, match="private IP"):
            validate_url("http://169.254.169.254/latest/meta-data/")

    def test_allows_private_ip_when_enabled(self):
        result = validate_url("http://192.168.1.1/", allow_private_ips=True)
        assert result == "http://192.168.1.1/"


class TestBlockedHosts:
    """Tests for blocked hosts list."""

    def test_blocks_specified_host(self):
        blocked = {"evil.com", "malware.net"}
        with pytest.raises(URLValidationError, match="blocked"):
            validate_url("https://evil.com/", blocked_hosts=blocked)

    def test_blocks_specified_host_case_insensitive(self):
        blocked = {"evil.com"}
        with pytest.raises(URLValidationError, match="blocked"):
            validate_url("https://EVIL.COM/", blocked_hosts=blocked)

    def test_allows_non_blocked_host(self):
        blocked = {"evil.com"}
        result = validate_url("https://good.com/", blocked_hosts=blocked)
        assert result == "https://good.com/"


class TestCustomSchemes:
    """Tests for custom allowed schemes."""

    def test_custom_schemes(self):
        # Only allow https
        with pytest.raises(URLValidationError):
            validate_url("http://example.com/", allowed_schemes=("https",))

        # Allow https
        result = validate_url("https://example.com/", allowed_schemes=("https",))
        assert result == "https://example.com/"


class TestIsSafeUrl:
    """Tests for is_safe_url convenience function."""

    def test_safe_url_returns_true(self):
        assert is_safe_url("https://example.com/") is True

    def test_unsafe_url_returns_false(self):
        assert is_safe_url("http://localhost/") is False
        assert is_safe_url("ftp://example.com/") is False
        assert is_safe_url("http://192.168.1.1/") is False

    def test_respects_allow_private_ips(self):
        assert is_safe_url("http://localhost/", allow_private_ips=True) is True
        assert is_safe_url("http://192.168.1.1/", allow_private_ips=True) is True

    def test_respects_blocked_hosts(self):
        assert is_safe_url("https://evil.com/", blocked_hosts={"evil.com"}) is False
        assert is_safe_url("https://good.com/", blocked_hosts={"evil.com"}) is True

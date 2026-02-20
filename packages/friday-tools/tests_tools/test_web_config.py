"""Tests for web configuration models."""

import pytest
from pydantic import ValidationError

from friday_tools.web import (
    DEFAULT_WEB_CONFIG,
    HttpClientConfig,
    ProxyConfig,
    ReaderConfig,
    SecurityConfig,
    SSLConfig,
    WebConfig,
)


class TestHttpClientConfig:
    """Tests for HttpClientConfig."""

    def test_default_values(self):
        config = HttpClientConfig()
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.follow_redirects is True
        assert config.max_response_size == 10_000_000
        assert "FridayBot" in config.user_agent

    def test_custom_values(self):
        config = HttpClientConfig(
            timeout=60.0,
            max_retries=5,
            follow_redirects=False,
            max_response_size=5_000_000,
            user_agent="CustomBot/1.0",
        )
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.follow_redirects is False
        assert config.max_response_size == 5_000_000
        assert config.user_agent == "CustomBot/1.0"

    def test_timeout_validation(self):
        # Too low
        with pytest.raises(ValidationError):
            HttpClientConfig(timeout=0.5)
        # Too high
        with pytest.raises(ValidationError):
            HttpClientConfig(timeout=700.0)

    def test_max_retries_validation(self):
        # Negative
        with pytest.raises(ValidationError):
            HttpClientConfig(max_retries=-1)
        # Too high
        with pytest.raises(ValidationError):
            HttpClientConfig(max_retries=15)


class TestSSLConfig:
    """Tests for SSLConfig."""

    def test_default_values(self):
        config = SSLConfig()
        assert config.verify is True
        assert config.ca_bundle is None

    def test_custom_ca_bundle(self):
        config = SSLConfig(verify=True, ca_bundle="/path/to/ca-bundle.crt")
        assert config.ca_bundle == "/path/to/ca-bundle.crt"


class TestProxyConfig:
    """Tests for ProxyConfig."""

    def test_default_values(self):
        config = ProxyConfig()
        assert config.http is None
        assert config.https is None
        assert "localhost" in config.no_proxy
        assert "127.0.0.1" in config.no_proxy

    def test_custom_proxy(self):
        config = ProxyConfig(
            http="http://proxy:8080",
            https="https://proxy:8443",
            no_proxy=["internal.corp"],
        )
        assert config.http == "http://proxy:8080"
        assert config.https == "https://proxy:8443"
        assert config.no_proxy == ["internal.corp"]


class TestSecurityConfig:
    """Tests for SecurityConfig."""

    def test_default_values(self):
        config = SecurityConfig()
        assert config.allow_private_ips is False
        assert config.blocked_hosts == []

    def test_blocked_hosts(self):
        config = SecurityConfig(blocked_hosts=["evil.com", "malware.net"])
        assert "evil.com" in config.blocked_hosts
        assert "malware.net" in config.blocked_hosts


class TestReaderConfig:
    """Tests for ReaderConfig."""

    def test_default_values(self):
        config = ReaderConfig()
        assert config.default_format == "auto"
        assert config.max_content_length == 50000
        assert config.include_metadata is False
        assert "script" in config.remove_elements
        assert "style" in config.remove_elements

    def test_max_content_length_validation(self):
        # Too low
        with pytest.raises(ValidationError):
            ReaderConfig(max_content_length=500)
        # Too high
        with pytest.raises(ValidationError):
            ReaderConfig(max_content_length=3_000_000)

    def test_valid_formats(self):
        for fmt in ["auto", "markdown", "text", "html", "json"]:
            config = ReaderConfig(default_format=fmt)
            assert config.default_format == fmt

    def test_invalid_format(self):
        with pytest.raises(ValidationError):
            ReaderConfig(default_format="invalid")


class TestWebConfig:
    """Tests for complete WebConfig."""

    def test_default_values(self):
        config = WebConfig()
        assert config.client.timeout == 30.0
        assert config.ssl.verify is True
        assert config.proxy.http is None
        assert config.security.allow_private_ips is False
        assert config.reader.default_format == "auto"

    def test_from_dict_empty(self):
        config = WebConfig.from_dict({})
        assert config.client.timeout == 30.0
        assert config.ssl.verify is True

    def test_from_dict_partial(self):
        config = WebConfig.from_dict(
            {
                "client": {"timeout": 60.0},
                "security": {"allow_private_ips": True},
            }
        )
        assert config.client.timeout == 60.0
        assert config.client.max_retries == 3  # default
        assert config.security.allow_private_ips is True
        assert config.ssl.verify is True  # default

    def test_from_dict_full(self):
        config = WebConfig.from_dict(
            {
                "client": {
                    "timeout": 45.0,
                    "max_retries": 5,
                    "user_agent": "MyBot/2.0",
                },
                "ssl": {
                    "verify": False,
                },
                "proxy": {
                    "http": "http://proxy:8080",
                },
                "security": {
                    "allow_private_ips": True,
                    "blocked_hosts": ["evil.com"],
                },
                "reader": {
                    "default_format": "markdown",
                    "max_content_length": 100000,
                },
            }
        )
        assert config.client.timeout == 45.0
        assert config.client.max_retries == 5
        assert config.client.user_agent == "MyBot/2.0"
        assert config.ssl.verify is False
        assert config.proxy.http == "http://proxy:8080"
        assert config.security.allow_private_ips is True
        assert "evil.com" in config.security.blocked_hosts
        assert config.reader.default_format == "markdown"
        assert config.reader.max_content_length == 100000


class TestDefaultWebConfig:
    """Tests for the DEFAULT_WEB_CONFIG singleton."""

    def test_exists(self):
        assert DEFAULT_WEB_CONFIG is not None
        assert isinstance(DEFAULT_WEB_CONFIG, WebConfig)

    def test_default_values(self):
        assert DEFAULT_WEB_CONFIG.client.timeout == 30.0
        assert DEFAULT_WEB_CONFIG.security.allow_private_ips is False

# mypy: ignore-errors
"""
URL validation and security checks.

Provides SSRF (Server-Side Request Forgery) protection by validating
URLs before making HTTP requests.

Ref: docs/reference/specs/tool_specification.md - Category 5-6: Web Tools
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class URLValidationError(Exception):
    """Raised when a URL fails security validation."""

    pass


def validate_url(
    url: str,
    allowed_schemes: tuple[str, ...] = ("http", "https"),
    allow_private_ips: bool = False,
    blocked_hosts: set[str] | None = None,
) -> str:
    """
    Validate a URL for security (SSRF protection).

    Performs the following checks:
    1. URL scheme is allowed (http/https by default)
    2. Hostname is not in the blocked hosts list
    3. Hostname does not resolve to a private/reserved IP address

    Args:
        url: The URL to validate
        allowed_schemes: Tuple of allowed URL schemes
        allow_private_ips: If True, allows requests to private IP addresses
        blocked_hosts: Set of hostnames to block (in addition to private IPs)

    Returns:
        The validated and normalized URL

    Raises:
        URLValidationError: If the URL fails any security check
    """
    blocked_hosts = blocked_hosts or set()

    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise URLValidationError(f"Invalid URL format: {e}")  # noqa: B904

    # Check scheme
    if not parsed.scheme:
        raise URLValidationError("URL must include a scheme (http:// or https://)")

    if parsed.scheme.lower() not in allowed_schemes:
        raise URLValidationError(
            f"URL scheme '{parsed.scheme}' not allowed. "
            f"Allowed schemes: {', '.join(allowed_schemes)}"
        )

    # Check hostname exists
    hostname = parsed.hostname
    if not hostname:
        raise URLValidationError("URL must include a hostname")

    # Check blocked hosts
    hostname_lower = hostname.lower()
    if hostname_lower in blocked_hosts:
        raise URLValidationError(f"Host '{hostname}' is blocked")

    # Check for localhost variants
    localhost_variants = {
        "localhost",
        "localhost.localdomain",
        "local",
        "127.0.0.1",
        "::1",
        "0.0.0.0",
    }
    if hostname_lower in localhost_variants and not allow_private_ips:
        raise URLValidationError(f"Localhost access not allowed: {hostname}")

    # Resolve hostname and check IP
    if not allow_private_ips:
        try:
            literal_ip = ipaddress.ip_address(hostname)
        except ValueError:
            literal_ip = None
        if literal_ip is not None:
            if _is_private_ip(str(literal_ip)):
                raise URLValidationError(
                    f"Host '{hostname}' is a private IP address: {literal_ip}"
                )
            return url
        try:
            # Get all IP addresses for the hostname
            ip_addresses = socket.getaddrinfo(
                hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM
            )
            for _family, _, _, _, sockaddr in ip_addresses:
                ip_str = sockaddr[0]
                if _is_private_ip(ip_str):
                    raise URLValidationError(
                        f"Host '{hostname}' resolves to private IP address: {ip_str}"
                    )
        except socket.gaierror:
            # DNS resolution failed - let httpx handle this error
            # We don't block here because the hostname might be valid but temporarily unreachable  # noqa: E501
            pass
        except URLValidationError:
            # Re-raise our own exceptions
            raise
        except Exception:
            # Other errors during resolution - let httpx handle them
            pass

    return url


def _is_private_ip(ip_str: str) -> bool:
    """
    Check if an IP address is private/reserved.

    Private ranges include:
    - 10.0.0.0/8
    - 172.16.0.0/12
    - 192.168.0.0/16
    - 127.0.0.0/8 (loopback)
    - 169.254.0.0/16 (link-local)
    - ::1 (IPv6 loopback)
    - fc00::/7 (IPv6 unique local)
    - fe80::/10 (IPv6 link-local)

    Args:
        ip_str: IP address string (IPv4 or IPv6)

    Returns:
        True if the IP is private/reserved, False otherwise
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        )
    except ValueError:
        # Invalid IP address format - treat as potentially unsafe
        return True


def is_safe_url(
    url: str,
    allow_private_ips: bool = False,
    blocked_hosts: set[str] | None = None,
) -> bool:
    """
    Check if a URL is safe to fetch without raising an exception.

    Args:
        url: The URL to check
        allow_private_ips: If True, allows requests to private IP addresses
        blocked_hosts: Set of hostnames to block

    Returns:
        True if the URL passes validation, False otherwise
    """
    try:
        validate_url(
            url, allow_private_ips=allow_private_ips, blocked_hosts=blocked_hosts
        )
        return True
    except URLValidationError:
        return False

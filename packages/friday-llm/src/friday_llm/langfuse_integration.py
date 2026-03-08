# mypy: ignore-errors
"""
LangFuse observability integration for LiteLLM.

Configures LiteLLM's native ``"langfuse"`` callback so that every
``litellm.acompletion`` / ``litellm.aembedding`` call is
automatically traced in LangFuse.

Usage::

    from friday_llm.langfuse_integration import configure_langfuse

    langfuse_config = config.get("langfuse", {})
    configure_langfuse(langfuse_config)

The function is safe to call even when ``langfuse`` is not installed —
it will log a warning and return without error.
"""

import os
from typing import Any

from friday_core.logging import get_logger

logger = get_logger(__name__)

# Track whether we've already configured LangFuse
_langfuse_configured: bool = False


def configure_langfuse(config: dict[str, Any] | None = None) -> bool:
    """
    Enable LangFuse observability for all LiteLLM calls.

    Reads ``public_key``, ``secret_key``, and ``host`` from *config*
    and sets the corresponding ``LANGFUSE_*`` environment variables.
    Then registers LangFuse as a LiteLLM success/failure callback.

    This function is idempotent — calling it multiple times has no
    additional effect after the first successful configuration.

    Args:
        config: The ``langfuse:`` section from config.yaml.
            Expected keys: ``enabled``, ``public_key``,
            ``secret_key``, ``host``.

    Returns:
        ``True`` if LangFuse was successfully configured,
        ``False`` otherwise.
    """
    global _langfuse_configured

    if _langfuse_configured:
        logger.info("LangFuse already configured, skipping")
        return True

    if config is None or not config.get("enabled", False):
        logger.info("LangFuse disabled in configuration")
        return False

    public_key = config.get("public_key")
    secret_key = config.get("secret_key")
    host = config.get("host", "https://us.cloud.langfuse.com")

    if not public_key or not secret_key:
        logger.warning(
            "LangFuse enabled but missing keys — "
            "set langfuse.public_key and langfuse.secret_key "
            "in config.yaml"
        )
        return False

    # Verify the langfuse package is installed
    try:
        import langfuse  # noqa: F401
    except ImportError:
        logger.warning(
            "LangFuse enabled in config but the 'langfuse' "
            "package is not installed. "
            "Install with: pip install 'friday-llm[langfuse]'"
        )
        return False

    # Set env vars that LiteLLM's native callback reads
    os.environ["LANGFUSE_PUBLIC_KEY"] = public_key
    os.environ["LANGFUSE_SECRET_KEY"] = secret_key
    os.environ["LANGFUSE_HOST"] = host

    # Register the callback with LiteLLM
    import litellm

    # Preserve any existing callbacks
    existing = set(litellm.success_callback or [])
    existing.add("langfuse")
    litellm.success_callback = list(existing)

    existing_fail = set(litellm.failure_callback or [])
    existing_fail.add("langfuse")
    litellm.failure_callback = list(existing_fail)

    _langfuse_configured = True
    logger.info(
        "LangFuse observability enabled",
        host=host,
        public_key=public_key[:8] + "...",
    )
    return True

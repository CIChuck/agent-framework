import asyncio
import os

from friday_core.logging import get_logger

try:
    from massive import RESTClient
except ImportError:
    # Placeholder for development if the SDK is not installed
    class RESTClient:
        """Stub RESTClient for development without the Massive SDK installed."""

        def __init__(self, api_key):
            pass


from .exceptions import MassiveAuthError, MassiveRateLimitError
from .governor import MassiveGovernor
from .modules.crypto import CryptoModule
from .modules.equities import EquitiesModule
from .modules.indicators import IndicatorsModule

logger = get_logger(__name__)


class MassiveAgentClient:
    """
    Main entry point for the Massive Agent Core.

    Orchestrates modules (Equities, Crypto, Indicators) and manages
    the async Governor for tier-aware rate limiting. All SDK calls
    should go through ``execute_query`` to respect rate limits.
    """

    def __init__(self, api_key: str = None, tier: str = "free"):
        """
        Initialise the Massive Agent client.

        Args:
            api_key: Massive API key. Falls back to the ``MASSIVE_API_KEY``
                     environment variable when *None*.
            tier: API tier — ``"free"`` (5 req/min) or ``"starter"``.

        Raises:
            MassiveAuthError: If no API key is provided or found in the
                              environment.
        """
        self.api_key = api_key or os.getenv("MASSIVE_API_KEY")
        if not self.api_key:
            raise MassiveAuthError(
                "API key is missing. Provide it or set the MASSIVE_API_KEY environment variable."  # noqa: E501
            )

        self.tier = tier
        self.sdk = RESTClient(self.api_key)
        self.governor = MassiveGovernor(tier=self.tier)

        # Initialize Modules
        self.equities = EquitiesModule(self)
        self.crypto = CryptoModule(self)
        self.indicators = IndicatorsModule(self)

        logger.info(
            "MassiveAgentClient initialised",
            tier=self.tier,
        )

    async def probe_tier(self):
        """
        Automatically detect the API tier from response headers.

        Not yet implemented — the client relies on the *tier* constructor
        parameter for now.
        """
        # For now, we rely on the manual 'tier' parameter
        pass

    async def execute_query(self, func, *args, **kwargs):
        """
        Execute an SDK call through the Governor rate limiter.

        Synchronous SDK functions are dispatched to a thread-pool executor
        so the async event loop is never blocked.

        Args:
            func: The SDK callable to invoke.
            *args: Positional arguments forwarded to *func*.
            **kwargs: Keyword arguments forwarded to *func*.

        Returns:
            The raw result from the SDK call.

        Raises:
            MassiveRateLimitError: If the API returns HTTP 429 despite the
                                   governor.
        """
        await self.governor.wait()
        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, lambda: func(*args, **kwargs))
            logger.debug("SDK query succeeded", func=func.__name__)
            return result
        except Exception as e:
            if "429" in str(e):
                logger.error("Rate limit hit despite governor", func=func.__name__)
                raise MassiveRateLimitError("Rate limit hit despite governor.") from e
            logger.error("SDK query failed", func=func.__name__, error=str(e))
            raise

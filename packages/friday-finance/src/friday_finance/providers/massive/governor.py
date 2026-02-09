import asyncio

from friday_core.logging import get_logger

logger = get_logger(__name__)


class MassiveGovernor:
    """
    A tier-aware rate limiter using a modified Token Bucket algorithm.

    Enforces a minimum interval between successive API calls so that
    the Massive free-tier limit (5 requests / minute) is never exceeded.
    """

    TIER_INTERVALS = {
        "free": 12.05,   # 5 per minute ≈ 12 s spacing
        "starter": 0.05, # Effectively unlimited
    }

    def __init__(self, tier: str = "free"):
        """
        Initialise the governor.

        Args:
            tier: API tier — ``"free"`` or ``"starter"``.
        """
        self.tier = tier.lower()
        self.interval = self.TIER_INTERVALS.get(self.tier, 12.05)
        self.last_call = 0.0
        self.lock = asyncio.Lock()

    async def wait(self):
        """Ensure the next call respects the tier's time boundary."""
        async with self.lock:
            now = asyncio.get_running_loop().time()
            elapsed = now - self.last_call

            if elapsed < self.interval:
                sleep_time = self.interval - elapsed
                logger.debug("Governor throttling", sleep_seconds=round(sleep_time, 2))
                await asyncio.sleep(sleep_time)

            self.last_call = asyncio.get_running_loop().time()

    def update_tier(self, tier: str):
        """
        Switch to a different API tier at runtime.

        Args:
            tier: The new tier name (``"free"`` or ``"starter"``).
        """
        self.tier = tier.lower()
        self.interval = self.TIER_INTERVALS.get(self.tier, 12.05)
        logger.info("Governor tier updated", tier=self.tier, interval=self.interval)

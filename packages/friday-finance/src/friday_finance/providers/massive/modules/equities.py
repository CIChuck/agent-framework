# mypy: ignore-errors
from datetime import datetime, timedelta
from typing import Any

from friday_core.logging import get_logger

from ..registry import AssetRegistry

logger = get_logger(__name__)


class EquitiesModule:
    """
    Handles Stock and Index-proxy data fetching.

    Includes 'Market Day' logic so free-tier queries always target a
    valid trading day with available data.
    """

    def __init__(self, client):
        """
        Initialise the equities module.

        Args:
            client: A ``MassiveAgentClient`` instance used for SDK calls.
        """
        self.client = client

    def _resolve_market_day(self, target_date: datetime = None) -> str:
        """
        Ensure we are querying a valid trading day.

        If *target_date* falls on a weekend it is rolled back to the
        previous Friday. Defaults to T-1 (yesterday) to guarantee data
        availability on the free tier.

        Args:
            target_date: The desired date.  Defaults to yesterday.

        Returns:
            An ISO-formatted date string (``YYYY-MM-DD``).
        """
        if target_date is None:
            # Default to yesterday to avoid "restricted timeframe" errors on Free Tier
            target_date = datetime.now() - timedelta(days=1)

        # Simplistic business day roll-back
        while target_date.weekday() > 4:  # Saturday or Sunday
            target_date -= timedelta(days=1)

        return target_date.strftime("%Y-%m-%d")

    async def get_details(self, ticker: str) -> dict[str, Any]:
        """
        Fetch company / ETF background information.

        Args:
            ticker: Symbol or alias (e.g. ``"AAPL"``, ``"sp500"``).

        Returns:
            A dict with keys ``ticker``, ``name``, ``description``,
            ``homepage``, and ``market_cap``.
        """
        ticker = AssetRegistry.resolve_ticker(ticker)
        logger.info("Fetching ticker details", ticker=ticker)

        func = self.client.sdk.get_ticker_details
        result = await self.client.execute_query(func, ticker)

        return {
            "ticker": result.ticker,
            "name": result.name,
            "description": getattr(result, "description", "No description available."),
            "homepage": getattr(result, "homepage_url", ""),
            "market_cap": getattr(result, "market_cap", None),
        }

    async def get_eod_price(self, ticker: str) -> dict[str, Any]:
        """
        Fetch the most recent daily close (End-of-Day) OHLCV bar.

        Args:
            ticker: Symbol or alias.

        Returns:
            A dict with ``ticker``, ``date``, ``open``, ``high``,
            ``low``, ``close``, and ``volume``.
        """
        ticker = AssetRegistry.resolve_ticker(ticker)
        market_day = self._resolve_market_day()
        logger.info("Fetching EOD price", ticker=ticker, market_day=market_day)

        func = self.client.sdk.get_aggs

        result = await self.client.execute_query(
            func, ticker, 1, "day", market_day, market_day
        )

        if not result or len(result) == 0:
            return {"error": "No data found for the resolved market day."}

        last_bar = result[0]
        return {
            "ticker": ticker,
            "date": market_day,
            "open": last_bar.open,
            "high": last_bar.high,
            "low": last_bar.low,
            "close": last_bar.close,
            "volume": last_bar.volume,
        }

    async def get_market_summary(self, ticker: str) -> dict[str, Any]:
        """
        High-level tool call for agents.

        Combines identity details and price data into a single summary.
        On the free tier the Governor will space the two underlying calls.

        Args:
            ticker: Symbol or alias.

        Returns:
            A dict with ``summary`` (human-readable string), ``details``,
            and ``price_data``.
        """
        details = await self.get_details(ticker)
        price = await self.get_eod_price(ticker)

        return {
            "summary": f"{details['name']} is trading at ${price['close']} as of {price['date']}.",  # noqa: E501
            "details": details,
            "price_data": price,
        }

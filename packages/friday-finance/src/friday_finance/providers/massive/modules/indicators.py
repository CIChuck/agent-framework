from typing import Any

from friday_core.logging import get_logger

from ..registry import AssetRegistry

logger = get_logger(__name__)


class IndicatorsModule:
    """
    Interface to Massive's Technical Indicators API.

    Supports Simple Moving Average (SMA), Relative Strength Index (RSI),
    and trend analysis via Golden / Death Cross detection.
    """

    def __init__(self, client):
        """
        Initialise the indicators module.

        Args:
            client: A ``MassiveAgentClient`` instance used for SDK calls.
        """
        self.client = client

    async def get_sma(self, ticker: str, window: int = 50, timespan: str = "day") -> dict[str, Any]:
        """
        Fetch the Simple Moving Average for a ticker.

        Common windows: 50 (intermediate trend), 200 (long-term trend).

        Args:
            ticker: Symbol or alias.
            window: Number of periods for the moving average.
            timespan: Bar size — ``"day"``, ``"week"``, etc.

        Returns:
            A dict with ``ticker``, ``window``, ``value``, ``timestamp``,
            and ``indicator``.
        """
        ticker = AssetRegistry.resolve_ticker(ticker)
        logger.info("Fetching SMA", ticker=ticker, window=window, timespan=timespan)

        func = self.client.sdk.get_sma
        result = await self.client.execute_query(
            func,
            ticker,
            timestamp=None,  # Gets most recent
            timespan=timespan,
            window=window,
            series_type="close",
            order="desc",
            limit=1,
        )

        if not result or not hasattr(result, "values") or len(result.values) == 0:
            logger.warning("No SMA data returned", ticker=ticker, window=window)
            return {"ticker": ticker, "window": window, "value": None, "status": "no_data"}

        latest_value = result.values[0].value
        return {
            "ticker": ticker,
            "window": window,
            "value": round(latest_value, 2),
            "timestamp": result.values[0].timestamp,
            "indicator": "SMA",
        }

    async def get_rsi(self, ticker: str, window: int = 14) -> dict[str, Any]:
        """
        Fetch the Relative Strength Index (momentum indicator).

        The standard RSI window is 14 periods.

        Args:
            ticker: Symbol or alias.
            window: Number of periods (default 14).

        Returns:
            A dict with ``ticker``, ``window``, ``value``, and
            ``indicator``.
        """
        ticker = AssetRegistry.resolve_ticker(ticker)
        logger.info("Fetching RSI", ticker=ticker, window=window)

        func = self.client.sdk.get_rsi
        result = await self.client.execute_query(
            func,
            ticker,
            timespan="day",
            window=window,
            series_type="close",
            order="desc",
            limit=1,
        )

        latest_value = result.values[0].value if result and hasattr(result, "values") else None
        return {
            "ticker": ticker,
            "window": window,
            "value": round(latest_value, 2) if latest_value else None,
            "indicator": "RSI",
        }

    async def get_trend_analysis(self, ticker: str) -> dict[str, Any]:
        """
        Determine Golden Cross / Death Cross status.

        Compares SMA-50 against SMA-200.  Requires two API calls (spaced
        by ~12 s on the free tier).

        Args:
            ticker: Symbol or alias.

        Returns:
            A dict with ``ticker``, ``sma50``, ``sma200``, and
            ``sentiment`` (``"bullish"``, ``"bearish"``, or ``"neutral"``).
        """
        logger.info("Running trend analysis", ticker=ticker)
        sma50 = await self.get_sma(ticker, 50)
        sma200 = await self.get_sma(ticker, 200)

        status = "neutral"
        if sma50["value"] and sma200["value"]:
            status = "bullish" if sma50["value"] > sma200["value"] else "bearish"

        return {
            "ticker": ticker,
            "sma50": sma50["value"],
            "sma200": sma200["value"],
            "sentiment": status,
        }

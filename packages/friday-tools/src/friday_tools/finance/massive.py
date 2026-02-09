"""
Massive-backed finance tools.

Contains ``BaseTool`` wrappers around the ``friday_finance`` Massive provider,
exposing market data, crypto snapshots, and technical indicators to the
Friday agent tool registry.
"""

from typing import Any

from friday_core.logging import get_logger
from friday_finance import MassiveAgentClient

from ..definition import BaseTool

logger = get_logger(__name__)


class MassiveBaseTool(BaseTool):
    """
    Base class for all Massive-backed finance tools.

    Manages a shared ``MassiveAgentClient`` instance so that the
    Governor rate-limiter is applied consistently across tools.
    """

    def __init__(
        self,
        client: MassiveAgentClient | None = None,
        api_key: str | None = None,
        tier: str = "free",
    ):
        """
        Initialise the base tool.

        Args:
            client: An existing ``MassiveAgentClient`` to share across
                    tools. When *None* a new client is created.
            api_key: Massive API key (only used when *client* is *None*).
            tier: API tier (only used when *client* is *None*).
        """
        self.client = client or MassiveAgentClient(api_key=api_key, tier=tier)


class GetMarketDataTool(MassiveBaseTool):
    """
    Fetch market data for US Stocks, ETFs, and Indices.

    Supports three data types: ``summary`` (combined overview),
    ``price`` (EOD OHLCV), and ``details`` (company background).
    Automatic Market Day resolution handles weekends and holidays.
    """

    @property
    def name(self) -> str:
        """Unique tool identifier."""
        return "get_market_data"

    @property
    def description(self) -> str:
        """Human-readable description surfaced to the LLM."""
        return (
            "Get financial data for US Equities, ETFs, and "
            "major Indices. Can retrieve a comprehensive summary, "
            "current price (EOD), or company details. "
            "For Indices, use proxies like 'sp500' (SPY), "
            "'nasdaq100' (QQQ), 'total_bond' (AGG). "
            "Automatic 'Market Day' resolution handles "
            "weekends/holidays."
        )

    @property
    def category(self) -> str:
        """Tool category for registry filtering."""
        return "finance"

    @property
    def tags(self) -> list[str]:
        """Fine-grained tags for tool discovery."""
        return ["stocks", "market", "price", "massive"]

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """JSON Schema describing the tool's accepted parameters."""
        return {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": (
                        "Symbol or alias "
                        "(e.g., 'AAPL', 'sp500', 'total_bond')."
                    ),
                },
                "data_type": {
                    "type": "string",
                    "enum": ["summary", "price", "details"],
                    "default": "summary",
                    "description": (
                        "Type of data to fetch. 'summary' is "
                        "recommended for general queries."
                    ),
                },
            },
            "required": ["ticker"],
        }

    async def execute(self, **kwargs: Any) -> str:
        """
        Execute the market data query.

        Args:
            **kwargs: Must include ``ticker`` (str). Optionally
                      ``data_type`` (str, default ``"summary"``).

        Returns:
            A string representation of the result dict.
        """
        ticker = kwargs.get("ticker")
        data_type = kwargs.get("data_type", "summary")
        logger.info("Executing get_market_data", ticker=ticker, data_type=data_type)

        try:
            if data_type == "price":
                result = await self.client.equities.get_eod_price(ticker)
            elif data_type == "details":
                result = await self.client.equities.get_details(ticker)
            else:  # summary
                result = await self.client.equities.get_market_summary(ticker)
            return str(result)
        except Exception as e:
            logger.error("get_market_data failed", ticker=ticker, error=str(e))
            return f"Error fetching market data for {ticker}: {str(e)}"


class GetCryptoDataTool(MassiveBaseTool):
    """
    Fetch real-time Cryptocurrency snapshots.

    Returns current price, day change, and percentage change.
    Optionally compares BTC vs Bonds for a Risk-On / Risk-Off signal.
    """

    @property
    def name(self) -> str:
        """Unique tool identifier."""
        return "get_crypto_data"

    @property
    def description(self) -> str:
        """Human-readable description surfaced to the LLM."""
        return (
            "Get real-time snapshot data for Cryptocurrencies (e.g., BTC, ETH). "
            "Returns current price, day change, and percentage change. "
            "Markets are 24/7."
        )

    @property
    def category(self) -> str:
        """Tool category for registry filtering."""
        return "finance"

    @property
    def tags(self) -> list[str]:
        """Fine-grained tags for tool discovery."""
        return ["crypto", "bitcoin", "price", "massive"]

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """JSON Schema describing the tool's accepted parameters."""
        return {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Crypto symbol (e.g., 'BTC', 'ETH', 'BTC/USD').",
                },
                "check_risk_on": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "If true, compares BTC vs Bonds "
                        "for a 'Risk On/Off' signal."
                    ),
                },
            },
            "required": ["symbol"],
        }

    async def execute(self, **kwargs: Any) -> str:
        """
        Execute the crypto data query.

        Args:
            **kwargs: Must include ``symbol`` (str). Optionally
                      ``check_risk_on`` (bool, default *False*).

        Returns:
            A string representation of the result dict.
        """
        symbol = kwargs.get("symbol")
        check_risk = kwargs.get("check_risk_on", False)
        logger.info("Executing get_crypto_data", symbol=symbol, check_risk=check_risk)

        try:
            if check_risk:
                result = await self.client.crypto.get_risk_on_comparison()
                return str(result)

            result = await self.client.crypto.get_snapshot(symbol)
            return str(result)
        except Exception as e:
            logger.error("get_crypto_data failed", symbol=symbol, error=str(e))
            return f"Error fetching crypto data for {symbol}: {str(e)}"


class GetTechnicalAnalysisTool(MassiveBaseTool):
    """
    Calculate technical indicators for an asset.

    Supports Simple Moving Average (SMA), Relative Strength Index (RSI),
    and Trend Analysis (Golden / Death Cross).
    """

    # Indicator-specific default windows
    _DEFAULT_WINDOWS = {
        "sma": 50,
        "rsi": 14,
    }

    @property
    def name(self) -> str:
        """Unique tool identifier."""
        return "get_technical_analysis"

    @property
    def description(self) -> str:
        """Human-readable description surfaced to the LLM."""
        return (
            "Calculate technical indicators for an asset. "
            "Supports Simple Moving Average (SMA), Relative Strength Index (RSI), "
            "and Trend Analysis (Golden/Death Cross)."
        )

    @property
    def category(self) -> str:
        """Tool category for registry filtering."""
        return "finance"

    @property
    def tags(self) -> list[str]:
        """Fine-grained tags for tool discovery."""
        return ["technical-analysis", "indicators", "chart", "massive"]

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """JSON Schema describing the tool's accepted parameters."""
        return {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Symbol to analyze (e.g., 'AAPL', 'SPY').",
                },
                "indicator": {
                    "type": "string",
                    "enum": ["sma", "rsi", "trend"],
                    "description": "Indicator to calculate.",
                },
                "window": {
                    "type": "integer",
                    "description": (
                        "Period for SMA (default 50) or "
                        "RSI (default 14). Ignored for trend."
                    ),
                },
            },
            "required": ["ticker", "indicator"],
        }

    async def execute(self, **kwargs: Any) -> str:
        """
        Execute the technical analysis query.

        Args:
            **kwargs: Must include ``ticker`` (str) and ``indicator``
                      (``"sma"`` | ``"rsi"`` | ``"trend"``). Optionally
                      ``window`` (int).

        Returns:
            A string representation of the result dict.
        """
        ticker = kwargs.get("ticker")
        indicator = kwargs.get("indicator")
        default_window = self._DEFAULT_WINDOWS.get(indicator, 50)
        window = kwargs.get("window", default_window)
        logger.info(
            "Executing get_technical_analysis",
            ticker=ticker,
            indicator=indicator,
            window=window,
        )

        try:
            if indicator == "sma":
                result = await self.client.indicators.get_sma(ticker, window=window)
            elif indicator == "rsi":
                result = await self.client.indicators.get_rsi(ticker, window=window)
            elif indicator == "trend":
                result = await self.client.indicators.get_trend_analysis(ticker)
            else:
                return f"Unknown indicator: {indicator}"

            return str(result)
        except Exception as e:
            logger.error(
                "get_technical_analysis failed",
                ticker=ticker,
                indicator=indicator,
                error=str(e),
            )
            return f"Error performing technical analysis for {ticker}: {str(e)}"

from datetime import datetime
from typing import Any

from friday_core.logging import get_logger

from ..registry import AssetRegistry

logger = get_logger(__name__)


class CryptoModule:
    """
    Handles Cryptocurrency pairs (e.g., BTC/USD, ETH/USD).

    Crypto markets are 24/7 so there is no Market Day logic; the most
    recent previous-close aggregate is used to stay free-tier compatible.
    """

    def __init__(self, client):
        """
        Initialise the crypto module.

        Args:
            client: A ``MassiveAgentClient`` instance used for SDK calls.
        """
        self.client = client

    def _format_ticker(self, symbol: str) -> str:
        """
        Standardise a symbol to the Massive ``X:BTCUSD`` format.

        Args:
            symbol: Raw symbol string (e.g. ``"BTC"``, ``"BTC/USD"``,
                    ``"X:BTCUSD"``).

        Returns:
            The normalised ticker string.
        """
        symbol = symbol.upper().replace("/", "")
        if not symbol.startswith("X:"):
            if "USD" not in symbol:
                symbol += "USD"
            return f"X:{symbol}"
        return symbol

    async def get_snapshot(self, symbol: str) -> dict[str, Any]:
        """
        Get the most recent daily close (Previous Close) for a crypto pair.

        Uses ``get_previous_close_agg`` to ensure compatibility with the
        free tier.

        Args:
            symbol: Crypto symbol (e.g. ``"BTC"``, ``"ETH"``).

        Returns:
            A dict with ``symbol``, ``price``, ``day_change``,
            ``day_change_percent``, and ``last_updated``.

        Raises:
            MassiveNotFoundError: When no data is returned for the symbol.
        """
        ticker = self._format_ticker(symbol)
        logger.info("Fetching crypto snapshot", ticker=ticker)

        func = self.client.sdk.get_previous_close_agg
        result = await self.client.execute_query(func, ticker)

        if not result or len(result) == 0:
            logger.warning("No crypto data returned", ticker=ticker)
            return {"symbol": ticker, "error": "No data found."}

        last_bar = result[0]

        change_percent = 0.0
        if last_bar.open and last_bar.open != 0:
            change_percent = ((last_bar.close - last_bar.open) / last_bar.open) * 100

        return {
            "symbol": ticker,
            "price": last_bar.close,
            "day_change": last_bar.close - last_bar.open,
            "day_change_percent": round(change_percent, 2),
            "last_updated": (
                datetime.fromtimestamp(last_bar.timestamp / 1000).isoformat()
                if hasattr(last_bar, "timestamp")
                else datetime.now().isoformat()
            ),
            "note": "Data is Previous Close (Free Tier compatible)",
        }

    async def get_risk_on_comparison(self) -> dict[str, Any]:
        """
        Compare Bitcoin vs Bonds for a Risk-On / Risk-Off signal.

        Fetches the latest BTC snapshot and the latest bond (AGG) EOD
        price so the agent can assess relative momentum.

        Returns:
            A dict with ``risk_on_proxy`` (BTC data) and
            ``risk_off_proxy`` (AGG bond data).
        """
        btc = await self.get_snapshot("BTC")

        bond_ticker = AssetRegistry.resolve_ticker("total_bond")  # AGG
        logger.info("Fetching bond data for risk comparison", ticker=bond_ticker)

        # Fetch actual bond price data for a meaningful comparison
        bond_result = await self.client.equities.get_eod_price(bond_ticker)

        bond_proxy: dict[str, Any] = {
            "asset": "AGG (Bonds)",
            "ticker": bond_ticker,
        }
        if "error" not in bond_result:
            bond_proxy.update({
                "price": bond_result["close"],
                "date": bond_result["date"],
            })
        else:
            logger.warning("Bond data unavailable for risk comparison", error=bond_result["error"])
            bond_proxy["error"] = bond_result["error"]

        return {
            "risk_on_proxy": {
                "asset": "Bitcoin",
                "price": btc.get("price"),
                "change": btc.get("day_change_percent"),
            },
            "risk_off_proxy": bond_proxy,
        }

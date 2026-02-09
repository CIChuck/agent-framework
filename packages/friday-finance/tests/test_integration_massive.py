"""
Integration tests for the Massive API provider.

These tests use a real API key and hit the live Massive API.
They are rate-limited by the MassiveGovernor (~12 s between calls
on the free tier), so individual tests may take a while.

Run with:
    pytest packages/friday-finance/tests/test_integration_massive.py -v -s
"""

import pytest
from friday_finance import MassiveAgentClient

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

API_KEY = "pQBVbd4spIQEVEfc5WRjAonQXwBl_grA"


@pytest.fixture(scope="module")
def client():
    """
    Create a module-scoped MassiveAgentClient.

    Sharing one client across all tests ensures the Governor
    rate-limiter is honoured correctly.
    """
    return MassiveAgentClient(api_key=API_KEY, tier="free")


# ---------------------------------------------------------------------------
# Equities
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_eod_price(client):
    """Fetch EOD price for AAPL — should return a dict with close price."""
    result = await client.equities.get_eod_price("AAPL")
    assert isinstance(result, dict)
    assert result["ticker"] == "AAPL"
    assert "close" in result
    assert isinstance(result["close"], (int, float))


@pytest.mark.asyncio
async def test_get_details(client):
    """Fetch company details for AAPL — should include name and market_cap."""
    result = await client.equities.get_details("AAPL")
    assert isinstance(result, dict)
    assert result["ticker"] == "AAPL"
    assert "name" in result
    assert "market_cap" in result


@pytest.mark.asyncio
async def test_get_market_summary(client):
    """Market summary combines price + details for a ticker."""
    result = await client.equities.get_market_summary("AAPL")
    assert isinstance(result, dict)
    assert "summary" in result
    assert "details" in result
    assert "price_data" in result
    assert result["details"]["ticker"] == "AAPL"
    assert "close" in result["price_data"]


@pytest.mark.asyncio
async def test_alias_resolution(client):
    """Alias 'sp500' should resolve to SPY and return valid data."""
    result = await client.equities.get_eod_price("sp500")
    assert isinstance(result, dict)
    assert result["ticker"] == "SPY"
    assert "close" in result


# ---------------------------------------------------------------------------
# Crypto
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_crypto_snapshot(client):
    """Fetch a BTC snapshot — should include price and day_change fields."""
    result = await client.crypto.get_snapshot("BTC")
    assert isinstance(result, dict)
    assert "price" in result
    assert "day_change" in result
    assert "day_change_percent" in result


# ---------------------------------------------------------------------------
# Technical Indicators
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_sma(client):
    """Fetch SMA-50 for SPY — should return a numeric value."""
    result = await client.indicators.get_sma("SPY", window=50)
    assert isinstance(result, dict)
    assert result["indicator"] == "SMA"
    assert result["window"] == 50
    assert result["value"] is not None
    assert isinstance(result["value"], (int, float))


@pytest.mark.asyncio
async def test_get_rsi(client):
    """Fetch RSI-14 for AAPL — value should be between 0 and 100."""
    result = await client.indicators.get_rsi("AAPL", window=14)
    assert isinstance(result, dict)
    assert result["indicator"] == "RSI"
    assert result["value"] is not None
    assert 0 <= result["value"] <= 100


# ---------------------------------------------------------------------------
# Tool wrappers (via friday_tools.finance)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_market_data_tool(client):
    """GetMarketDataTool should return a string result via execute()."""
    from friday_tools.finance import GetMarketDataTool

    tool = GetMarketDataTool(client=client)
    result = await tool.execute(ticker="AAPL", data_type="price")
    assert isinstance(result, str)
    assert "AAPL" in result
    assert "close" in result


@pytest.mark.asyncio
async def test_crypto_data_tool(client):
    """GetCryptoDataTool should return a string result via execute()."""
    from friday_tools.finance import GetCryptoDataTool

    tool = GetCryptoDataTool(client=client)
    result = await tool.execute(symbol="BTC")
    assert isinstance(result, str)
    assert "price" in result


@pytest.mark.asyncio
async def test_technical_analysis_tool(client):
    """GetTechnicalAnalysisTool should return SMA data as a string."""
    from friday_tools.finance import GetTechnicalAnalysisTool

    tool = GetTechnicalAnalysisTool(client=client)
    result = await tool.execute(ticker="SPY", indicator="sma", window=50)
    assert isinstance(result, str)
    assert "SMA" in result

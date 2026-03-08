# mypy: ignore-errors
import time

import pytest
from friday_finance.providers.massive.client import MassiveAgentClient
from friday_finance.providers.massive.exceptions import MassiveAuthError
from friday_finance.providers.massive.governor import MassiveGovernor
from friday_finance.providers.massive.registry import AssetRegistry

# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


def test_registry_resolution():
    """Verify alias-to-ticker translation and passthrough."""
    assert AssetRegistry.resolve_ticker("sp500") == "SPY"
    assert AssetRegistry.resolve_ticker("AAPL") == "AAPL"
    assert AssetRegistry.resolve_ticker("total bond") == "AGG"


def test_registry_metadata():
    """Verify metadata lookup for a resolved ticker."""
    meta = AssetRegistry.get_metadata("SPY")
    assert meta is not None
    assert meta["ticker"] == "SPY"
    assert "S&P 500" in meta["name"]


def test_registry_metadata_unknown():
    """Verify metadata returns None for unknown tickers."""
    assert AssetRegistry.get_metadata("ZZZZZ") is None


# ---------------------------------------------------------------------------
# Governor tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_governor_free_tier():
    """Free tier governor should enforce >= 12 s spacing between calls."""
    gov = MassiveGovernor(tier="free")
    assert gov.interval > 12

    start = time.time()
    await gov.wait()  # First call is instant
    await gov.wait()  # Second call should wait
    end = time.time()

    assert (end - start) >= 12


@pytest.mark.asyncio
async def test_governor_starter_tier():
    """Starter tier governor should impose near-zero wait."""
    gov = MassiveGovernor(tier="starter")
    assert gov.interval < 1

    start = time.time()
    await gov.wait()
    await gov.wait()
    end = time.time()

    assert (end - start) < 1


@pytest.mark.asyncio
async def test_governor_update_tier():
    """Updating tier should change the interval immediately."""
    gov = MassiveGovernor(tier="free")
    assert gov.interval > 12

    gov.update_tier("starter")
    assert gov.interval < 1
    assert gov.tier == "starter"


# ---------------------------------------------------------------------------
# Client tests
# ---------------------------------------------------------------------------


def test_client_raises_on_missing_api_key(monkeypatch):
    """Client must raise MassiveAuthError when no API key is available."""
    monkeypatch.delenv("MASSIVE_API_KEY", raising=False)
    with pytest.raises(MassiveAuthError):
        MassiveAgentClient(api_key=None)


def test_client_accepts_explicit_api_key(monkeypatch):
    """Client should initialise successfully with an explicit key."""
    monkeypatch.delenv("MASSIVE_API_KEY", raising=False)
    client = MassiveAgentClient(api_key="test-key-123", tier="starter")
    assert client.api_key == "test-key-123"
    assert client.tier == "starter"


def test_client_reads_env_api_key(monkeypatch):
    """Client should fall back to MASSIVE_API_KEY env var."""
    monkeypatch.setenv("MASSIVE_API_KEY", "env-key-456")
    client = MassiveAgentClient()
    assert client.api_key == "env-key-456"

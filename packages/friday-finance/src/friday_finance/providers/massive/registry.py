

class AssetRegistry:
    """
    Manages the translation of human-readable concepts into Massive-compatible tickers.
    Specifically designed to provide ETF proxies for Indices and Bonds.
    """
    
    # Mapping of categories to their most liquid ETF proxy
    PROXIES = {
        # Indices
        "sp500": {"ticker": "SPY", "name": "S&P 500 Index (via SPY)"},
        "nasdaq100": {"ticker": "QQQ", "name": "Nasdaq-100 (via QQQ)"},
        "dowjones": {"ticker": "DIA", "name": "Dow Jones Industrial Average (via DIA)"},
        "russell2000": {"ticker": "IWM", "name": "Russell 2000 (via IWM)"},
        
        # Bonds / Fixed Income
        "total_bond": {"ticker": "AGG", "name": "U.S. Aggregate Bond Index"},
        "treasury_long": {"ticker": "TLT", "name": "20+ Year Treasury Bond"},
        "treasury_mid": {"ticker": "IEF", "name": "7-10 Year Treasury Bond"},
        "treasury_short": {"ticker": "SHY", "name": "1-3 Year Treasury Bond"},
        "corp_bond": {"ticker": "LQD", "name": "Investment Grade Corporate Bond"},
        "high_yield": {"ticker": "HYG", "name": "High Yield Corporate Bond"},
    }

    @classmethod
    def resolve_ticker(cls, query: str) -> str:
        """
        Translates a common name or alias into a ticker. 
        If it's already a ticker (4 characters or fewer), it returns it as-is.
        """
        query_clean = query.lower().replace(" ", "_")
        if query_clean in cls.PROXIES:
            return cls.PROXIES[query_clean]["ticker"]
        
        # Fallback: Assume it's already a ticker
        return query.upper()

    @classmethod
    def get_metadata(cls, ticker: str) -> dict | None:
        """Returns internal registry metadata for a given ticker proxy."""
        for _key, data in cls.PROXIES.items():
            if data["ticker"] == ticker.upper():
                return data
        return None

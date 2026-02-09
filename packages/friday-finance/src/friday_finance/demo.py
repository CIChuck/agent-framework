import asyncio
import json
import os
import time
from collections.abc import Coroutine
from typing import Any

from friday_finance import MassiveAgentClient

# ANSI Colors for nicer CLI output
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_header(title: str):
    print(f"\n{BOLD}{CYAN}=== {title} ==={RESET}")

def print_result(label: str, data: Any):
    if isinstance(data, (dict, list)):
        formatted = json.dumps(data, indent=2, default=str)
        print(f"{GREEN}{label}:{RESET}\n{formatted}")
    else:
        print(f"{GREEN}{label}:{RESET} {data}")

def print_error(label: str, error: Exception):
    print(f"{RED}{label} FAILED:{RESET} {error}")

async def run_step(name: str, coro: Coroutine):
    print(f"\n{YELLOW}Running: {name}...{RESET}")
    start = time.time()
    try:
        result = await coro
        elapsed = time.time() - start
        print_result(f"Result ({elapsed:.2f}s)", result)
    except Exception as e:
        print_error(name, e)

async def async_main():
    print_header("Friday Finance - Massive Provider Reference App")

    # 1. Setup & Auth
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        print(f"{RED}Error: MASSIVE_API_KEY environment variable is not set.{RESET}")
        print("Please export it and try again:")
        print("  export MASSIVE_API_KEY='your_key_here'")
        return

    # Check for tier override
    tier = os.getenv("MASSIVE_TIER", "free")
    print(f"Initializing Client (Tier: {BOLD}{tier}{RESET})...")
    
    try:
        client = MassiveAgentClient(api_key=api_key, tier=tier)
    except Exception as e:
        print_error("Initialization", e)
        return

    # 2. Equities Module Tests
    print_header("Testing Equities Module")
    
    # A. Company Details
    await run_step("get_details('AAPL')", 
                   client.equities.get_details("AAPL"))

    # B. EOD Price
    await run_step("get_eod_price('MSFT')", 
                   client.equities.get_eod_price("MSFT"))

    # C. Market Summary (Combines Details + Price)
    await run_step("get_market_summary('NVDA')", 
                   client.equities.get_market_summary("NVDA"))
    
    # D. ETF Proxy Lookup (Registry Test)
    print(f"\n{YELLOW}Testing Registry Lookup (sp500 -> SPY)...{RESET}")
    await run_step("get_eod_price('sp500')", 
                   client.equities.get_eod_price("sp500"))

    # 3. Crypto Module Tests
    print_header("Testing Crypto Module (24/7)")

    # A. Snapshot
    await run_step("get_snapshot('BTC')", 
                   client.crypto.get_snapshot("BTC"))
    
    # B. Risk On/Off Comparison
    await run_step("get_risk_on_comparison() [BTC vs AGG]", 
                   client.crypto.get_risk_on_comparison())

    # 4. Indicators Module Tests
    print_header("Testing Indicators Module")

    # A. SMA (Simple Moving Average)
    await run_step("get_sma('SPY', window=50)", 
                   client.indicators.get_sma("SPY", window=50))

    # B. RSI (Relative Strength Index)
    await run_step("get_rsi('SPY', window=14)", 
                   client.indicators.get_rsi("SPY", window=14))

    # C. Trend Analysis (Golden Cross Check)
    # Note: This makes 2 calls (SMA50 + SMA200). 
    # On Free tier, this will demonstrate the Governor waiting 12s between calls.
    print(f"\n{YELLOW}Testing Trend Analysis (Expect delays on Free Tier)...{RESET}")
    await run_step("get_trend_analysis('SPY')", 
                   client.indicators.get_trend_analysis("SPY"))

    print_header("Test Complete")

def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print(f"\n{RED}Test interrupted by user.{RESET}")

if __name__ == "__main__":
    main()

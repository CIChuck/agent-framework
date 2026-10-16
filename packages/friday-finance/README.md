# Friday Finance

An asynchronous integration around the Massive Python SDK for equities, cryptocurrency and technical indicators. Data access remains subject to the configured provider account and plan.

**Distribution:** [friday-framework-finance](https://pypi.org/project/friday-framework-finance/) · **Import:** `friday_finance`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-finance==0.1.0a4"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: resolve an asset alias locally

```python
from friday_finance import AssetRegistry

print(AssetRegistry.resolve_ticker("sp500"))
```

This only resolves a built-in alias; it makes no provider request. Querying data requires a Massive account/API key and network access.

## Query market data

Set `MASSIVE_API_KEY` in your process environment using your normal secret-management method. This complete example performs a **live** provider request:

```python
import asyncio

from friday_finance import MassiveAgentClient

async def main() -> None:
    client = MassiveAgentClient(tier="free")
    details = await client.equities.get_details("AAPL")
    print(details["ticker"])

asyncio.run(main())
```

`MassiveAgentClient` accepts an explicit `api_key` or reads `MASSIVE_API_KEY`. Set `tier` to your actual account tier. Its governor controls calls issued through `execute_query`; direct use of `client.sdk` bypasses that governor. `probe_tier()` is a placeholder and does not detect your plan.

`equities`, `crypto` and `indicators` expose the provider modules. Data freshness and availability depend on endpoint, market and entitlement; a wrapper does not guarantee real-time data. Weekend rollback in equity date selection is not a complete exchange-holiday calendar. Missing credentials raise `MassiveAuthError`. `execute_query()` maps exceptions whose message contains `429` to `MassiveRateLimitError`; other SDK/transport exceptions propagate unchanged, including remote authentication, timeout and not-found failures. The declared Friday timeout/not-found classes are not currently used to normalize those failures; handle the underlying provider exceptions as well.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
There is no package-local test suite yet. Start with an import check:

```bash
uv run --no-sync python -c "import friday_finance"
```

No package-local suite is currently present. Live examples and `friday-finance-demo` need credentials and may consume provider quota; they are not offline smoke tests.
## Documentation and support

[Agent-facing finance tools](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-tools/README.md) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-finance/src/friday_finance) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).

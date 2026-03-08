# mypy: ignore-errors
"""
Friday Finance - Financial data provider integration.

This package provides data-access modules for financial APIs.
Tool wrappers (BaseTool subclasses) live in ``friday_tools.finance``.
"""

from .providers.massive import (
    AssetRegistry,
    CryptoModule,
    EquitiesModule,
    IndicatorsModule,
    MassiveAgentClient,
    MassiveAuthError,
    MassiveBaseException,
    MassiveGovernor,
    MassiveMarketClosedError,
    MassiveNotFoundError,
    MassiveRateLimitError,
    MassiveTimeoutError,
)

__all__ = [
    "MassiveAgentClient",
    "MassiveGovernor",
    "AssetRegistry",
    "EquitiesModule",
    "CryptoModule",
    "IndicatorsModule",
    "MassiveAuthError",
    "MassiveBaseException",
    "MassiveMarketClosedError",
    "MassiveNotFoundError",
    "MassiveRateLimitError",
    "MassiveTimeoutError",
]

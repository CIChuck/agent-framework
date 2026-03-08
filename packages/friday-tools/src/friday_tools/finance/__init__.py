# mypy: ignore-errors
"""
Finance tools for AI agents.

Wraps financial data providers (e.g. Massive) as ``BaseTool`` subclasses
that can be registered in the Friday tool registry.
"""

from .massive import (
    GetCryptoDataTool,
    GetMarketDataTool,
    GetTechnicalAnalysisTool,
    MassiveBaseTool,
)

__all__ = [
    "MassiveBaseTool",
    "GetMarketDataTool",
    "GetCryptoDataTool",
    "GetTechnicalAnalysisTool",
]

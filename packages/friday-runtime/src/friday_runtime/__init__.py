"""
Friday Runtime — Headless runtime kernel for the Friday Agent Framework.

Provides the RuntimeKernel, the central orchestration layer that manages
dependency injection, service lifecycle, and agent execution without
requiring the CLI presentation layer.
"""

from friday_runtime.config import RuntimeConfig
from friday_runtime.kernel import RuntimeKernel

__all__ = [
    "RuntimeConfig",
    "RuntimeKernel",
]

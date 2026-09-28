"""Runtime tool loading helpers for declarative provider-aware registry assembly."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from functools import lru_cache
from typing import Any

from friday_agent import DefaultToolRegistry
from friday_core.interfaces import ToolDefinition

from friday_runtime.config import ToolProviderConfig, ToolsConfig


class ToolProviderLoadError(RuntimeError):
    """Raised when a configured runtime tool provider cannot be loaded."""


def register_runtime_tools(
    registry: DefaultToolRegistry,
    config: ToolsConfig,
) -> None:
    """Register synchronous native providers; DI owns async MCP discovery."""
    for tool in _select_builtin_tools(config.providers.builtin):
        registry.register(tool)

    for tool in _select_friday_tools(config.providers.friday_tools):
        registry.register(tool)

def _select_builtin_tools(provider: ToolProviderConfig) -> list[ToolDefinition]:
    if not provider.enabled:
        return []

    catalog = _builtin_tool_catalog()
    return _filter_catalog(catalog, provider)


def _select_friday_tools(provider: ToolProviderConfig) -> list[ToolDefinition]:
    if not provider.enabled:
        return []

    catalog = _friday_tools_catalog()
    return _filter_catalog(catalog, provider)


@lru_cache(maxsize=1)
def _builtin_tool_catalog() -> tuple[ToolDefinition, ...]:
    temp_registry = DefaultToolRegistry()
    temp_registry.load_decorated_tools()
    return tuple(sorted(temp_registry.list_tools(), key=lambda tool: tool.name))


@lru_cache(maxsize=1)
def _friday_tools_catalog() -> tuple[ToolDefinition, ...]:
    try:
        friday_tools = importlib.import_module("friday_tools")
    except Exception as exc:
        raise ToolProviderLoadError(
            f"Unable to import friday_tools package for runtime discovery: {exc}"
        ) from exc

    modules = [friday_tools]
    if hasattr(friday_tools, "__path__"):
        module_names = sorted(
            module_name
            for _, module_name, _ in pkgutil.walk_packages(
                friday_tools.__path__,
                f"{friday_tools.__name__}.",
            )
        )
        for module_name in module_names:
            try:
                modules.append(importlib.import_module(module_name))
            except Exception as exc:
                raise ToolProviderLoadError(
                    f"Unable to import friday_tools module '{module_name}': {exc}"
                ) from exc

    discovered: dict[str, ToolDefinition] = {}
    for module in modules:
        for value in vars(module).values():
            if inspect.isclass(value) or not isinstance(value, ToolDefinition):
                continue
            if not isinstance(getattr(value, "name", None), str):
                continue
            if not isinstance(getattr(value, "category", None), str):
                continue
            discovered.setdefault(value.name, value)

    return tuple(sorted(discovered.values(), key=lambda tool: tool.name))


def _filter_catalog(
    catalog: tuple[ToolDefinition, ...],
    provider: ToolProviderConfig,
) -> list[ToolDefinition]:
    by_name = {tool.name: tool for tool in catalog}

    if provider.mode == "selected":
        selected: dict[str, ToolDefinition] = {}
        if provider.include_categories:
            selected.update(
                {
                    tool.name: tool
                    for tool in catalog
                    if tool.category in provider.include_categories
                }
            )
        for tool_name in provider.include_tools:
            tool = by_name.get(tool_name)
            if tool is not None:
                selected[tool_name] = tool
    else:
        selected = {tool.name: tool for tool in catalog}
        if provider.include_categories:
            selected = {
                name: tool
                for name, tool in selected.items()
                if tool.category in provider.include_categories
            }
        for tool_name in provider.include_tools:
            tool = by_name.get(tool_name)
            if tool is not None:
                selected[tool_name] = tool

    if provider.exclude_categories:
        selected = {
            name: tool
            for name, tool in selected.items()
            if tool.category not in provider.exclude_categories
        }

    for tool_name in provider.exclude_tools:
        selected.pop(tool_name, None)

    return [selected[name] for name in sorted(selected)]


def validate_agent_tool_bindings(
    *,
    agent_name: str,
    declared_tools: list[str],
    available_tool_names: set[str],
) -> None:
    """Fail hard when an agent references tools unavailable in the runtime."""
    missing = sorted({tool_name for tool_name in declared_tools if tool_name not in available_tool_names})
    if missing:
        raise ValueError(
            f"Agent '{agent_name}' references unavailable tool(s): {missing}"
        )


def collect_profile_tool_references(profile: Any) -> list[str]:
    """Collect all tool references declared across an agent profile."""
    ordered: list[str] = []
    seen: set[str] = set()
    for field_name in ("tools", "injected_tools", "available_tools", "required_tools"):
        values = getattr(profile, field_name, [])
        if not isinstance(values, list):
            continue
        for value in values:
            if not isinstance(value, str):
                continue
            stripped = value.strip()
            if stripped and stripped not in seen:
                ordered.append(stripped)
                seen.add(stripped)
    return ordered

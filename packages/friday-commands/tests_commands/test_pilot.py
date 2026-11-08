"""Neutral pilot contract tests against the frozen Chat metadata oracle."""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from dataclasses import FrozenInstanceError, asdict
from pathlib import Path
from textwrap import dedent

import pytest
from friday_commands import (
    PILOT_SPECS,
    CommandExecution,
    CommandOutcome,
    CommandRegistry,
    CommandRequest,
    CommandSpec,
    ExitData,
    HelpData,
    NoData,
    UiEffect,
    build_pilot_handlers,
    describe_help,
)

ROOT = Path(__file__).resolve().parents[3]
SPECS = {spec.name: spec for spec in PILOT_SPECS}


class Catalog:
    def __init__(self, specs: tuple[CommandSpec, ...] = PILOT_SPECS) -> None:
        self.entries = list(specs)
        self.calls: list[tuple[str, str | None]] = []

    def specs(self) -> tuple[CommandSpec, ...]:
        self.calls.append(("specs", None))
        return tuple(self.entries)

    def lookup_key(self, key: str) -> CommandSpec | None:
        self.calls.append(("lookup_key", key))
        return next(
            (spec for spec in self.entries if key in (spec.name, *spec.aliases)),
            None,
        )


class TripwireCatalog:
    def specs(self) -> tuple[CommandSpec, ...]:
        raise AssertionError("Unexpected catalog read")

    def lookup_key(self, key: str) -> CommandSpec | None:
        raise AssertionError("Unexpected catalog read")


def request(name: str, *args: str) -> CommandRequest:
    return CommandRequest(name, args, SPECS[name])


def test_exact_pilot_metadata_matches_frozen_independent_baseline() -> None:
    baseline = json.loads(
        (
            ROOT
            / "docs/planning/active/command-refactor/validation/pilot/baseline.json"
        ).read_text()
    )["observations"]["metadata"]
    assert tuple(spec.name for spec in PILOT_SPECS) == ("help", "exit", "cls")
    for spec in PILOT_SPECS:
        assert json.loads(json.dumps(asdict(spec))) == baseline[spec.name]
    with pytest.raises(FrozenInstanceError):
        PILOT_SPECS[0].name = "changed"


def test_factory_does_not_read_catalog_or_register_defaults() -> None:
    registry = CommandRegistry()
    first = build_pilot_handlers(TripwireCatalog())
    second = build_pilot_handlers(TripwireCatalog())
    assert set(first) == {"help", "exit", "cls"}
    assert registry.specs() == ()
    assert registry.names() == frozenset()
    assert first is not second
    with pytest.raises(TypeError):
        first["another"] = first["help"]
    with pytest.raises(TypeError):
        del first["exit"]


@pytest.mark.parametrize("focus", [None, ""])
def test_general_help_sorts_one_catalog_snapshot(focus: str | None) -> None:
    catalog = Catalog(PILOT_SPECS)
    outcome = describe_help(catalog, focus)
    assert isinstance(outcome.data, HelpData)
    assert tuple(spec.name for spec in outcome.data.commands) == ("cls", "exit", "help")
    assert outcome.data.focused_name is None
    assert outcome.error is None
    assert outcome.ui_effects == ()
    assert catalog.calls == [("specs", None)]
    catalog.entries.clear()
    assert len(outcome.data.commands) == 3


def test_empty_catalog_returns_general_help_without_effects() -> None:
    outcome = describe_help(Catalog(()))
    assert outcome == CommandOutcome(data=HelpData(()))


@pytest.mark.parametrize(
    ("focus", "key"),
    [
        (" Q ", "q"),
        ("/ Q ", "q"),
        (" /Q ", "/q"),
        ("//Q", "/q"),
        ("///Q", "//q"),
        ("/ /Q", "/q"),
        ("\tQ\n", "q"),
        (" ", ""),
        ("/ ", ""),
    ],
)
def test_focused_help_normalizes_once_and_uses_only_exact_lookup(
    focus: str, key: str
) -> None:
    target = CommandSpec("target", "Target", "custom", "/target")
    calls: list[str] = []

    class FocusCatalog(TripwireCatalog):
        def lookup_key(self, actual: str) -> CommandSpec | None:
            calls.append(actual)
            return target if actual == key else None

    outcome = describe_help(FocusCatalog(), focus)
    assert outcome == CommandOutcome(data=HelpData((target,), focused_name="target"))
    assert calls == [key]


@pytest.mark.parametrize("focus", ["q", "/quit", "CLEARSCREEN"])
def test_focused_alias_reports_canonical_name(focus: str) -> None:
    catalog = Catalog()
    outcome = describe_help(catalog, focus)
    expected = "cls" if focus == "CLEARSCREEN" else "exit"
    assert outcome == CommandOutcome(data=HelpData((SPECS[expected],), expected))
    assert len(catalog.calls) == 1
    assert catalog.calls[0][0] == "lookup_key"


@pytest.mark.parametrize("focus", ["/ Missing ", "//q", " "])
def test_unknown_help_returns_exact_normalized_error(focus: str) -> None:
    catalog = Catalog()
    outcome = describe_help(catalog, focus)
    key = focus.removeprefix("/").strip().lower()
    assert outcome.data is None
    assert outcome.error is not None
    assert outcome.error.code == "unknown_command"
    assert outcome.error.command_name == key
    assert outcome.error.usage is None
    assert outcome.ui_effects == ()
    assert catalog.calls == [("lookup_key", key)]


@pytest.mark.parametrize("focus", [False, 0, [], {}, (), 5, object()])
def test_non_string_focus_rejected_before_catalog_access(focus: object) -> None:
    with pytest.raises(TypeError):
        describe_help(TripwireCatalog(), focus)


def test_string_subclass_focus_is_supported() -> None:
    class Focus(str):
        pass

    assert describe_help(Catalog(), Focus("/Q")).data == HelpData(
        (SPECS["exit"],), "exit"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("args", [(), ("",), ("exit",), ("q", "ignored", "more")])
async def test_help_handler_invokes_shared_selection_once(
    monkeypatch: pytest.MonkeyPatch, args: tuple[str, ...]
) -> None:
    import friday_commands.pilot as pilot

    catalog = Catalog()
    expected = CommandOutcome(data=HelpData(()))
    calls = []

    def select(actual_catalog, focus=None):
        calls.append((actual_catalog, focus))
        return expected

    monkeypatch.setattr(pilot, "describe_help", select)
    outcome = await build_pilot_handlers(catalog)["help"](
        request("help", *args), CommandExecution()
    )
    assert outcome is expected
    assert calls == [(catalog, args[0] if args else None)]
    assert catalog.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["exit", "cls"])
@pytest.mark.parametrize("args", [(), ("ignored", "extra")])
async def test_exit_clear_return_only_typed_requests_without_catalog_or_session_access(
    name: str, args: tuple[str, ...], monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = []
    original = CommandExecution.__getattribute__
    execution = CommandExecution("unused")

    def tripwire(self, attr):
        calls.append(attr)
        raise AssertionError("Unexpected execution/context read")

    with monkeypatch.context() as patch:
        patch.setattr(CommandExecution, "__getattribute__", tripwire)
        result = await build_pilot_handlers(TripwireCatalog())[name](
            request(name, *args), execution
        )
    assert CommandExecution.__getattribute__ is original
    assert calls == []
    if name == "exit":
        assert result == CommandOutcome(data=ExitData(True))
    else:
        assert result == CommandOutcome(
            data=NoData(), ui_effects=(UiEffect.CLEAR_SCREEN,)
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("handler_name", "other_name"),
    [
        (own, other)
        for own in ("help", "exit", "cls")
        for other in ("help", "exit", "cls")
        if own != other
    ],
)
async def test_wrong_canonical_request_fails_before_catalog_read(
    handler_name: str, other_name: str
) -> None:
    with pytest.raises(ValueError):
        await build_pilot_handlers(TripwireCatalog())[handler_name](
            request(other_name), CommandExecution()
        )


class RequestSubclass(CommandRequest):
    pass


class ExecutionSubclass(CommandExecution):
    pass


class FieldsTripwire:
    def __getattribute__(self, name: str):
        raise AssertionError("Inspected a field before type validation")


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["help", "exit", "cls"])
@pytest.mark.parametrize(
    "bad_request",
    [None, {}, FieldsTripwire, RequestSubclass("help", (), SPECS["help"])],
    ids=["none", "mapping", "fields", "subclass"],
)
async def test_request_requires_exact_model_before_field_inspection(
    name: str, bad_request: object
) -> None:
    if bad_request is FieldsTripwire:
        bad_request = FieldsTripwire()
    with pytest.raises(TypeError):
        await build_pilot_handlers(TripwireCatalog())[name](
            bad_request, CommandExecution()
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["help", "exit", "cls"])
@pytest.mark.parametrize(
    "bad_execution", [None, {}, FieldsTripwire, ExecutionSubclass()]
)
async def test_execution_type_is_checked_before_wrong_request_name(
    name: str, bad_execution: object
) -> None:
    other = "exit" if name == "help" else "help"
    if bad_execution is FieldsTripwire:
        bad_execution = FieldsTripwire()
    with pytest.raises(TypeError):
        await build_pilot_handlers(TripwireCatalog())[name](
            request(other), bad_execution
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("focused", [False, True])
@pytest.mark.parametrize("cancel", [False, True])
async def test_catalog_errors_and_cancellation_propagate_once(
    focused: bool, cancel: bool
) -> None:
    failure = asyncio.CancelledError() if cancel else RuntimeError("catalog failure")
    calls = []

    class FailingCatalog:
        def specs(self) -> tuple[CommandSpec, ...]:
            calls.append("specs")
            raise failure

        def lookup_key(self, key: str) -> CommandSpec | None:
            calls.append(key)
            raise failure

    with pytest.raises(type(failure)) as caught:
        await build_pilot_handlers(FailingCatalog())["help"](
            request("help", *(("q",) if focused else ())), CommandExecution()
        )
    assert caught.value is failure
    assert calls == ["q" if focused else "specs"]


@pytest.mark.parametrize("optimized", [False, True])
def test_standalone_pilot_uses_only_stdlib(optimized: bool) -> None:
    source = str(ROOT / "packages/friday-commands/src")
    script = dedent(
        f"""
        import sys
        sys.path.insert(0, {source!r})
        class StdlibOnly:
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split('.')[0] not in sys.stdlib_module_names | {{'friday_commands'}}:
                    raise ModuleNotFoundError(fullname)
        sys.meta_path.insert(0, StdlibOnly())
        import asyncio
        from friday_commands import (
            PILOT_SPECS, CommandExecution, CommandRegistry, ExitData,
            HelpData, NoData, UiEffect, build_pilot_handlers,
        )
        registry = CommandRegistry()
        class Catalog:
            def specs(self):
                return registry.specs()
            def lookup_key(self, key):
                exact = {{k: s for s in registry.specs() for k in (s.name, *s.aliases)}}
                return exact.get(key)
        handlers = build_pilot_handlers(Catalog())
        if registry.names():
            raise RuntimeError('implicit defaults')
        for spec in PILOT_SPECS:
            registry.register(spec, handlers[spec.name])
        async def main():
            for text in ('/help', '/help /q', '/exit ignored', '/quit', '/q', '/cls', '/clearscreen extra'):
                result = await registry.execute_text(text, CommandExecution())
                if not result.handled or result.outcome is None:
                    raise RuntimeError(text)
                data = result.outcome.data
                if text.startswith('/help') and not isinstance(data, HelpData):
                    raise RuntimeError('help data')
                if text.startswith(('/exit', '/quit', '/q')) and data != ExitData(True):
                    raise RuntimeError('exit data')
                if text.startswith(('/cls', '/clearscreen')):
                    if data != NoData() or result.outcome.ui_effects != (UiEffect.CLEAR_SCREEN,):
                        raise RuntimeError('clear effect')
        asyncio.run(main())
        if any(n.startswith(('friday_chat', 'friday_cli', 'friday_runtime', 'rich')) for n in sys.modules):
            raise RuntimeError('host import')
        print('Standalone neutral pilot passed')
        """
    )
    result = subprocess.run(
        [sys.executable, "-I", "-B", *(["-O"] if optimized else []), "-c", script],
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Standalone neutral pilot passed"

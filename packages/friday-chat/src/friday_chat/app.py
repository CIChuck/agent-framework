"""Application lifecycle for FridayV2."""

from __future__ import annotations

import sys
from collections.abc import Awaitable, Callable, Coroutine, Sequence
from dataclasses import dataclass, field
from typing import Literal, Protocol, cast

from friday_chat.background import BackgroundTaskManager, BackgroundWorkCoordinator
from friday_chat.commands.registry import (
    CommandRegistry,
    RegistryCommandContext,
    build_default_registry,
)
from friday_chat.config import FridayChatConfig
from friday_chat.display import DisplayController, format_assistant_response
from friday_chat.runtime import FridayRuntime, build_runtime
from friday_chat.session import FridaySession
from friday_chat.shell import ShellService
from friday_chat.turns.processor import (
    TurnProcessingError,
    TurnProcessor,
    TurnResult,
    TurnTimeoutError,
)


class InputSource(Protocol):
    """Input boundary for the interactive FridayV2 loop."""

    async def read(self) -> str:
        """Read one user input value."""


class OutputSink(Protocol):
    """Output boundary for assistant responses."""

    async def write(self, text: str) -> None:
        """Write one assistant response."""


class AssistantOutputSink(OutputSink, Protocol):
    """Optional rich assistant response output boundary."""

    async def write_assistant_response(
        self,
        text: str,
        *,
        assistant_name: str,
    ) -> None:
        """Write one formatted assistant response."""

    async def begin_assistant_response(self, *, assistant_name: str) -> None:
        """Begin a streamed assistant response."""

    async def write_assistant_chunk(self, text: str) -> None:
        """Write one formatted streamed assistant response chunk."""


class TurnHandler(Protocol):
    """Minimal turn-processing contract used by the app lifecycle."""

    async def process(self, user_message: str) -> TurnResult:
        """Process one user message."""


class StreamingTurnHandler(TurnHandler, Protocol):
    """Turn handler that can stream no-tool assistant output."""

    async def process_streaming(
        self,
        user_message: str,
        *,
        on_chunk: Callable[[str], Awaitable[None]],
    ) -> TurnResult:
        """Process one user message and emit response chunks."""


class StreamingProcessMethod(Protocol):
    """Callable shape for optional streaming turn processing."""

    async def __call__(
        self,
        user_message: str,
        *,
        on_chunk: Callable[[str], Awaitable[None]],
    ) -> TurnResult:
        """Process one user message and emit response chunks."""


@dataclass(frozen=True)
class AppRunResult:
    """Summary of one FridayV2 app run."""

    exit_reason: Literal["eof", "keyboard_interrupt", "command_exit"]
    turns_processed: int
    maintenance_actions: tuple[str, ...]


@dataclass
class ListInputSource:
    """Deterministic input source used by tests."""

    values: Sequence[str]
    _index: int = 0

    async def read(self) -> str:
        if self._index >= len(self.values):
            raise EOFError
        value = self.values[self._index]
        self._index += 1
        return value


@dataclass
class ListOutputSink:
    """Deterministic output sink used by tests."""

    values: list[str] = field(default_factory=list)

    async def write(self, text: str) -> None:
        self.values.append(text)


class ConsoleInputSource:
    """Console input adapter for manual interactive use."""

    def __init__(self, prompt: str = "> ") -> None:
        self._prompt = prompt

    async def read(self) -> str:
        return input(self._prompt)


class ConsoleOutputSink:
    """Console output adapter for manual interactive use."""

    async def write(self, text: str) -> None:
        print(text)

    async def write_chunk(self, text: str) -> None:
        sys.stdout.write(text)
        sys.stdout.flush()

    async def finish_stream(self) -> None:
        sys.stdout.write("\n")
        sys.stdout.flush()


class FridayChatApp:
    """Top-level FridayV2 application lifecycle."""

    def __init__(
        self,
        *,
        config: FridayChatConfig | None = None,
        runtime: FridayRuntime | None = None,
        input_source: InputSource | None = None,
        output_sink: OutputSink | None = None,
        turn_handler: TurnHandler | None = None,
        background: BackgroundTaskManager | None = None,
        background_work: BackgroundWorkCoordinator | None = None,
        command_registry: CommandRegistry | None = None,
        command_context: RegistryCommandContext | None = None,
        shell_service: ShellService | None = None,
        session: FridaySession | None = None,
        display: DisplayController | None = None,
        version: str = "0.1.0",
    ) -> None:
        if runtime is None:
            if config is None:
                config = FridayChatConfig.model_validate(
                    {"llm": {"model": "fake/test-chat-model"}}
                )
            runtime = build_runtime(config)

        self.runtime = runtime
        self.input_source = input_source or ConsoleInputSource()
        self.output_sink = output_sink or ConsoleOutputSink()
        self.turn_handler = turn_handler or TurnProcessor(
            runtime,
            heartbeat_factory=display,
        )
        self.background = background or BackgroundTaskManager()
        self.background_work = background_work or BackgroundWorkCoordinator(
            runtime=runtime,
            manager=self.background,
        )
        self.command_registry = command_registry or build_default_registry()
        self.command_context = command_context or RegistryCommandContext(
            runtime=runtime,
            registry=self.command_registry,
        )
        self.shell_service = shell_service or ShellService()
        self.display = display
        self.version = version
        self.session = session or FridaySession(
            session_id="friday-v2",
            user_id=runtime.config.chat.user_name,
        )
        self._started = False

    @property
    def started(self) -> bool:
        """Return whether the app has been started."""
        return self._started

    def start(self) -> None:
        """Mark the app as started."""
        self._started = True
        if self.display is not None:
            self.display.render_banner(
                assistant_name=self.runtime.config.chat.assistant_name,
                version=self.version,
            )

    async def run(self) -> AppRunResult:
        """Run the interactive lifecycle until EOF or keyboard interrupt."""
        self.start()
        turns_processed = 0
        exit_reason: Literal["eof", "keyboard_interrupt", "command_exit"] = "eof"
        try:
            while True:
                try:
                    user_message = await self.input_source.read()
                except EOFError:
                    exit_reason = "eof"
                    break
                except KeyboardInterrupt:
                    exit_reason = "keyboard_interrupt"
                    break

                if not user_message.strip():
                    continue

                if user_message.startswith("!"):
                    command = user_message[1:].strip()
                    if command:
                        shell_result = await self.shell_service.execute(command)
                        await self.output_sink.write(shell_result.format())
                    continue

                if user_message.startswith("@"):
                    routed = await self._route_agent_message(user_message)
                    await self.output_sink.write(routed)
                    continue

                was_command, command_result = await self.command_registry.execute(
                    user_message,
                    self.command_context,
                )
                if was_command:
                    if command_result is not None and command_result.output:
                        await self.output_sink.write(command_result.output)
                    if command_result is not None and command_result.exit_requested:
                        exit_reason = "command_exit"
                        break
                    continue

                self._ensure_session_initialized()
                if (
                    self.runtime.compaction_task is not None
                    and not self.runtime.compaction_task.done()
                ):
                    await self.output_sink.write("Optimizing context memory...")
                    await self.background_work.wait_for_inflight_compaction()
                try:
                    result = await self._process_chat_turn(user_message)
                except TurnProcessingError as exc:
                    await self.output_sink.write(
                        _format_turn_processing_error(exc, self.runtime.config)
                    )
                    continue
                self._record_turn_state(user_message, result)
                turns_processed += 1
                self.background_work.schedule_after_turn(
                    turn_count=turns_processed,
                    user_message=user_message,
                    assistant_message=result.assistant_message,
                    budget_status=result.budget_status,
                )
        finally:
            try:
                await self._run_exit_maintenance()
            finally:
                await self.runtime.transcript.finalize()
                await self.background.close()
            self._started = False

        return AppRunResult(
            exit_reason=exit_reason,
            turns_processed=turns_processed,
            maintenance_actions=tuple(self.runtime.maintenance.actions),
        )

    async def _process_chat_turn(self, user_message: str) -> TurnResult:
        streaming_handler = getattr(self.turn_handler, "process_streaming", None)
        if callable(streaming_handler):
            typed_handler = cast(StreamingProcessMethod, streaming_handler)
            await self._begin_assistant_response()
            try:
                result = await typed_handler(
                    user_message,
                    on_chunk=self._write_response_chunk,
                )
            finally:
                await self._finish_response_stream()
            return result
        result = await self.turn_handler.process(user_message)
        await self._write_assistant_response(result.assistant_message)
        return result

    async def _write_assistant_response(self, text: str) -> None:
        write_response = getattr(self.output_sink, "write_assistant_response", None)
        if callable(write_response):
            await write_response(
                text,
                assistant_name=self.runtime.config.chat.assistant_name,
            )
            return
        await self.output_sink.write(
            format_assistant_response(
                text,
                assistant_name=self.runtime.config.chat.assistant_name,
            )
        )

    async def _begin_assistant_response(self) -> None:
        begin_response = getattr(self.output_sink, "begin_assistant_response", None)
        if callable(begin_response):
            await begin_response(assistant_name=self.runtime.config.chat.assistant_name)

    async def _write_response_chunk(self, chunk: str) -> None:
        write_assistant_chunk = getattr(self.output_sink, "write_assistant_chunk", None)
        if callable(write_assistant_chunk):
            await write_assistant_chunk(chunk)
            return
        write_chunk = getattr(self.output_sink, "write_chunk", None)
        if callable(write_chunk):
            await write_chunk(chunk)
            return
        await self.output_sink.write(chunk)

    async def _finish_response_stream(self) -> None:
        finish_stream = getattr(self.output_sink, "finish_stream", None)
        if callable(finish_stream):
            await finish_stream()

    async def _run_exit_maintenance(self) -> None:
        config = self.runtime.config.session
        await self._run_maintenance_step(
            "flush_pending_extraction",
            self.runtime.maintenance.flush_pending_extraction(),
        )
        if config.flush_on_exit:
            await self._run_maintenance_step(
                "flush_memory",
                self.runtime.maintenance.flush_memory(),
            )
        if config.lifecycle_on_exit:
            await self._run_maintenance_step(
                "run_lifecycle",
                self.runtime.maintenance.run_lifecycle(),
            )
        if config.reorganize_on_exit:
            await self._run_maintenance_step(
                f"reorganize_memory:{config.reorganize_mode}",
                self.runtime.maintenance.reorganize_memory(config.reorganize_mode),
            )

    async def _run_maintenance_step(
        self,
        name: str,
        operation: Coroutine[object, object, object],
    ) -> None:
        try:
            await operation
        except Exception as exc:
            self.runtime.diagnostics.maintenance_warnings.append(f"{name}: {exc}")

    async def _route_agent_message(self, user_message: str) -> str:
        route_text = user_message[1:].strip()
        if not route_text:
            return "Usage: @agent_name <message>"
        parts = route_text.split(maxsplit=1)
        agent = parts[0]
        message = parts[1] if len(parts) > 1 else ""
        if not message:
            return "Usage: @agent_name <message>"
        try:
            return await self.runtime.orchestrator.route(agent, message)
        except KeyError as exc:
            return str(exc)

    def _ensure_session_initialized(self) -> None:
        self.session.ensure_initialized(
            {
                "user_name": self.runtime.config.chat.user_name,
                "assistant_name": self.runtime.config.chat.assistant_name,
            }
        )

    def _record_turn_state(self, user_message: str, result: TurnResult) -> None:
        self.session.turn_ids.append(str(len(self.session.turn_ids) + 1))
        self.command_context.history.append((user_message, result.assistant_message))
        self.command_context.last_context = result.context
        self.command_context.last_prompt = result.prompt
        self.command_context.last_debug = {
            "retrieved_memory_count": str(result.retrieved_memory_count),
            "tool_context_injected": str(result.tool_context_injected),
            "context_budget_tokens": str(result.context_budget_tokens),
            "tool_schema_tokens": str(result.tool_schema_tokens),
        }
        self.command_context.last_timing = (
            result.metrics.as_dict() if result.metrics is not None else {}
        )


def _format_turn_processing_error(
    exc: TurnProcessingError,
    config: FridayChatConfig,
) -> str:
    """Return a concise CLI message for recoverable turn failures."""
    if isinstance(exc, TurnTimeoutError):
        timeout = exc.timeout_seconds or config.llm.timeout_seconds
        suffix = f" after {timeout:g}s" if timeout is not None else ""
        return (
            f"LLM turn timed out{suffix}. Tool calls may have completed, "
            "but the follow-up model response exceeded llm.timeout_seconds. "
            "Consider increasing llm.timeout_seconds or reducing tool result size."
        )
    message = str(exc) or exc.__class__.__name__
    return f"Turn failed: {message}"


__all__ = [
    "AppRunResult",
    "ConsoleInputSource",
    "ConsoleOutputSink",
    "FridayChatApp",
    "InputSource",
    "ListInputSource",
    "ListOutputSink",
    "OutputSink",
    "TurnHandler",
]

"""Application lifecycle for FridayV2."""

from __future__ import annotations

import sys
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from typing import Literal, Protocol, cast

from friday_chat.background import BackgroundTaskManager, BackgroundWorkCoordinator
from friday_chat.commands.registry import (
    CommandRegistry,
    CommandResult,
    CommandUiEffect,
    RegistryCommandContext,
    build_default_registry,
)
from friday_chat.config import FridayChatConfig
from friday_chat.display import DisplayController, format_assistant_response
from friday_chat.input_sources import AsyncPromptCallable, AsyncPromptReader
from friday_chat.reorganization.assembly import (
    ExitReorganizationModeError,
    build_exit_reorganization_request,
)
from friday_chat.reorganization.coordinator import (
    MaintenanceRuntimeHooks,
    ManualMaintenanceDrainResult,
    ManualMaintenanceResumeResult,
    ReorganizationCoordinator,
)
from friday_chat.reorganization.gate import MaintenanceAdmissionGate
from friday_chat.runtime import FridayRuntime, build_runtime
from friday_chat.session import FridaySession, SessionIdentityMismatchError
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

    def __init__(
        self,
        prompt: str = "> ",
        *,
        prompt_fn: AsyncPromptCallable | None = None,
    ) -> None:
        self._prompt = prompt
        self._reader = AsyncPromptReader(prompt_fn)

    async def read(self) -> str:
        return await self._reader.read(self._prompt)


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


@dataclass
class AppMaintenanceRuntimeHooks(MaintenanceRuntimeHooks):
    """Direct app hooks for exclusive-intent preparation and maintenance."""

    runtime: FridayRuntime
    background: BackgroundTaskManager
    background_work: BackgroundWorkCoordinator | None = None
    _extraction_preempted: bool = field(default=False, init=False, repr=False)

    async def prepare_for_manual_maintenance(self) -> None:
        """Cancel supervised writers after exclusive intent blocks new work."""
        self._extraction_preempted = bool(
            self.background_work is not None
            and self.background_work.extraction_running
        )
        await self.background.cancel_pending()

    async def drain_for_manual_maintenance(self) -> ManualMaintenanceDrainResult:
        """Flush committed stores while retaining extraction as future work."""
        buffered_extraction_count = len(
            self.runtime.maintenance.pending_extraction
        )
        succeeded = await self._run_step(
            "flush_memory",
            self.runtime.maintenance.flush_memory(),
        )
        if not succeeded:
            raise RuntimeError("manual maintenance drain failed")
        return ManualMaintenanceDrainResult(
            buffered_extraction_count=buffered_extraction_count,
            extraction_preempted=self._extraction_preempted,
        )

    def resume_after_manual_maintenance(self) -> ManualMaintenanceResumeResult:
        """Restart only extraction that this maintenance operation preempted."""
        required = self._extraction_preempted
        self._extraction_preempted = False
        pending_count = len(self.runtime.maintenance.pending_extraction)
        scheduled = False
        if required and pending_count and self.background_work is not None:
            scheduled = self.background_work.resume_preempted_extraction(
                trigger_reason="maintenance_resume"
            )
        return ManualMaintenanceResumeResult(
            required=required,
            scheduled=scheduled,
            pending_count=pending_count,
        )

    async def close_for_shutdown(self, *, snapshot_requested: bool) -> None:
        await self.background.close()
        failures = 0
        failures += not await self._run_step(
            "flush_pending_extraction",
            self.runtime.maintenance.flush_pending_extraction(),
        )
        if self.runtime.config.session.flush_on_exit or snapshot_requested:
            failures += not await self._run_step(
                "flush_memory",
                self.runtime.maintenance.flush_memory(),
            )
        if self.runtime.config.session.lifecycle_on_exit:
            failures += not await self._run_step(
                "run_lifecycle",
                self.runtime.maintenance.run_lifecycle(),
            )
        if snapshot_requested and failures:
            raise RuntimeError("shutdown maintenance drain failed")

    async def close_async_clients(self, *, snapshot_requested: bool) -> None:
        """Close process clients after coordinator-owned shutdown work ends."""
        succeeded = await self._run_step(
            "close_async_clients",
            self.runtime.async_clients.close(),
        )
        if snapshot_requested and not succeeded:
            raise RuntimeError("shutdown client cleanup failed")

    async def finalize_transcript(self) -> None:
        await self.runtime.transcript.finalize()

    async def _run_step(
        self,
        name: str,
        operation: Awaitable[object],
    ) -> bool:
        try:
            await operation
        except Exception as exc:
            self.runtime.diagnostics.maintenance_warnings.append(
                f"{name}: {type(exc).__name__}"
            )
            return False
        return True


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
        maintenance_gate: MaintenanceAdmissionGate | None = None,
        reorganization_coordinator: ReorganizationCoordinator | None = None,
        command_registry: CommandRegistry | None = None,
        command_context: RegistryCommandContext | None = None,
        shell_service: ShellService | None = None,
        session: FridaySession | None = None,
        display: DisplayController | None = None,
        version: str = "0.1.0a2",
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
        if reorganization_coordinator is not None:
            if (
                maintenance_gate is not None
                and maintenance_gate is not reorganization_coordinator.gate
            ):
                raise ValueError("app maintenance gate does not match coordinator")
            maintenance_gate = reorganization_coordinator.gate
        self.maintenance_gate = maintenance_gate or MaintenanceAdmissionGate()
        self.background_work = background_work or BackgroundWorkCoordinator(
            runtime=runtime,
            manager=self.background,
            gate=self.maintenance_gate,
        )
        if self.background_work.gate is not self.maintenance_gate:
            raise ValueError("background work must use the app maintenance gate")
        self.maintenance_hooks = AppMaintenanceRuntimeHooks(
            runtime=runtime,
            background=self.background,
            background_work=self.background_work,
        )
        self.reorganization_coordinator = (
            reorganization_coordinator
            or ReorganizationCoordinator(
                layout=runtime.maintenance_layout,
                gate=self.maintenance_gate,
                memory_participant=runtime.memory_recovery,
                transcript_participant=runtime.transcript_recovery,
                runtime_hooks=self.maintenance_hooks,
                mutation_adapter=runtime.reorganization_mutation,
                application_version=version,
            )
        )
        self.command_registry = command_registry or build_default_registry()
        self.command_context = command_context or RegistryCommandContext(
            runtime=runtime,
            registry=self.command_registry,
            maintenance_gate=self.maintenance_gate,
            reorganization_coordinator=self.reorganization_coordinator,
        )
        if self.command_context.maintenance_gate is None:
            self.command_context.maintenance_gate = self.maintenance_gate
        if self.command_context.reorganization_coordinator is None:
            self.command_context.reorganization_coordinator = (
                self.reorganization_coordinator
            )
        if (
            self.command_context.maintenance_gate is not self.maintenance_gate
            or self.command_context.reorganization_coordinator
            is not self.reorganization_coordinator
        ):
            raise ValueError("command context must use the app maintenance boundary")
        self.shell_service = shell_service or ShellService()
        self.display = display
        self.version = version
        if session is None:
            session = FridaySession(
                session_id=runtime.session_identity.value,
                user_id=runtime.config.chat.user_name,
                identity=runtime.session_identity,
            )
        elif session.session_id != runtime.session_identity.value:
            raise SessionIdentityMismatchError(
                "app session identity does not match runtime session identity"
            )
        else:
            session.identity = runtime.session_identity
        self.session = session
        self.command_context.session = self.session
        self._started = False

    @property
    def started(self) -> bool:
        """Return whether the app has been started."""
        return self._started

    def start(self) -> None:
        """Mark the app as started."""
        self._started = True
        if self.reorganization_coordinator.recovery_inspection_configured:
            try:
                warnings = self.reorganization_coordinator.startup_recovery_warnings()
            except Exception as exc:
                warnings = (
                    f"reorganization startup inspection failed: {type(exc).__name__}",
                )
            self.runtime.diagnostics.maintenance_warnings.extend(warnings)
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

                self.command_context.command_progress = self.output_sink.write
                try:
                    was_command, command_result = await self.command_registry.execute(
                        user_message,
                        self.command_context,
                    )
                finally:
                    self.command_context.command_progress = None
                if was_command:
                    effect_error = self._dispatch_command_effects(command_result)
                    if effect_error is not None:
                        await self.output_sink.write(effect_error)
                    if command_result is not None and command_result.output:
                        await self.output_sink.write(command_result.output)
                    if command_result is not None and command_result.exit_requested:
                        exit_reason = "command_exit"
                        break
                    continue

                extraction_preempted = (
                    await self.background_work.preempt_extraction_for_foreground_turn()
                )
                try:
                    async with self.maintenance_gate.shared("chat-turn"):
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
                    if extraction_preempted:
                        self.background_work.resume_preempted_extraction()
        finally:
            await self._shutdown_through_coordinator()
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

    async def _shutdown_through_coordinator(self) -> None:
        request = None
        skipped_action: str | None = None
        try:
            request = build_exit_reorganization_request(self.runtime.config)
        except ExitReorganizationModeError as exc:
            skipped_action = "reorganize_skipped:invalid_exit_mode"
            self.runtime.diagnostics.maintenance_warnings.append(str(exc))
        capability = self.reorganization_coordinator.execution_capability
        if request is not None and not capability.available_for(request):
            skipped_action = "reorganize_skipped:execute_disabled"
            self.runtime.diagnostics.maintenance_warnings.append(
                "reorganize_memory:"
                f"{self.runtime.config.session.reorganize_mode}: execute disabled: "
                f"{capability.reason_for(request)}"
            )
            request = None
        snapshot_requested = request is not None and request.execute
        try:
            await self.reorganization_coordinator.shutdown(request)
        except Exception as exc:
            self.runtime.diagnostics.maintenance_warnings.append(
                f"shutdown coordinator: {type(exc).__name__}"
            )
        finally:
            if skipped_action is not None:
                self.runtime.maintenance.actions.append(skipped_action)
            try:
                await self.maintenance_hooks.close_async_clients(
                    snapshot_requested=snapshot_requested
                )
            except Exception as exc:
                self.runtime.diagnostics.maintenance_warnings.append(
                    f"shutdown coordinator: {type(exc).__name__}"
                )

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

    def _dispatch_command_effects(
        self,
        command_result: CommandResult | None,
    ) -> str | None:
        if command_result is None:
            return None
        for effect in command_result.ui_effects:
            if effect is CommandUiEffect.CLEAR_SCREEN:
                if self.display is None:
                    return "Unable to clear the terminal: display is unavailable."
                try:
                    self.display.clear_screen()
                except Exception:
                    return "Unable to clear the terminal."
        return None

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
        self.command_context.last_budget_status = result.budget_status
        self.command_context.last_tool_budget_snapshot = result.tool_budget_snapshot
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
    cause = _format_exception_cause(exc)
    if cause:
        return f"Turn failed: {message} Last error: {cause}"
    return f"Turn failed: {message}"


def _format_exception_cause(exc: BaseException) -> str | None:
    cause = _root_exception_cause(exc)
    if cause is None:
        return None
    message = " ".join(str(cause).split())
    response_body = _exception_response_body(cause)
    if response_body:
        message = f"{message} Response body: {response_body}"
    if len(message) > 500:
        message = f"{message[:497]}..."
    return f"{cause.__class__.__name__}: {message}"


def _root_exception_cause(exc: BaseException) -> BaseException | None:
    current = exc.__cause__ or exc.__context__
    seen: set[int] = {id(exc)}
    root: BaseException | None = current
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        root = current
        nested = getattr(current, "last_error", None)
        if isinstance(nested, BaseException):
            current = nested
            continue
        current = current.__cause__ or current.__context__
    return root


def _exception_response_body(exc: BaseException) -> str | None:
    response = getattr(exc, "response", None)
    if response is None:
        return None
    text = getattr(response, "text", None)
    if not isinstance(text, str) or not text.strip():
        return None
    return " ".join(text.split())


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

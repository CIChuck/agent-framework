"""Replay support for FridayV2."""

from __future__ import annotations

import asyncio
import csv
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path

from friday_chat.runtime import FridayRuntime
from friday_chat.session import SessionIdentity, SessionIdentityMismatchError
from friday_chat.turns.processor import TurnProcessor

SleepFn = Callable[[float], Awaitable[None]]


@dataclass(frozen=True)
class ReplayTurn:
    """One loaded replay turn."""

    turn_number: int
    user_message: str
    assistant_message: str


@dataclass
class ReplayResult:
    """Replay execution result."""

    processed_turns: int
    loaded_turns: list[ReplayTurn] = field(default_factory=list)
    reset_output: str = ""


class ReplayService:
    """Replay exported transcript CSV files through the normal turn processor."""

    def __init__(
        self,
        runtime: FridayRuntime | None = None,
        *,
        session_identity: SessionIdentity | None = None,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        if runtime is None:
            from friday_chat.config import FridayChatConfig
            from friday_chat.runtime import build_runtime

            runtime = build_runtime(
                FridayChatConfig.model_validate(
                    {"llm": {"model": "fake/test-chat-model"}}
                ),
                session_identity=session_identity,
            )
        elif (
            session_identity is not None
            and runtime.session_identity != session_identity
        ):
            raise SessionIdentityMismatchError(
                "replay session identity does not match injected runtime"
            )
        self.runtime = runtime
        self.sleep = sleep
        self.processed_messages: list[str] = []

    async def replay_csv(
        self,
        path: str | Path,
        *,
        delay_seconds: float = 0.0,
    ) -> ReplayResult:
        """Replay a Friday transcript CSV."""
        turns = load_replay_csv(path)
        if not turns:
            return ReplayResult(processed_turns=0, loaded_turns=[])

        from friday_chat.commands.registry import (
            RegistryCommandContext,
            build_default_registry,
        )

        registry = build_default_registry()
        context = RegistryCommandContext(runtime=self.runtime, registry=registry)
        _, reset_result = await registry.execute("/reset", context)
        reset_output = reset_result.output if reset_result is not None else ""

        processor = TurnProcessor(self.runtime)
        for index, turn in enumerate(turns):
            await processor.process(turn.user_message)
            self.processed_messages.append(turn.user_message)
            if delay_seconds > 0 and index < len(turns) - 1:
                await self.sleep(delay_seconds)

        return ReplayResult(
            processed_turns=len(turns),
            loaded_turns=turns,
            reset_output=reset_output,
        )


def load_replay_csv(path: str | Path) -> list[ReplayTurn]:
    """Load replay turns from a transcript CSV."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Replay CSV not found: {csv_path}")
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    turns = [
        ReplayTurn(
            turn_number=int(row["turn_number"]),
            user_message=row["user_message"],
            assistant_message=row.get("assistant_message", ""),
        )
        for row in rows
        if row.get("user_message", "").strip()
    ]
    return sorted(turns, key=lambda turn: turn.turn_number)


def parse_replay_delay(value: str | float | None) -> float:
    """Parse a replay delay value."""
    if value is None:
        return 0.0
    try:
        delay = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Replay delay must be numeric.") from exc
    if delay < 0:
        raise ValueError("Replay delay must be non-negative.")
    return delay

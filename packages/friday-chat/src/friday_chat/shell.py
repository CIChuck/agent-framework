"""Optional shell execution service for FridayV2."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ShellResult:
    """Result of one shell command execution."""

    command: str
    cwd: Path
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool = False

    def format(self) -> str:
        """Format a shell result for chat output."""
        if self.timed_out:
            return f"Shell command timed out: {self.command}"
        return "\n".join(
            [
                f"Command: {self.command}",
                f"cwd: {self.cwd}",
                f"exit_code: {self.returncode}",
                "stdout:",
                self.stdout.rstrip(),
                "stderr:",
                self.stderr.rstrip(),
            ]
        ).rstrip()


class ShellService:
    """Explicitly opt-in shell execution boundary."""

    def __init__(
        self,
        *,
        enabled: bool = False,
        cwd: str | Path | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        self.enabled = enabled
        self.cwd = Path(cwd or ".").resolve()
        self.timeout_seconds = timeout_seconds

    async def execute(self, command: str) -> ShellResult:
        """Execute a shell command when explicitly enabled."""
        if not self.enabled:
            return ShellResult(
                command=command,
                cwd=self.cwd,
                returncode=None,
                stdout="",
                stderr="Shell execution is disabled.",
            )
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=self.cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout_seconds,
            )
        except TimeoutError:
            process.kill()
            await process.communicate()
            return ShellResult(
                command=command,
                cwd=self.cwd,
                returncode=None,
                stdout="",
                stderr="",
                timed_out=True,
            )
        return ShellResult(
            command=command,
            cwd=self.cwd,
            returncode=process.returncode,
            stdout=stdout.decode(errors="replace"),
            stderr=stderr.decode(errors="replace"),
        )

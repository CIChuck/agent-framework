"""
System information tools.

Ref: docs/specs/tool_specification.md - Category 4: System Tools
"""

from __future__ import annotations

import os
import platform
import subprocess
from typing import Any

from ..definition import BaseTool


class ProcessListTool(BaseTool):
    """List running processes."""

    @property
    def name(self) -> str:
        return "process_list"

    @property
    def description(self) -> str:
        return "List running processes with their PID, name, and resource usage."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "description": "Filter processes by name (substring match)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of processes to return",
                    "default": 50,
                },
                "sort_by": {
                    "type": "string",
                    "description": "Sort by: cpu, memory, pid, name",
                    "enum": ["cpu", "memory", "pid", "name"],
                    "default": "cpu",
                },
            },
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        name_filter = kwargs.get("filter", "")
        limit = kwargs.get("limit", 50)
        sort_by = kwargs.get("sort_by", "cpu")

        try:
            # Use ps command for cross-platform compatibility
            if platform.system() == "Windows":
                return "Error: Process listing not supported on Windows"

            # Get process list with ps
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return f"Error: Failed to list processes: {result.stderr}"

            lines = result.stdout.strip().split("\n")
            if len(lines) < 2:
                return "No processes found"

            # Parse header and data
            lines[0]
            processes = []

            for line in lines[1:]:
                parts = line.split(None, 10)
                if len(parts) < 11:
                    continue

                proc = {
                    "user": parts[0],
                    "pid": int(parts[1]),
                    "cpu": float(parts[2]),
                    "memory": float(parts[3]),
                    "command": parts[10],
                }

                # Apply filter
                if name_filter and name_filter.lower() not in proc["command"].lower():
                    continue

                processes.append(proc)

            # Sort
            if sort_by == "cpu":
                processes.sort(key=lambda x: x["cpu"], reverse=True)
            elif sort_by == "memory":
                processes.sort(key=lambda x: x["memory"], reverse=True)
            elif sort_by == "pid":
                processes.sort(key=lambda x: x["pid"])
            elif sort_by == "name":
                processes.sort(key=lambda x: x["command"].lower())

            # Limit results
            processes = processes[:limit]

            # Format output
            output_lines = ["PID      CPU%   MEM%   COMMAND"]
            output_lines.append("-" * 60)
            for p in processes:
                cmd = (
                    p["command"][:40] + "..."
                    if len(p["command"]) > 40
                    else p["command"]
                )
                output_lines.append(
                    f"{p['pid']:<8} {p['cpu']:>5.1f}  {p['memory']:>5.1f}  {cmd}"
                )

            return "\n".join(output_lines)

        except subprocess.TimeoutExpired:
            return "Error: Process listing timed out"
        except Exception as e:
            return f"Error: Failed to list processes: {e}"


class ProcessKillTool(BaseTool):
    """Terminate a process."""

    @property
    def name(self) -> str:
        return "process_kill"

    @property
    def description(self) -> str:
        return "Terminate a process by PID. Use with caution."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pid": {
                    "type": "integer",
                    "description": "Process ID to terminate",
                },
                "signal": {
                    "type": "string",
                    "description": "Signal to send (TERM, KILL, HUP)",
                    "default": "TERM",
                    "enum": ["TERM", "KILL", "HUP", "INT"],
                },
            },
            "required": ["pid"],
        }

    async def execute(self, **kwargs: Any) -> str:
        pid = kwargs["pid"]
        signal = kwargs.get("signal", "TERM")

        # Security: Don't allow killing system processes
        if pid <= 1:
            return "Error: Cannot terminate system processes (PID <= 1)"

        try:
            import signal as sig

            signal_map = {
                "TERM": sig.SIGTERM,
                "KILL": sig.SIGKILL,
                "HUP": sig.SIGHUP,
                "INT": sig.SIGINT,
            }

            os.kill(pid, signal_map.get(signal, sig.SIGTERM))
            return f"Sent {signal} signal to process {pid}"

        except ProcessLookupError:
            return f"Error: Process {pid} not found"
        except PermissionError:
            return f"Error: Permission denied to terminate process {pid}"
        except Exception as e:
            return f"Error: Failed to terminate process: {e}"


class EnvironmentGetTool(BaseTool):
    """Get environment variables."""

    @property
    def name(self) -> str:
        return "environment_get"

    @property
    def description(self) -> str:
        return "Get the value of an environment variable."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the environment variable",
                },
                "default": {
                    "type": "string",
                    "description": "Default value if not set",
                },
            },
            "required": ["name"],
        }

    async def execute(self, **kwargs: Any) -> str:
        name = kwargs["name"]
        default = kwargs.get("default")

        # Security: Block access to sensitive env vars
        sensitive = {"AWS_SECRET", "PASSWORD", "SECRET", "TOKEN", "KEY", "CREDENTIAL"}
        name_upper = name.upper()
        for s in sensitive:
            if s in name_upper:
                return f"Error: Access to sensitive environment variable denied: {name}"

        value = os.environ.get(name, default)
        if value is None:
            return f"Environment variable '{name}' is not set"

        return value


class SystemInfoTool(BaseTool):
    """Get system information."""

    @property
    def name(self) -> str:
        return "system_info"

    @property
    def description(self) -> str:
        return "Get system information including OS, CPU, memory, and disk usage."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        try:
            info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "os_release": platform.release(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "hostname": platform.node(),
            }

            # Try to get memory info (Unix)
            try:
                with open("/proc/meminfo") as f:
                    meminfo = f.read()
                    for line in meminfo.split("\n"):
                        if line.startswith("MemTotal:"):
                            total = int(line.split()[1]) / 1024 / 1024
                            info["memory_total_gb"] = f"{total:.1f}"
                        elif line.startswith("MemAvailable:"):
                            avail = int(line.split()[1]) / 1024 / 1024
                            info["memory_available_gb"] = f"{avail:.1f}"
            except Exception:
                pass

            # Try to get disk info
            try:
                stat = os.statvfs("/")
                total = stat.f_blocks * stat.f_frsize / 1024 / 1024 / 1024
                free = stat.f_bavail * stat.f_frsize / 1024 / 1024 / 1024
                info["disk_total_gb"] = f"{total:.1f}"
                info["disk_free_gb"] = f"{free:.1f}"
            except Exception:
                pass

            # Format output
            lines = []
            for key, value in info.items():
                label = key.replace("_", " ").title()
                lines.append(f"{label}: {value}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error: Failed to get system info: {e}"


# Convenience instances
process_list = ProcessListTool()
process_kill = ProcessKillTool()
environment_get = EnvironmentGetTool()
system_info = SystemInfoTool()

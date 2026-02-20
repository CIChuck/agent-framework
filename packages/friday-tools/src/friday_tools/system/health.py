from __future__ import annotations

import psutil
from pydantic import BaseModel, Field

from friday_tools.base import FridayTool, ToolResult


class SystemHealthTool(FridayTool):
    """
    Check system health metrics (CPU, RAM, Disk).
    Useful for Sentinel agents to monitor host stability.
    """

    name = "system_health"
    description = "Get current system resource usage (CPU, Memory, Disk)."

    class Input(BaseModel):
        check_disk: bool = Field(
            False, description="Whether to include disk usage (can be slow)."
        )

    async def run(self, args: Input) -> ToolResult:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Memory
        mem = psutil.virtual_memory()
        mem_info = {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "percent": mem.percent,
        }

        # Disk
        disk_info = {}
        if args.check_disk:
            disk = psutil.disk_usage("/")
            disk_info = {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent,
            }

        content = (
            f"CPU Usage: {cpu_percent}%\n"
            f"Memory: {mem_info['percent']}% ({mem_info['available_gb']}GB free)\n"
        )
        if disk_info:
            content += f"Disk: {disk_info['percent']}% ({disk_info['free_gb']}GB free)"

        return ToolResult(
            content=content,
            data={
                "cpu": {"percent": cpu_percent},
                "memory": mem_info,
                "disk": disk_info,
            },
        )

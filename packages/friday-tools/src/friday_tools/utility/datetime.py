# mypy: ignore-errors
"""
Date and time utility tools.

Provides tools for getting current date/time in various formats and timezones.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

from friday_tools.base import FridayTool, ToolResult

# Try to import zoneinfo (Python 3.9+)
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for older Python versions
    ZoneInfo = None  # type: ignore


def _get_local_timezone() -> str:
    """Get the system's local timezone name."""
    try:
        # Try to get IANA timezone name from system
        if hasattr(time, "tzname") and time.tzname[0]:
            # This gives abbreviated names like 'EST', need to map to IANA
            # For now, try to detect from the offset
            pass
        # Use datetime to get local timezone info
        local_tz = datetime.now().astimezone().tzinfo
        if local_tz and hasattr(local_tz, "key"):
            return local_tz.key  # type: ignore
        # Fallback: return "local" which we'll handle specially
        return "local"
    except Exception:
        return "UTC"


class GetCurrentDateTimeTool(FridayTool):
    """
    Get the current date and time, optionally in a specific timezone.

    Useful for agents that need to know the current time, schedule events,
    or work with time-sensitive data.
    """

    name = "get_current_datetime"
    description = (
        "Get the current date and time, optionally in a specific timezone and format."
    )
    category = "utility"
    tags = ["datetime", "time", "timezone", "utility"]

    class Input(BaseModel):
        timezone_name: str = Field(
            default="local",
            description="IANA timezone name (e.g., 'America/New_York', 'UTC', 'Europe/London', 'Asia/Tokyo'). Use 'local' for system timezone.",  # noqa: E501
        )
        format: Literal["iso", "human", "unix"] = Field(
            default="iso",
            description="Output format: 'iso' for ISO 8601, 'human' for human-readable, 'unix' for Unix timestamp",  # noqa: E501
        )

    async def run(self, args: Input) -> ToolResult:
        """Execute the datetime tool."""
        try:
            # Resolve timezone name for display
            tz_display = args.timezone_name

            # Handle timezone
            if args.timezone_name == "local":
                # Use system local timezone
                now = datetime.now().astimezone()
                tz_display = _get_local_timezone()
                if tz_display == "local":
                    # Couldn't determine IANA name, use offset
                    tz_display = now.strftime("UTC%z")
            elif args.timezone_name == "UTC":
                now = datetime.now(UTC)
            elif ZoneInfo is not None:
                try:
                    tz = ZoneInfo(args.timezone_name)
                    now = datetime.now(tz)
                except Exception:
                    return ToolResult(
                        content=f"Unknown timezone: {args.timezone_name}",
                        error=f"Invalid timezone: {args.timezone_name}",
                    )
            else:
                # No zoneinfo support, only UTC works
                if args.timezone_name != "UTC":
                    return ToolResult(
                        content="Only UTC timezone supported (zoneinfo unavailable)",
                        error="zoneinfo module not available",
                    )
                now = datetime.now(UTC)

            # Build result data
            result_data = {
                "timezone": tz_display,
                "utc_offset": now.strftime("%z"),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "day_of_week": now.strftime("%A"),
            }

            # Format based on requested output type
            if args.format == "iso":
                formatted = now.isoformat()
                result_data["datetime"] = formatted
            elif args.format == "human":
                formatted = now.strftime("%A, %B %d, %Y at %I:%M:%S %p %Z")
                result_data["datetime"] = formatted
            elif args.format == "unix":
                formatted = str(int(now.timestamp()))
                result_data["datetime"] = int(now.timestamp())
            else:
                formatted = now.isoformat()
                result_data["datetime"] = formatted

            # Build human-readable content
            content = (
                f"Current time ({tz_display}): {formatted}\n"
                f"Date: {result_data['date']}\n"
                f"Time: {result_data['time']}\n"
                f"Day: {result_data['day_of_week']}"
            )

            return ToolResult(
                content=content,
                data=result_data,
                metadata={"format": args.format, "timezone": tz_display},
            )

        except Exception as e:
            return ToolResult(
                content=f"Error getting current datetime: {e}",
                error=str(e),
            )

# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Register a Moltbook agent and print the response."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from friday_moltbook import Moltbook, MoltbookConfig
from friday_moltbook.errors import MoltbookError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Register a Moltbook agent.")
    parser.add_argument("--name", required=True, help="Agent name")
    parser.add_argument("--description", required=True, help="Agent description")
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override Moltbook base URL (default: https://www.moltbook.com/api/v1)",
    )
    return parser


async def _run() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    config_kwargs = {}
    if args.base_url:
        config_kwargs["base_url"] = args.base_url
    config = MoltbookConfig(**config_kwargs) if config_kwargs else MoltbookConfig()
    client = Moltbook(config)

    try:
        response = await client.register_agent(
            name=args.name,
            description=args.description,
        )
    except MoltbookError as exc:
        print(f"Registration failed: {exc}", file=sys.stderr)
        return 1

    payload = {
        "success": response.success,
        "data": response.data,
        "error": response.error,
        "hint": response.hint,
        "raw": response.raw,
        "status_code": response.status_code,
    }
    print(json.dumps(payload, indent=2, default=str))
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_run()))


if __name__ == "__main__":
    main()

"""Create a Moltbook post and print the response."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

from friday_moltbook import Moltbook, MoltbookConfig
from friday_moltbook.errors import MoltbookError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a Moltbook post.")
    parser.add_argument("--submolt", required=True, help="Submolt name")
    parser.add_argument("--title", required=True, help="Post title")
    parser.add_argument("--content", help="Post content (text post)")
    parser.add_argument("--url", help="Link URL (link post)")
    parser.add_argument(
        "--api-key",
        default=None,
        help="Moltbook API key (default: MOLTBOOK_API_KEY)",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override Moltbook base URL (default: https://www.moltbook.com/api/v1)",
    )
    return parser


async def _run() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if bool(args.content) == bool(args.url):
        print("Provide exactly one of --content or --url.", file=sys.stderr)
        return 1

    api_key = args.api_key or os.getenv("MOLTBOOK_API_KEY")
    if not api_key:
        print(
            "Missing API key. Provide --api-key or set MOLTBOOK_API_KEY.",
            file=sys.stderr,
        )
        return 1

    config_kwargs = {"api_key": api_key}
    if args.base_url:
        config_kwargs["base_url"] = args.base_url
    config = MoltbookConfig(**config_kwargs)
    client = Moltbook(config)

    try:
        if args.content:
            response = await client.create_post(
                submolt=args.submolt,
                title=args.title,
                content=args.content,
            )
        else:
            response = await client.create_link_post(
                submolt=args.submolt,
                title=args.title,
                url=args.url,
            )
    except MoltbookError as exc:
        print(f"Post failed: {exc}", file=sys.stderr)
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

"""Command-line entrypoint for the agent quality experiment."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections.abc import Sequence
from pathlib import Path


def _ensure_repo_root_on_syspath() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def build_parser() -> argparse.ArgumentParser:
    _ensure_repo_root_on_syspath()
    from experiments.agent_quality.fake_llm import DEFAULT_PROMPT
    from experiments.agent_quality.runtime import DEFAULT_AGENT_NAME

    parser = argparse.ArgumentParser(description="Run the Friday agent quality experiment.")
    parser.add_argument("--agent", default=DEFAULT_AGENT_NAME, help="Agent profile name to run.")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Prompt to send to the experiment agent.")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit structured JSON output.",
    )
    parser.add_argument(
        "--debug-telemetry",
        action="store_true",
        help="Enable debug telemetry during the experiment run.",
    )
    return parser


def _format_human_output(result: dict[str, object]) -> str:
    lines = [
        f"success: {result['success']}",
        f"agent: {result['agent_name']}",
        f"session_id: {result['session_id']}",
        f"llm_mode: {result['llm_mode']}",
        f"telemetry_enabled: {result['telemetry_enabled']}",
        f"prompt: {result['prompt']}",
    ]
    if result.get("response"):
        lines.append(f"response: {result['response']}")
    if result.get("error"):
        lines.append(f"error: {result['error']}")
    return "\n".join(lines)


async def _run(args: argparse.Namespace) -> int:
    _ensure_repo_root_on_syspath()
    from experiments.agent_quality.runtime import run_agent_quality_experiment

    result = await run_agent_quality_experiment(
        prompt=args.prompt,
        agent_name=args.agent,
        debug_telemetry=args.debug_telemetry,
    )
    payload = result.to_dict()
    if args.json_output:
        print(json.dumps(payload, indent=2))
    else:
        print(_format_human_output(payload))
    return 0 if result.success else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return asyncio.run(_run(args))


if __name__ == "__main__":
    raise SystemExit(main())

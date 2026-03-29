"""Command-line entrypoint for the provider memory smoke experiment."""

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
    parser = argparse.ArgumentParser(
        description="Run the Friday provider-backed memory smoke experiment."
    )
    parser.add_argument(
        "--agent",
        default=None,
        help="Agent profile name to run. Defaults to scenario.agent_name from scenario config.",
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Prompt to send to the experiment agent. Defaults to scenario.prompt from scenario config.",
    )
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
    parser.add_argument(
        "--no-preserve-artifacts",
        action="store_true",
        help="Do not persist the experiment result summary under artifacts/.",
    )
    return parser


def _format_human_output(result: dict[str, object]) -> str:
    lines = [
        f"success: {result['success']}",
        f"agent: {result['agent_name']}",
        f"session_id: {result['session_id']}",
        f"agent_role: {result['agent_role']}",
        f"agent_goal: {result['agent_goal']}",
        f"agent_context_strategy: {result['agent_context_strategy']}",
        f"agent_llm_service: {result['agent_llm_service']}",
        f"inference_llm_service: {result['inference_llm_service']}",
        f"extraction_llm_service: {result['extraction_llm_service']}",
        f"embedding_service: {result['embedding_service']}",
        f"extraction_enabled: {result['extraction_enabled']}",
        f"extracted_entities_count: {result['extracted_entities_count']}",
        f"extracted_relationships_count: {result['extracted_relationships_count']}",
        f"extracted_insights_count: {result['extracted_insights_count']}",
        f"extracted_summaries_count: {result['extracted_summaries_count']}",
        f"prompt: {result['prompt']}",
    ]
    if result.get("runtime_base_system_prompt"):
        lines.append(
            f"runtime_base_system_prompt: {result['runtime_base_system_prompt']}"
        )
    if result.get("rendered_system_prompt"):
        lines.append(f"rendered_system_prompt: {result['rendered_system_prompt']}")
    if result.get("composed_system_prompt"):
        lines.append(f"composed_system_prompt: {result['composed_system_prompt']}")
    if result.get("response"):
        lines.append(f"response: {result['response']}")
    if result.get("artifact_result_path"):
        lines.append(f"artifact_result_path: {result['artifact_result_path']}")
    if result.get("error"):
        lines.append(f"error: {result['error']}")
    return "\n".join(lines)


async def _run(args: argparse.Namespace) -> int:
    _ensure_repo_root_on_syspath()
    from experiments.provider_memory_smoke.runtime import (
        run_provider_memory_smoke_experiment,
    )

    result = await run_provider_memory_smoke_experiment(
        prompt=args.prompt,
        agent_name=args.agent,
        debug_telemetry=args.debug_telemetry,
        preserve_artifacts=not args.no_preserve_artifacts,
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

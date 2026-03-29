"""Command-line entrypoint for the workflow artifact smoke experiment."""

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
        description="Run the live Friday canonical workflow artifact smoke experiment."
    )
    parser.add_argument(
        "--workflow",
        default=None,
        help="Workflow name to execute. Defaults to scenario.workflow_name.",
    )
    parser.add_argument(
        "--query",
        default=None,
        help="Topic/query for the researcher agent. Defaults to scenario.query.",
    )
    parser.add_argument(
        "--output-filename",
        default=None,
        help="Output markdown filename under outputs/. Defaults to scenario.output_filename.",
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
        f"workflow: {result['workflow_name']}",
        f"execution_id: {result['execution_id']}",
        f"session_id: {result['session_id']}",
        f"query: {result['query']}",
        f"selected_article_title: {result['selected_article_title']}",
        f"selected_article_url: {result['selected_article_url']}",
        f"selected_article_source: {result['selected_article_source']}",
        f"selected_article_valid_json: {result['selected_article_valid_json']}",
        f"output_path: {result['output_path']}",
        f"output_exists: {result['output_exists']}",
        f"output_paragraph_count: {result['output_paragraph_count']}",
        f"summary_artifact_present: {result['summary_artifact_present']}",
        f"summary_artifact_output_ref: {result['summary_artifact_output_ref']}",
        f"transcript_path: {result['transcript_path']}",
        f"transcript_exists: {result['transcript_exists']}",
        f"transcript_entry_count: {result['transcript_entry_count']}",
        f"memory_root: {result['memory_root']}",
        f"memory_root_exists: {result['memory_root_exists']}",
    ]
    if result.get("artifact_result_path"):
        lines.append(f"artifact_result_path: {result['artifact_result_path']}")
    if result.get("error"):
        lines.append(f"error: {result['error']}")
    return "\n".join(lines)


async def _run(args: argparse.Namespace) -> int:
    _ensure_repo_root_on_syspath()
    from experiments.workflow_artifact_smoke.runtime import (
        run_workflow_artifact_smoke_experiment,
    )

    result = await run_workflow_artifact_smoke_experiment(
        workflow_name=args.workflow,
        query=args.query,
        output_filename=args.output_filename,
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

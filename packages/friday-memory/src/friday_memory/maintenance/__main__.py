# mypy: ignore-errors
"""
CLI Entry Point for Memory Maintenance Utilities.

Usage:
    python -m friday_memory.maintenance <command> [options]

Commands:
    backup      Create a backup of memory stores
    restore     Restore from a backup
    list        List available backups
    analyze     Analyze consistency issues
    prune       Prune redundant/stale memories
    synthesize  Synthesize new memories
    classify    Classify facts as falsifiable/conversational
    verify      Verify falsifiable claims
    reorganize  Run full reorganization pipeline
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="python -m friday_memory.maintenance",
        description="Memory Reorganization Utilities for Friday Memory",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Backup command ---
    backup_parser = subparsers.add_parser("backup", help="Create a backup")
    backup_parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Memory directory to backup",
    )
    backup_parser.add_argument(
        "--output",
        "-o",
        help="Backup output directory (default: <dir>/backups/<timestamp>)",
    )

    # --- Restore command ---
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Memory directory to restore to",
    )
    restore_parser.add_argument(
        "--backup-id",
        help="Backup ID to restore (default: latest)",
    )
    restore_parser.add_argument(
        "--backup-dir",
        help="Specific backup directory to restore from",
    )

    # --- List command ---
    list_parser = subparsers.add_parser("list", help="List available backups")
    list_parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Memory directory",
    )

    # --- Analyze command ---
    analyze_parser = subparsers.add_parser("analyze", help="Analyze consistency")
    analyze_parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Memory directory to analyze",
    )
    analyze_parser.add_argument(
        "--report",
        "-r",
        help="Output report to JSON file",
    )
    analyze_parser.add_argument(
        "--stale-days",
        type=int,
        default=90,
        help="Days before entity is considered stale (default: 90)",
    )

    # --- Prune command ---
    prune_parser = subparsers.add_parser("prune", help="Prune redundancies")
    prune_parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Memory directory to prune",
    )
    prune_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be pruned without modifying (default: True)",
    )
    prune_parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually perform the pruning",
    )
    prune_parser.add_argument(
        "--backup-first",
        action="store_true",
        help="Create backup before pruning",
    )
    prune_parser.add_argument(
        "--stale-days",
        type=int,
        default=90,
        help="Days before entity is considered stale (default: 90)",
    )
    prune_parser.add_argument(
        "--min-hits",
        type=int,
        default=1,
        help="Minimum hit count to keep entity (default: 1)",
    )
    prune_parser.add_argument(
        "--similarity",
        type=float,
        default=0.95,
        help="Similarity threshold for deduplication (default: 0.95)",
    )

    # --- Synthesize command ---
    synth_parser = subparsers.add_parser("synthesize", help="Synthesize memories")
    synth_parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Memory directory",
    )
    synth_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be synthesized (default: True)",
    )
    synth_parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually perform synthesis",
    )
    synth_parser.add_argument(
        "--backup-first",
        action="store_true",
        help="Create backup before synthesis",
    )
    synth_parser.add_argument(
        "--model",
        help="LLM model to use (default: from config)",
    )
    synth_parser.add_argument(
        "--api-base",
        help="LLM API base URL",
    )
    synth_parser.add_argument(
        "--api-key",
        help="LLM API key",
    )

    # --- Classify command ---
    classify_parser = subparsers.add_parser("classify", help="Classify facts")
    classify_parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Memory directory",
    )
    classify_parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum facts to classify (default: 100)",
    )
    classify_parser.add_argument(
        "--model",
        help="LLM model to use",
    )
    classify_parser.add_argument(
        "--api-base",
        help="LLM API base URL",
    )
    classify_parser.add_argument(
        "--api-key",
        help="LLM API key",
    )

    # --- Verify command ---
    verify_parser = subparsers.add_parser("verify", help="Verify claims")
    verify_parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Memory directory",
    )
    verify_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be verified (default: True)",
    )
    verify_parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually perform verification",
    )
    verify_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum claims to verify (default: 50)",
    )
    verify_parser.add_argument(
        "--model",
        help="LLM model to use",
    )
    verify_parser.add_argument(
        "--api-base",
        help="LLM API base URL",
    )
    verify_parser.add_argument(
        "--api-key",
        help="LLM API key",
    )

    # --- Reorganize command ---
    reorg_parser = subparsers.add_parser("reorganize", help="Full reorganization")
    reorg_parser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Memory directory",
    )
    reorg_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be done (default: True)",
    )
    reorg_parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually perform reorganization",
    )
    reorg_parser.add_argument(
        "--backup-first",
        action="store_true",
        default=True,
        help="Create backup first (default: True)",
    )
    reorg_parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup (dangerous!)",
    )
    reorg_parser.add_argument(
        "--skip-synthesis",
        action="store_true",
        help="Skip synthesis step",
    )
    reorg_parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip verification step",
    )
    reorg_parser.add_argument(
        "--model",
        help="LLM model to use",
    )
    reorg_parser.add_argument(
        "--api-base",
        help="LLM API base URL",
    )
    reorg_parser.add_argument(
        "--api-key",
        help="LLM API key",
    )

    return parser


def get_llm_service(args):
    """Create LLM service from args if provided."""
    if not hasattr(args, "model") or not args.model:
        return None

    try:
        from friday_llm import LiteLLMService

        return LiteLLMService(
            model_name=args.model,
            api_base=getattr(args, "api_base", None),
            api_key=getattr(args, "api_key", None),
        )
    except ImportError:
        logger.warning("friday_llm not available, LLM features disabled")
        return None


async def cmd_backup(args) -> int:
    """Handle backup command."""
    from friday_memory.maintenance.backup import BackupManager

    manager = BackupManager(args.dir)
    manifest = manager.create_backup(args.output)

    print("Backup created successfully!")
    print(f"  ID: {manifest.backup_id}")
    print(f"  Location: {manifest.backup_dir}")
    print(f"  Files: {len(manifest.files)}")

    return 0


async def cmd_restore(args) -> int:
    """Handle restore command."""
    from friday_memory.maintenance.backup import BackupManager

    manager = BackupManager(args.dir)

    if args.backup_dir:
        # Load manifest from specific directory
        manifest_path = Path(args.backup_dir) / "manifest.json"
        if not manifest_path.exists():
            print(f"Error: No manifest found at {args.backup_dir}")
            return 1

        from friday_memory.maintenance.models import BackupManifest

        manifest = BackupManifest.model_validate_json(manifest_path.read_text())
    else:
        # Find backup by ID or use latest
        backups = manager.list_backups()
        if not backups:
            print("No backups found")
            return 1

        if args.backup_id:
            manifest = next(
                (b for b in backups if b.backup_id.startswith(args.backup_id)), None
            )
            if not manifest:
                print(f"Backup not found: {args.backup_id}")
                return 1
        else:
            manifest = backups[0]  # Latest

    print(f"Restoring from backup {manifest.backup_id[:8]}...")
    manager.restore_backup(manifest)
    print("Restore complete!")

    return 0


async def cmd_list(args) -> int:
    """Handle list command."""
    from friday_memory.maintenance.backup import BackupManager

    manager = BackupManager(args.dir)
    backups = manager.list_backups()

    if not backups:
        print("No backups found")
        return 0

    print(f"Found {len(backups)} backups:\n")
    for backup in backups:
        print(
            f"  {backup.backup_id[:8]}  {backup.created_at.strftime('%Y-%m-%d %H:%M')}  "  # noqa: E501
            f"{len(backup.files)} files"
        )

    return 0


async def cmd_analyze(args) -> int:
    """Handle analyze command."""
    from friday_memory.maintenance.analyzer import ConsistencyAnalyzer
    from friday_memory.maintenance.models import PruneConfig

    config = PruneConfig(stale_threshold_days=args.stale_days)
    analyzer = ConsistencyAnalyzer(args.dir, config)

    report = await analyzer.analyze()

    # Print summary
    print(analyzer.generate_report_summary(report))

    # Save to file if requested
    if args.report:
        Path(args.report).write_text(report.model_dump_json(indent=2))
        print(f"\nReport saved to: {args.report}")

    return 0


async def cmd_prune(args) -> int:
    """Handle prune command."""
    from friday_memory.maintenance.backup import BackupManager
    from friday_memory.maintenance.models import PruneConfig
    from friday_memory.maintenance.pruner import RedundancyPruner

    dry_run = not args.no_dry_run

    if args.backup_first and not dry_run:
        manager = BackupManager(args.dir)
        manifest = manager.create_backup()
        print(f"Backup created: {manifest.backup_id[:8]}")

    config = PruneConfig(
        stale_threshold_days=args.stale_days,
        min_hit_count=args.min_hits,
        similarity_threshold=args.similarity,
    )
    pruner = RedundancyPruner(args.dir, config)

    report = await pruner.prune(dry_run=dry_run)

    print(pruner.generate_report_summary(report))

    return 0


async def cmd_synthesize(args) -> int:
    """Handle synthesize command."""
    from friday_memory.maintenance.backup import BackupManager
    from friday_memory.maintenance.synthesizer import MemorySynthesizer

    dry_run = not args.no_dry_run
    llm = get_llm_service(args)

    if args.backup_first and not dry_run:
        manager = BackupManager(args.dir)
        manifest = manager.create_backup()
        print(f"Backup created: {manifest.backup_id[:8]}")

    synthesizer = MemorySynthesizer(args.dir, llm_service=llm)
    report = await synthesizer.synthesize(dry_run=dry_run)

    print(synthesizer.generate_report_summary(report))

    return 0


async def cmd_classify(args) -> int:
    """Handle classify command."""
    from friday_memory.maintenance.fact_checker import FactChecker

    llm = get_llm_service(args)
    if not llm:
        print("Error: LLM model required for classification (use --model)")
        return 1

    checker = FactChecker(
        args.dir,
        classifier_llm=llm,
    )

    classified = await checker.classify_facts(limit=args.limit)

    print(f"\nClassified {len(classified)} facts:")
    falsifiable = sum(1 for c in classified if c.falsifiable)
    conversational = len(classified) - falsifiable

    print(f"  Falsifiable: {falsifiable}")
    print(f"  Conversational: {conversational}")

    for fact in classified[:10]:
        status = "FALSIFIABLE" if fact.falsifiable else "CONVERSATIONAL"
        preview = (
            fact.original_text[:50] + "..."
            if len(fact.original_text) > 50
            else fact.original_text
        )
        print(f"\n  [{status}] {preview}")
        print(f"    Type: {fact.claim_type.value}")
        print(f"    Reason: {fact.reasoning}")

    if len(classified) > 10:
        print(f"\n  ... and {len(classified) - 10} more")

    return 0


async def cmd_verify(args) -> int:
    """Handle verify command."""
    from friday_memory.maintenance.fact_checker import FactChecker
    from friday_memory.maintenance.models import FactCheckConfig

    dry_run = not args.no_dry_run
    llm = get_llm_service(args)

    if not llm:
        print("Error: LLM model required for verification (use --model)")
        return 1

    config = FactCheckConfig(batch_size=args.limit)
    checker = FactChecker(
        args.dir,
        classifier_llm=llm,
        researcher_llm=llm,
        judge_llm=llm,
        config=config,
    )

    report = await checker.run_full_check(dry_run=dry_run)

    print(checker.generate_report_summary(report))

    return 0


async def cmd_reorganize(args) -> int:
    """Handle reorganize command."""
    from friday_memory.maintenance.reorganizer import MemoryReorganizer

    dry_run = not args.no_dry_run
    backup_first = not args.no_backup

    llm = get_llm_service(args)

    reorganizer = MemoryReorganizer(
        args.dir,
        llm_service=llm,
    )

    report = await reorganizer.reorganize(
        backup_first=backup_first,
        dry_run=dry_run,
        skip_synthesis=args.skip_synthesis,
        skip_verify=args.skip_verify,
    )

    print(reorganizer.generate_report_summary(report))

    return 0 if report.success else 1


async def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.command:
        parser.print_help()
        return 1

    # Dispatch to command handler
    commands = {
        "backup": cmd_backup,
        "restore": cmd_restore,
        "list": cmd_list,
        "analyze": cmd_analyze,
        "prune": cmd_prune,
        "synthesize": cmd_synthesize,
        "classify": cmd_classify,
        "verify": cmd_verify,
        "reorganize": cmd_reorganize,
    }

    handler = commands.get(args.command)
    if not handler:
        print(f"Unknown command: {args.command}")
        return 1

    return await handler(args)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

# REM-001 Implementation Report

**Status:** Remediation candidate prepared for fresh independent review.

## Scope and decisions

- F-001: `friday_core.mcp` now defines bounded policy selections and safe
  identifiers for local stdio trust, workspace scoping, and disabled-by-default
  per-server/per-tool ingestion opt-in. Metadata carries schema cost,
  sanitization state, and typed filter diagnostics. Provenance carries optional
  call and correlation identifiers, output sanitization state, and a consistent
  ingestion decision. Discovery carries typed per-server connection, catalog,
  cache, filter/rejection, and refresh-eligibility facts. Unknown measurements
  and unassigned identifiers remain absent by default. These are contract
  shapes only; later WS-01/02/03/05/06/07 consumers must implement enforcement.
- F-002: Normalization still fails closed on collision. The error includes the
  canonical key and both ordered source pairs as bounded length, punctuation
  shape, and 12-character SHA-256 fingerprints. Raw source names are not echoed.
  The fingerprints describe names only; tool arguments and their hashes remain
  absent from the contracts by default.
- Cross-package DTO ownership and the read-only metadata-sidecar decision stay
  in `friday_core.mcp`. Existing standalone MCP implementation and integrated
  stdio-only posture are unchanged. No broad mypy suppression was added.

## Checks

- Focused core contract and MCP import tests: 44 passed.
- Core, MCP, and runtime package tests: 232 passed.
- Ruff for core and MCP: passed.
- Targeted mypy for `friday_core.mcp`: passed.
- Development-board validation: passed, 23 tasks; dashboard `render --check`:
  current; documentation lifecycle: passed, 317 Markdown files; `git diff
  --check`: passed.
- Runtime and agent import smoke: passed, using LiteLLM's local cost-map backup
  after the remote fetch was unavailable.
- Package-wide mypy retains the baseline NumPy stub syntax failure with the
  project's Python 3.10 target. With `--python-version 3.13`, it reaches four
  pre-existing errors in untouched `friday_core.profiles.py`.
- Integration tests retain the baseline development-board count assertion:
  23 passed, 1 failed, because the test expects 22 while the board has 23.

This report is builder evidence, not a validation verdict or maintainer
acceptance. Fresh delta and aggregate reviews are required.

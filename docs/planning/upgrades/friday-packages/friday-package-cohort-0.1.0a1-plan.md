# Friday Package Cohort 0.1.0a1 Plan

- Status: Published to production PyPI and post-publication verified
- Approval date: 2026-08-28
- Branch: `feature/friday-package-cohort-0.1.0a1`
- Trigger: Friday Chat clean installation exposed incompatible exact pins across
  the published `0.1.0a0` package graph.
- Evidence: [cohort release evidence](../../../reference/releases/friday-package-cohort-0.1.0a1-release-evidence.md)

## Objective

Restore a single installable Friday dependency graph by bringing every current
Friday distribution and every internal exact dependency pin to `0.1.0a1`, the
version that contains the latest Friday LLM public contract. This returns the
first-alpha package family to the lock-step policy already established by the
PyPI preparation plan.

## Release Cohort

All current distributions move to `0.1.0a1`:

- `friday-framework`;
- `friday-chat`;
- `friday-framework-agent`;
- `friday-framework-cli`;
- `friday-framework-core`;
- `friday-framework-finance`;
- `friday-framework-llm`;
- `friday-framework-mcp`;
- `friday-framework-memory`;
- `friday-framework-moltbook`;
- `friday-framework-optimization`;
- `friday-framework-runtime`;
- `friday-framework-sandbox`;
- `friday-framework-speech`;
- `friday-framework-telemetry`;
- `friday-framework-tools`;
- `friday-framework-transcript`.

Every internal requirement, including optional extras and self-references,
must use the same exact `0.1.0a1` pin. No compatible ranges are introduced in
this alpha cohort.

## Why The Full Cohort Is Required

Updating only direct Friday LLM consumers is insufficient. Exact pins propagate
the old LLM graph through Memory to Agent and Optimization, through Agent and
Memory to Runtime, through those packages to CLI and MCP extras, and finally to
Friday Chat and the root meta-package. Optional extras can recreate the same
conflict even when a default install succeeds. A complete lock-step bump makes
every supported installation shape resolve to one coherent graph.

## Scope

Authorized changes include:

- root and package `pyproject.toml` versions and internal Friday pins;
- package runtime version constants where they exist;
- `uv.lock`;
- metadata, artifact, smoke-install, and version-parity helpers/tests;
- package release notes/evidence and PyPI planning documentation;
- compatibility fixes only if validation proves an actual public-contract
  incompatibility with Friday LLM `0.1.0a1`.

Unrelated local config, runtime state, caches, and documents remain untouched.
Production PyPI publication was separately authorized and completed on
2026-08-28. TestPyPI was not used. Live provider execution and release tagging
remain separate authority gates.

## Implementation Sequence

1. Capture the branch, dirty-state, package graph, published versions, and
   existing validation baseline.
2. Change all 17 project versions and all internal exact pins to `0.1.0a1`.
3. Synchronize exported runtime versions and add parity checks.
4. Regenerate `uv.lock` and prove no stale `0.1.0a0` internal pins remain in
   active metadata or lock state.
5. Extend release helpers so a whole-cohort validation is the default release
   proof while retaining explicit subset support.
6. Run focused package tests, full repository tests, Ruff, and mypy; separate
   unchanged baseline debt.
7. Build every wheel and sdist from a clean committed worktree.
8. Validate metadata, dependency pins, extras, package contents, secrets, and
   Twine metadata.
9. Clean-install the entire cohort and smoke Friday Chat plus the root
   meta-package on Python 3.10, 3.11, 3.12, and 3.13 where provisioned.
10. Record immutable candidate hashes only after every deterministic and
    clean-install gate passes.

## Publication Order

Publish only after separate authorization, in dependency order:

1. Telemetry, Transcript, Sandbox, and Moltbook;
2. Core;
3. Finance, Friday LLM, and Speech;
4. Memory;
5. Agent and Optimization;
6. Tools;
7. Runtime and MCP;
8. CLI;
9. Friday Chat;
10. root `friday-framework` meta-package.

The next layer must not be uploaded until every exact dependency in the prior
layers is present and independently installable on the target registry.

## Acceptance Criteria

- Every Friday `project.version` is exactly `0.1.0a1`.
- Every internal Friday requirement and extra is exactly `0.1.0a1`.
- `uv lock --check` passes and the lock contains one coherent Friday version.
- Runtime version constants match distribution metadata where exposed.
- Metadata and artifact validators detect any stale `0.1.0a0` pin.
- All 17 wheels and sdists pass custom validation and Twine.
- Clean `friday-chat`, `friday-framework`, and extras installation resolves
  without workspace sources or `--no-deps` workarounds.
- Python 3.10-3.13 smoke evidence is recorded, or an unavailable environment is
  an explicit release hold.
- No rejected `51a112c` Friday Chat artifact is reused.
- No upload, tag, push, or live provider call occurs without its separate
  approval.

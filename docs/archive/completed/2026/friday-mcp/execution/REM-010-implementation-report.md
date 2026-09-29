# REM-010 implementation report

- Date: 2026-09-29
- Branch: `feature/friday-mcp-ws08-docs`
- Directive: `docs/planning/active/friday-mcp/remediation/REM-010-directive.md`, approved at `325947a5d3b727dfe07fde4bb136e3f7525535b9`
- Finding: `VAL-019-F-001` in the historical `VAL-019-report.md`
- Product candidate: `fb3712127229ba032427b8f3deae04da543e646d`
- State: bounded implementation complete; independent delta and complete aggregate review pending. VAL-019 is superseded for decisions on this changed candidate, with its original files preserved.

## Product delta

The product commit changes exactly the five directive-allowed Memory source/test paths. Snapshot staging now explicitly returns `False` if a malformed, unvalidated copy has no call ID, before any lookup or write. The three collection moves declare the actual numeric embedding sequences using Chroma's `PyEmbeddings` shape; values and collection transitions are unchanged. Orphan cleanup uses a local, runtime-checked node-listing protocol, reports a missing capability through its existing error-result path, and leaves the Core graph interface unchanged. The Memory completion union is an explicit `TypeAlias`; the typed and legacy request paths, warning, and response parsing remain unchanged.

New behavioral coverage exercises the missing-ID no-write case and existing valid snapshot path, the promotion/demotion/reactivation cycle with persisted numeric embeddings, graph cleanup preview/deletion/shared nodes/missing listing, and typed versus legacy structured completion. Existing native collection and legacy completion tests also remain green.

## Verification

All commands ran without live providers or external effects. `uv run` commands used `UV_CACHE_DIR=/private/tmp/friday-uv-cache`, `UV_NO_SYNC=true`, and `LITELLM_LOCAL_MODEL_COST_MAP=true`; pytest also used `PYTHONDONTWRITEBYTECODE=1` and disabled its cache plugin. The exact joint VAL-019 mypy arguments ran with a fresh `MYPY_CACHE_DIR=/private/tmp/rem010-mypy-fresh-2`:

```sh
uv run --no-sync mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py packages/friday-mcp/src/friday_mcp/client packages/friday-runtime/src/friday_runtime packages/friday-chat/src/friday_chat packages/friday-memory/src/friday_memory packages/friday-transcript/src/friday_transcript packages/friday-telemetry/src/friday_telemetry
```

It exited 0: no issues in 176 source files. Other results:

| Check | Result |
| --- | --- |
| Focused collection manager, completion, MCP memory, and Memory maintenance pytest | 154 passed, exit 0 |
| Complete `packages/friday-memory/tests_memory` plus `tests/integration/test_mcp_memory_ingestion.py` pytest | 722 passed, 1 skipped, 1 pre-existing legacy-client deprecation warning, exit 0 |
| Ruff on `packages/friday-memory` and the MCP memory integration test | All checks passed, exit 0 |
| `uv lock --check --offline` | Lock current, exit 0 |
| Documentation lifecycle, board validate, dashboard render check | Passed, exit 0 each |
| `git diff --check` and staged product diff check | Passed, exit 0 |

The broader Chat and top-level integration nonzero outcomes in historical VAL-019 are inherited, separately classified there, and were not rerun for this bounded Memory remediation; they are not represented as passes or waivers. The initial board-helper calls without `--no-sync` attempted a package build and failed because the restricted environment could not fetch `hatchling`; the required `--no-sync` board checks then passed.

## Scope and preservation

The staged product list was verified as exactly the five allowed paths before commit; `git show --stat fb3712127229ba032427b8f3deae04da543e646d` reports those five paths only. SHA-256 fingerprints for `.DS_Store`, deleted `family-tree.md`, the 57 files in `docker-bench-security/`, the Chat YAML backup, the Sandbox audit Dockerfile, and the five original VAL-019 request/report/evidence/manifest files matched the pre-commit record at `/private/tmp/rem010-preservation-before.json`. No board, packet index, queue/log, Core, interface, lock, prior report, unrelated dirty file, or historical validation byte was edited. No push, merge, release, live-provider call, or external UAT occurred.

Next gate: freeze this candidate for a fresh-context, read-only independent REM-010 delta review followed by complete `20c70dd70622e5f1b80029076a789fb58c748fb5d`-based feature-branch aggregate review. This local result does not imply initiative completion, maintainer acceptance, WS-09 authority, or delivery.

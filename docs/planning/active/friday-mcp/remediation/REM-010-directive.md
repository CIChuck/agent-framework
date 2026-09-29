# REM-010 — Close Aggregate Memory Typing Gate

- Date: 2026-09-29
- Status: Draft; explicit maintainer approval required before product edits
- Initiative: `friday-mcp`
- Finding: [VAL-019-F-001](../validation/VAL-019-report.md), Medium
- Reviewed aggregate candidate: `847d410934150865395bdcf58beb2a9342cd19f8`
- Baseline: `20c70dd70622e5f1b80029076a789fb58c748fb5`
- Branch: `feature/friday-mcp-ws08-docs`
- Cycle: first aggregate remediation

The nine accepted work units remain accepted. Fresh VAL-019 found that the
joint Python-3.13 mypy check required for the complete feature-branch
aggregate exits 1. Five errors are visible in the modified Memory collection
manager, including a new `str | None` call ID passed to an API requiring
`str`; removing that file's historical broad suppression exposed four older
vector/graph typing errors. Four additional errors in unchanged Memory LLM
completion are inherited, but must either be fixed within this bounded scope
or explicitly waived to make the required joint gate meaningful. This
directive chooses a small typed fix, not a waiver. The original VAL-019
report/evidence and accepted WS-08 product candidate remain historical inputs.

## Exact product scope

- `packages/friday-memory/src/friday_memory/retrieval/collection_manager.py`
- `packages/friday-memory/src/friday_memory/llm_completion.py`
- `packages/friday-memory/tests_memory/test_retrieval/test_collection_manager.py`
- `packages/friday-memory/tests_memory/test_llm_completion.py`
- `packages/friday-memory/tests_memory/test_mcp_memory.py`

A REM-010 implementation report, new manifest, request/review/evidence,
status and board/packet updates are process artifacts. Do not edit Core,
Chroma adapters, other Memory files, Chat, Runtime, MCP, Transcript, Telemetry,
dependencies, lock, accepted work-unit reports, original VAL-019 inputs or any
unrelated dirty path. If a correct fix requires a shared interface or another
package, stop and return the proposed scope change for maintainer review.

## VAL-019-F-001 — Required joint typing command fails

1. At MCP snapshot staging, narrow the optional call ID with an explicit
   runtime check before passing it to `find_mcp_snapshot`. Preserve the
   validated snapshot contract and fail closed for impossible malformed input;
   do not use a cast or unchecked assertion as the only guard.
2. Give the three Chroma `Collection.add` calls a truthful declared embedding
   shape compatible with their actual numeric sequences without changing
   stored values or promotion/demotion/reactivation behavior.
3. Express the `get_all_nodes` capability at the collection manager's local
   boundary with an explicit typed capability and safe handling when absent.
   Do not silently widen the mandatory Core `GraphStoreAdapter` contract or
   reach into an implementation's private attributes.
4. In `llm_completion.py`, make the existing typed/legacy union a real type
   alias and preserve the runtime typed-client versus legacy-client split.
   Do not change completion requests, warning behavior or result parsing.
5. Add focused tests for the invalid call-ID guard, existing valid snapshot
   path, promotion/demotion/reactivation and graph-node cleanup capability,
   and typed/legacy Memory completion compatibility where needed to cover the
   corrections. Keep the tests behavioral rather than mirroring annotations.

## Verification and closeout

Run the **exact joint Python-3.13 mypy command** in
[VAL-019 request](../validation/VAL-019-request.yaml) with a fresh scratch
cache; it must exit 0, or stop and report any newly visible error without
expanding scope. Run focused Memory MCP, collection manager, completion and
maintenance tests, the complete Memory package and MCP memory integration
tests, affected Ruff, offline lock, board and documentation checks, and
`git diff --check`. Recheck native-only and legacy-client behavior. Verify the
five unrelated fingerprints and a product delta confined to the five allowed
paths.

Commit a stable corrected candidate, mark VAL-019 superseded only for decisions
on that changed candidate while preserving its report and evidence byte-exact,
and request a **new** fresh-context read-only review of this remediation delta
followed by the complete `20c70dd`-based feature-branch aggregate. Do not infer
initiative completion, acceptance, WS-09 authority or delivery from a local
green check. A separate remediator is required for this cross-package typing
boundary under the independent-validation policy; no product work begins until
the maintainer approves this exact directive and assignment.

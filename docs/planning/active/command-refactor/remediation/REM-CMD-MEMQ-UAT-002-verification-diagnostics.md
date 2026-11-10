# REM-CMD-MEMQ-UAT-002 — bounded verification response diagnostics

Status: **authorized for implementation** by Chuck Russell’s explicit “proceed”
following the diagnostic scope: preserve role/model/completion reason and safe
validation fields, distinguish incomplete responses, preserve strict validation
and rollback. This records that current direction; no additional approval is
requested. The earlier Chat-only two-fix proposal remains unapproved and held.

## Baseline, precedence and exact exception

Initiative friday-command-refactor; started/local; branch feature/command-retirement.
Base f530e7550bad18bdb7771b6843a80aad675d8ce5. Maintainer direction takes precedence
within this named scope; all other approved MEMQ limits remain. This explicitly
permits the small shared Friday Memory additions below despite the ordinary
Chat parity freeze. Prior D3 VERIFIED applies to bab16757/source e4c0b9a2 only.
This repair must receive fresh independent review before being called verified.

The actual full run1bca75db4f1d4d049db21d167e4c13b7 failed at verify with234
candidates and MaintenanceResponseValidationError, after synthesis created0
records with156 quarantined sources. It reported completed verified rollback.
The exact role/field and production truncation remain unknown. The configured
verifiers are classifier/researcher Gemini2.5 Flash and judge Gemini3.5 Flash
Lite through OpenRouter, each with maintenance’s8000-token fallback. No model,
YAML or token-budget change is authorized by this diagnostic unit.

## Ownership and implementation allowlist

| Path | Exact allowed change |
| --- | --- |
| packages/friday-memory/src/friday_memory/llm_completion.py | Add backward-compatible optional model and finish_reason to immutable MemoryCompletion; retain typed response metadata and legacy model where available. Existing execution/override/credential behavior unchanged. |
| packages/friday-memory/src/friday_memory/json_response.py | Add an opt-in strict enclosing-object mode that cannot recover a nested object from incomplete/invalid outer JSON. Preserve the existing default parser behavior for all other callers, reasoning exclusion and complete fenced/noisy JSON compatibility. |
| packages/friday-memory/src/friday_memory/response_diagnostics.py (new) | UI-neutral immutable safe diagnostic types and bounded validation issue extraction/formatting. Known schema field paths/type codes only; redact unknown input-controlled keys. No raw response, prompts, credentials, reasoning or Pydantic input/context values. |
| packages/friday-chat/src/friday_chat/reorganization/mutation.py | Use shared diagnostics and strict enclosing-object parsing at maintenance completion; distinguish explicit length termination from generic parse/schema failure; propagate only typed safe diagnostics through existing preflight/step errors. Preserve step order, schemas, exact coverage, cancellation policy, provider requests and rollback. |
| packages/friday-memory/tests_memory/test_llm_completion.py; test_json_response.py; test_response_diagnostics.py (new) | Metadata compatibility, strict/default parser boundaries, headless import, redaction/bounds and immutability tests. |
| packages/friday-chat/tests_chat/test_reorganization_response_diagnostics.py (new) | Canonical provider path, role/model/reason/field evidence, controlled234-response truncation, unsafe provider input tripwires, safe step/journal/terminal propagation and rollback controls. |
| Current packet README/authority/next-phase/tactical/execution-log; board/dashboard; this directive and a matching approval record | Current repair state, authority and immutable evidence links. No historical evidence rewrite. |
| validation/memory-queries/uat-diagnostics/ (new) | Frozen request, exact manifests, commands/output, review and diagnostic handoff. |
| Chat framework follow-up log | Record diagnostics support and unresolved live failure without claiming repair or acceptance. |

No neutral command semantics, entity quoting, ingestion behavior, package metadata,
dependency/lock, config, provider route, output budget, batch policy, pipeline
ordering, source quarantine, recovery API or user data change. No permissive
coercion or partial-verification acceptance. No live provider/paid calls, operator
reorganization or recovery against personal stores. Provider-free disposable
rollback tests are authorized. The functional verification
fix, entity/ingest shared-owner repairs and human UAT remain later gates.

## Required behavior and acceptance criteria

- VD-01: Typed completion model/finish_reason survive the shared Memory boundary.
  Existing callers and legacy clients work with absent finish metadata.
- VD-02: Strict parsing accepts complete objects and supported fenced/noisy forms;
  incomplete enclosing objects and top-level arrays cannot be replaced by a nested
  object. The legacy default parser is byte/behavior-compatible through its tests.
- VD-03: Maintenance refuses explicit length-limited responses even if their text
  happens to contain a complete object. Unknown finish metadata remains unknown;
  syntax failures must not be falsely called confirmed token truncation.
- VD-04: Safe error evidence contains the maintenance role, configured model,
  schema, canonical available finish reason and bounded field/type summaries.
  Unknown response keys are redacted; raw input, validator context/message,
  prompt/response/reasoning content and credentials cannot enter errors/journals.
- VD-05: Diagnostics reach existing failed mutation results, categorical journal
  and terminal output. Valid responses still succeed; schema/coverage failures
  still fail closed; coordinator rollback remains intact. No retry or extra
  service call is introduced.
- VD-06: Synthetic234-decision complete control passes. Truncated outer JSON fails
  as parse/incomplete, rather than validation of a recovered inner decision.
  The witness is not represented as the actual production response.
- VD-07: A fresh headless subprocess uses shared diagnostic/parser/completion code
  while forbidding Chat/Commands/TUI imports. Reuse does not require importing Chat.
- VD-08: All changes stay in the allowlist and preserve the three dirty files,
  existing exports, external locator, supplied evidence and personal stores.

## Verification and review

Use the frozen uv environment/Python3.13, -B and private external caches/basetemps.
Run the changed Memory and Chat tests first, then relevant Memory LLM/maintenance
and Chat reorganization regressions, full Chat (live_lmstudio excluded), Commands/
cohort and CLI. Counts are observations, never hardcoded acceptance substitutes.
Run changed-source Ruff/mypy, new-file format checks, pinned no-new-format-debt,
board/dashboard/docs and diff checks. Known root/whole-file format and dirty-config
whitespace debt remain unwaived; do not reformat unrelated source or user edits.

Commit one stable candidate, then a fresh independent read-only validator reviews
this delta and the bounded interaction with current MEMQ/maintenance. Use a new
private scratch and explicit source origins. No inherited builder conclusions,
repairs, nested delegation or full historical council replay. This is a diagnostic
subunit under repository independent-validation policy; not a new D0–D3 sequence.
At most two bounded correction cycles; escalate remaining mandatory findings.

Stop if a repair requires another package/semantic/state change or missing
service metadata cannot be obtained within the declared optional fields. Stop
for protected-input drift. After VERIFIED, hand back the diagnostic candidate
and exact retest instructions. A fresh process must load the repaired code;
the running process is not modified. Human UAT and actual failure resolution
remain pending until a newly captured result establishes the failed role/field.
No acceptance, push, merge, release or new provider authority follows.

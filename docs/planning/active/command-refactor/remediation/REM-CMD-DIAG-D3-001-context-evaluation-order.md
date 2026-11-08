# REM-CMD-DIAG-D3-001 — preserve context formatting and count order

Status: **proposed contract amendment and bounded remediation; approval pending**.
This document grants no implementation authority until Chuck Russell approves
its exact bytes. Existing contract, directive, preparation and prior remediation
records remain unchanged. Human DIAG acceptance and delivery remain pending.

## Finding and controlling decision

**DIAG-D3-ASTRA-001 (medium, mandatory)** affects the complete bounded aggregate
at `1d3b273b7797c72a868f259d095593a15a4e42b9`. The
[round-1 reconciliation](../validation/diagnostics/implementation/d3/council-round1-reconciliation.md)
records Sol VERIFIED 9.7, Astra CHANGES_REQUESTED 8.7 and Claude VERIFIED 9.7.
A mandatory reproduced incompatibility takes precedence over the other results.

The approved [contract DG-02/03](../diagnostics-command-contract.md) fixes
`context_text() -> str` and shared `len(text)` before export. Legacy Chat formats
the selected text before evaluating the displayed length. Both requirements
cannot be fulfilled for arbitrary accepted stateful string subclasses through
that unchanged seam. DG-03 expressly says:

> Stop for any other incompatible legacy value and request a contract decision;
> do not silently stringify text or broaden these exceptions.

The recommended decision is to **preserve legacy behavior** through the narrow
typed projection amendment below. This proposes no new compatibility waiver.
Approval supersedes only the specified DG-02/03 algorithm and the related
source-freeze/test assertions that would otherwise prevent this correction.
All other original approval and DG-01–06 / DG-T01–14 requirements still apply.

## Reproduced behavior

[Controller characterization](../validation/diagnostics/implementation/d3/context-evaluation-characterization.json)
uses the actual baseline handler AST at `9dbcec54` and the current wrapper.
It reproduces the differences on source and actual installed interpreters in
normal and optimized modes, under the pinned guard and private export roots.

| Accepted input, with `--debug` | Legacy | Current candidate |
| --- | --- | --- |
| Plain `"abc"` control | Same output/file | Same output/file |
| Formatter changes subsequent length from 3 to 99 | Truth-test length, format, length; displays 99 | Truth-test length, length, format; displays 3 |
| Formatter and second length can each raise | Formatter exception first | Length exception first |
| Length raises only after formatting | Length exception; no export directory/file | Success; `--file` can write a file |

Each row covers debug-only and debug-plus-file paths. The last two rows show
failure-order and file-effect differences as well as the displayed-count issue.
Ordinary values passing the 72 frozen observations do not establish these cases.

## Exact proposed interface and ownership amendment

Add one method to the existing `friday_commands.diagnostics.DiagnosticsPort`:

```python
def context_debug_snapshot(self) -> ContextData: ...
```

Retain `context_text() -> str` and every other existing signature. No model,
closed outcome alternative, export name, command metadata, dependency or
configuration changes are proposed.

The shared context handler continues to own exact flag selection. After the
unchanged request → execution → canonical-name checks:

1. Without exact `--debug`, call `context_text()` once and construct
   `ContextData(text)`, as before. Do not call the new capability.
2. With exact `--debug`, call `context_debug_snapshot()` once. Require exact
   `ContextData`, a non-None `character_count` and `export_path=None`. Wrong
   snapshot type raises `TypeError`; an absent count or preexisting export path
   raises `ValueError`. Do not recompute length or reformat the snapshot text.
3. With exact `--file`, call the existing synchronous `export_context(data)`
   once, after the complete snapshot/count exists, validate its string return
   and return typed data carrying that path. Failure propagation, no retry or
   rollback, flag repetition/case behavior and effect ordering remain unchanged.

The Chat port implements the new fact projection by selecting the original
cached-or-fallback text through `context_text()` exactly once, validating it
with the existing typed string boundary, applying its empty format spec once,
then calling `len` on the original selected string. The formatted portion is
copied to a plain built-in string without invoking its formatter again and
returned as `ContextData(formatted_text, character_count)` with no export path.
The snapshot contains only the formatted text portion and count, without the
English debug heading or footer. Existing Chat renderers retain those messages.

This is explicit host projection of a valid string, consistent with other
diagnostic fact projections. Neutral models still accept string subclasses
without conversion. Truthy non-string cache values still fail before formatting
or file effects under the already-approved boundary. Falsy fallback reads,
non-debug output identity/formatting and the legacy raw non-debug file body stay
unchanged. The shared owner never imports Chat, renders English, parses a second
command or delegates to a legacy engine. The host never selects flags or returns
its own independent command result. No callback or runtime object crosses the
boundary. The current per-invocation export-body cache may remain; removing or
redesigning it is outside this finding.

## Bounded implementation scope after approval

Only these paths may change outside planning documentation:

- `packages/friday-commands/src/friday_commands/diagnostics.py`
- `packages/friday-commands/tests_commands/test_diagnostics.py`
- `packages/friday-chat/src/friday_chat/commands/diagnostics.py`
- `packages/friday-chat/tests_chat/test_command_diagnostics.py`
- `packages/friday-commands/README.md`, only to describe this capability
- `packages/friday-chat/README.md`, only to describe this correction

Update `validation/diagnostics/installed_probe.py` and add separate correction
evidence/status records under this packet. Existing D1/D2 test fakes and
context-specific assertions may change only as required by the new capability;
retain every unrelated assertion/body and all required named nodes. Record an
exact before/after AST exception map. Do not edit contracts.py, __init__.py,
registry.py, fixtures, old SESSION tests, metadata/lock, configuration, frozen
preparation/capture/comparison programs, accepted probes or prior evidence.
Both dirty examples and existing ignored exports retain exact bytes and metadata.

Use a separate bounded remediator for the interface correction, then fresh
independent review; it must receive this exact approval and numbered finding.
No additional advisory cleanup, later command family, TUI or delivery work.

## Required proof and stop

- DG-T04 proves exact capability selection, zero construction reads, one call,
  strict snapshot refusals and count-before-export without recalculating facts.
- DG-T10/11 prove legacy-equal output, traces, exception identity and absence of
  writes on the stateful/raising inputs above, including repeated/reordered
  debug/file flags. Retain once-only formatting and distinct injected outcome
  consumption. Non-debug behavior and the four approved refusals stay covered.
- Show the new regression assertions fail on the actual unfixed candidate at
  test-call phase and pass on corrected source. A count-before-format mutant and
  a format-twice mutant must be rejected through assertions; setup failures earn
  no rejection credit. Confirm canonical module roots/hashes at start and end.
- Extend actual installed proof with explicit normal/optimized assertions for
  these cases and the new neutral capability. Retain all six once-only shared
  delegations, retained pilot/SESSION proof and strict inventory/origin controls.
- Run all named and owning suites, focused static/type/format checks, source
  captures, preservation/AST audits and administration. Reconcile any additional
  cases against the previous 1,971 total. Root Ruff 534, the test_display conflict
  and legacy registry formatting remain failed/unwaived baseline debt.
- Commit corrected product/probe source, then rebuild and replay from that exact
  revision using the same closed inputs. Refresh both artifact hash maps, default
  138-name/version equality, all eight actual installed probe lanes, adversarial
  member/origin/archive/semantic controls and clean restored copies. Old 30790
  builds and round-1 evidence remain preserved as historical proof only.
- Freeze a new candidate for fresh Sol/Astra/Claude remediation-delta review,
  followed by complete bounded D3 and DIAG aggregate conformance. Reconcile all
  mandatory findings before human DIAG acceptance. Stop for any further contract
  conflict, protected drift, unexpected scope/dependency change or new regression.

Approval authorizes only this interface amendment and its bounded construction,
proof and review. It grants no DIAG acceptance, full-refactor/P0/P1/TUI completion,
cleanup or external delivery authority.

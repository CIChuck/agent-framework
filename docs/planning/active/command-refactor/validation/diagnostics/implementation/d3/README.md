# DIAG-001 D3 — regression, artifacts and isolated installed proof

Execution phase: validation. Validation state: in_review (correction cycle1).
DIAG-D3-ASTRA-001 is addressed under the exact maintainer-approved
[REM-CMD-DIAG-D3-001](../../../../remediation/REM-CMD-DIAG-D3-001-context-evaluation-order.md)
([approval](../../../../approval/diagnostics-context-evaluation.md)). No unit
acceptance, advancement or delivery is granted.

## Correction cycle1 (current)

Corrected product/test/probe source: `28c544fa67e934f03c212aed39ba20802b500b13`.
Only the six amendment paths changed outside planning documents, plus
`installed_probe.py`; contracts, `__init__`, registry, fixtures, metadata, lock,
configuration and frozen capture programs are unchanged. The AST exception map
is embedded in [correction evidence](correction-evidence.json).

- Shared `/context` uses `context_debug_snapshot()` once, only for exact
  `--debug`, strictly refusing non-`ContextData`, missing counts and preset paths
  before export. Chat selects once, formats once, then measures the original
  string, matching legacy output, traces, exception identity and file effects
  on 12/12 stateful/raising characterization rows (9 differed before the fix).
- Unfixed candidate: 28 failures with call-phase assertion witnesses in DG-T04,
  DG-T10 and DG-T11. Nine mutants, including count-before-format and
  format-twice, are rejected by assertions; unchanged control 539 passes with
  stable private module origins, test hashes and repository exports.
- Source: Chat 1,338, Commands/cohort 498, CLI 155 (1,991 = 1,971 + 20 new
  DG-T04 cases); D2-fast 538, D3-fast 166; DIAG 68 + 4 approved refusals,
  SESSION 25, pilot 196.
- Closed bundle and replay of `28c544fa` match 154 artifacts, 13 builds, 125
  locked inputs and the 138-name default closure. Eight installed probes pass,
  with explicit normal/optimized format-then-length and strict snapshot checks.
  50 member/origin, 4 semantic and 10 archive refusals, 2 source refusals and 8
  restored copies pass. The corrected probe rejects round-1 `30790ec0` artifacts
  through its new assertions in both lanes and modes.
- Every workspace artifact hash differs from round 1 because `SOURCE_DATE_EPOCH`
  follows the commit time. Two early mutation sweeps preceded test refinements
  and earn no credit. Root Ruff 534, test_display conflict and registry format
  remain failed/unwaived. Ignored exports equal the frozen inventory.

## Preserved round-1 builder evidence

The following records the reviewed candidate. Passing receipts remain intact;
they do not close the additional stateful-string incompatibility.

Exact CLI, defined before final installed executions:

```sh
INSTALLED_PYTHON -I -B [-O] validation/diagnostics/installed_probe.py \
  --lane neutral|chat --prepared PRIVATE_PREPARED --source CLEAN_GIT_EXPORT \
  --dist BUNDLE/g5-dist --profile BUNDLE/LANE-profile.txt \
  --accepted-profile PINNED_SESSION_PROFILE --pilot-probe PINNED_PILOT_PROBE \
  --session-probe PINNED_SESSION_PROBE --revision ARTIFACT_SOURCE_COMMIT \
  --report FRESH_PRIVATE_REPORT.json
```

Only actual installed interpreters import product modules. The source export
supplies inventory/oracle bytes. Both normal and optimized modes explicitly load
the pinned guard. Safe environment and each actual child argv/exit are recorded.
No providers, secrets, real stores or network are exercised.

Accepted SESSION complete member/type/directory/byte/executable and file/path
origin helpers are hash-verified read-only inputs. Commands/Chat origins bind to
the inventoried distribution roots, including the entry-point child. The old
SESSION probe remains untouched; its obsolete 24-export neutral entry point is
not run or claimed passed. The new retained SESSION neutral function changes
only its name and fourteen literal export names, with the remaining AST audited.
SESSION Chat checks are reused unchanged. The accepted pilot probe runs unchanged.

New proof covers strict models/factory/ports, explicit neutral registration,
canonical six-command delegation, original parsed args, exact metadata and
68 frozen rows plus four approved refusals, unconditional per-dispatch counts,
consumed injected outcomes, custom/renamed/current context, fallback/recorded
snapshots, pending/failure/cancellation and private fixed exports. Complete
installed inventory/origin/archive controls remain separate from source tests.

Initial probe syntax/development trials are historical only. Final proof binds
identical product/probe source and two closed bundle trials. Existing product,
tests, dependency/lock and original evidence stay frozen. Ignored synthetic
exports and both dirty examples remain preserved. Root Ruff 534, test_display
conflict and registry formatting stay failed/unwaived. Final aggregate council
precedes human acceptance. UAT, later families, P0/P1/TUI and delivery stay open.

## Current builder results

[Evidence](evidence.json), [preservation](preservation.json),
[profiles](profile-comparison.json), [retained SESSION AST](retained-session-AST.json)
and [before inventory](before-inventory.json) bind exact source, commands,
outputs, hash maps and limitations. 1,971 source tests pass; two 13-build/125-input
trials match all 154 artifact hashes and profiles. Eight actual installed probes
pass; neutral 1/default 138 closures are exact. Complete Commands/Chat inventory
is 7+63 source/data files and 18+134 sdist members.

Copied installs reject 50 member/origin changes; four independent runtime engine
substitutions demonstrate delegation/outcome rejection. Ten archive controls,
precise zero-command/zero-download prebuild refusal, two source-capture refusals
and 8 restored clean copied probes pass. Each negative has its expected terminal
RuntimeError reason; setup errors earn no credit. Every copy verifies interpreter
prefix and canonical package roots before mutation. Parent and entry child
origins bind to inventoried roots. Ignored exports retain bytes/modes/timestamps.

Prototype `e42bfb22` syntax generation, `2d21fefe` development runs and `a5f1be65`'s incorrect registry
order assertion are preserved historical receipts. Final source/probe is
`30790ec0f06813e7331c851d04c123997a398d97`; generic registry snapshots are correctly
canonically sorted, while the DIAG spec/factory order remains its frozen order.
The old SESSION main neutral 24-export assertion is not claimed passed. No old
API was spoofed; the retained copy's only changes are its name and approved 14
literal appended names. Existing package and test bytes stay frozen since D2.

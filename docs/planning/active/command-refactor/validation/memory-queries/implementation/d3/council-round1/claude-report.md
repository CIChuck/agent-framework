# MEMQ-001 D3 + bounded aggregate — council round1, seat Claude (Opus 5.5/high)

**Verdict: VERIFIED** (D3 and bounded MEMQ aggregate only). No mandatory findings.
Advisory rubric: **9.5/10**. Not acceptance; UAT20 NOT RUN; no delivery.

Candidate `bab167579a0c6fcae8765f263ec754f1d4700d93`; artifact/probe source `e4c0b9a2c5e80569829cc56af9addc8b3e358714`;
D3 start `4d3fb148…`; aggregate base `c5871054…`. Request SHA256 `6c9e21b2…220a` verified before reading; manifest `0ee4fc20…09e9`
and provided tree `3709edd3…90b5` verified and fully traversed. No builder reasoning or prior verdict consumed; D2 history used only for provenance.

## Mandatory findings
None.

## Advisory observations (non-blocking)
- A1. The approved directive's allowlist prose says "fifteen (P) / eighteen (R)" package paths, but its table enumerates 14 / 17. All 17 changed product paths are in the table. This is a counting defect in the pinned, approved document, not in the implementation.
- A2. Directive line 3 still says "fresh council pending at this correction freeze". It is pinned or immutable, and current status lives in the packet, board and authority, which agree.
- A3. `friday-dev-board.py next` selects `friday-langfuse-integration` (AWAITING_APPROVAL) by priority. `show friday-command-refactor` is started/granted on this branch. This is unrelated to MEMQ.
- A4. Five of the 20 retained D2 mutants also produced non-assertion failures (ValueError/TypeError/TimeoutError). I gave those zero credit. Each of the five still has at least one genuine call-phase `AssertionError` witness.

## Commands actually executed by me (own scratch, `-B`, `PYTHONDONTWRITEBYTECODE=1`, `GIT_OPTIONAL_LOCKS=0`)
| Lane | Result |
| --- | --- |
| Integrity start/end (all 8 manifest groups, 275,082 tree entries, Git identity) | 0 mismatches both boundaries; ls-files SHA `bcd89cb4…a865` before status, identical |
| 720 embedded/raw pairs (9 files: 64/26/94/10/18/10/15/10/473) | 720/720 embedded==sha==raw; 473 current (449 fresh, 8 inspected-prior, 16 dev-attempt labelled) |
| Own pinned prepare.py + guard selftest | offline startup OK; guard 18 refusals |
| Commands/cohort, Chat (excl. live_lmstudio), CLI | 599 / 1390 (1 pre-existing warning) / 155 passed = 2144 |
| Neutral new / named Chat / fast D2 / fast D3 | 101 / 52 / 616 / 117 passed; all 14 MQ-T nodes present (T01 24, T02 1, T03 6, T04 66, T05 1, T06 3, T07 1, T08 6, T09 6, T10 15, T11 9, T12 8, T13 1, T14R 6); no skip/xfail/sleep |
| Passive origin witness (collected/finish/after) | 14 snapshots; every friday_* module canonical repo `packages/*/src`, 0 drift |
| Ruff named+probe+R files; mypy | pass; mypy "no issues in 15 source files" |
| new-format 5; raw changed-format 9; format_debt check | 5 formatted; 4 baseline-debt files fail (adapters/memory/registry/runtime), 5 pass; `new_format_debt: {}` |
| Root Ruff / root collect / root pytest | 534 errors (fail, unwaived); 7082 collected + `test_display` collision error (=6929+101+52); root pytest interrupted same collision |
| AST audit (own script) | test_diagnostics & test_session_views exact after MQ-D4 reversal; union 18; contracts additions only (+alias,13 models; changed only FoundationData/CommandOutcome); registry tuple 39, changed idx 3,9,10,11,12,16, 33 unchanged, only wrappers/helper/imports; memory.py preview_text/record_value/__all__ unchanged; option R files only named additions; 4 retained probe bodies exact after approved rename(+16 names, 38→54 unique) |
| Own closed build + replay of e4c0b9a2 export | both passed; 154 artifacts equal, profile equal, 8 tools, 125 locked, 13 workspace builds each; equal to builder maps; vs baseline 27 changed/127 identical; neutral profile = 1 dist; Chat pip check 138 compatible |
| Own 8 installed main probes (pilot+MEMQ × neutral/Chat × -I -B / -I -B -O) | all exit 0 status passed; MEMQ revision e4c0b9a2, probe 40e9ca72; 305 Chat origin modules all in own prefix; entry-point child `--help` exit 0; Chat closure = accepted 138 name/version (profile materialized from pinned DIAG correction-evidence 641d9b0d, sha 7414804f) |
| Installed semantics (from own reports) | 13 models, 27 strict refusals, 54 exports, 6 pending; 6 canonical delegations, 18 factory/18 handler calls, injected/renamed/custom ×6; retained DIAG 68+4, SESSION 25 |
| Persisted option R (installed, normal & -O) | real FrameworkMemoryAdapter; single 1/multi 11/re-ingest 22/promotion; 6 groups incl. absent(None) and empty("") distinct; no source/decayed reads; records unchanged |
| Retained no-description ingest (own installed prefix) | `/ingest FILE` still raises Chroma `TypeError` (unwaived); explicit description works and lists |
| Reconstructed controls (all paths rewritten to own scratch; Git via read-only GIT_DIR/GIT_WORK_TREE) | 50 installed member/origin/shadow refusals (each after copied-root identity), 10 archive, 1 prebuild (0 builds/0 downloads), 4 DIAG + 6 MEMQ semantic, 8 restored clean copies; all exact reasons |
| Reconstructed source captures (private CWD launcher) | MEMQ 68+2+6 twice; DIAG 72 (68+4 cache); SESSION 25; pilot 196; comparer selftest 14; guard 18; supplemental 4 exact; lock 214; extra/changed source refusals pre-import (3 source refusals total with prebuild) |
| Board validate / render --check / docs / diff --check (worktree, unit range, D3) | 36 tasks OK; current; 933 md OK; all clean |
| Normative pins | 30 rows: 29 exact + CMD-F05 b8021069→9bc9ecd1 (exact approved old/new row; recorded in authority + evidence); dirty examples match pins |

My first MEMQ installed attempt (4 runs) failed. I had set `REVIEW_SCRATCH` to the prepared dir, so the probe correctly refused ("Report must be in private scratch"). That attempt is a reviewer setup error and earns zero credit. It is preserved under `attempt1-setup-error/`; all 8 runs were then redone fresh.

## Inspected, not executed
- The builder's scratch, receipts, maps and control drivers: hashed, then reconstructed. They were never run in place.
- The retained D2 mutant reports (20 + unchanged control). I classified them independently: all 20 have a terminal call-phase `AssertionError` in a named test, and each differs from current source only in its declared module. The control exits 0 and its 59 origin modules hash-equal current source. All 1,239 origin files are present; 3,318 origin records were checked with 0 disk mismatches. I did not regenerate them, because runtime and tests are byte-identical since D2.
- The D0 baseline closed trial (report `7a6298ba…`), used only for the 27/127 comparison.
- The D1 neutral mutant controls were not re-examined. They are covered by verified D1.

## MD3 matrix
| ID | Result | Evidence |
| --- | --- | --- |
| MD3-01 | PASS | D3 delta is docs and evidence only (12 paths); there is no source/test change since 3ed1d58a. The aggregate's 17 product paths are all in the allowlist, with no dependency, lock, framework or ingest change. |
| MD3-02 | PASS | AST audit; 101 + 52 named cases pass; API54 bindings; union 18. |
| MD3-03 | PASS | Probe bytes equal the e4c0b9a2 export; 4 retained bodies are exact; no `__all__` assignment; patches only substitute test seams. |
| MD3-04 | PASS | My own build and replay: 154 equal, 27/127, neutral 1, Chat 138, pip checks pass, prebuild refusal. |
| MD3-05 | PASS | My own 8 probes, with full inventories and origins, parent and entry-child, isolated (no PYTHONPATH). |
| MD3-06 | PASS | Installed report sections, plus 6 MEMQ semantic refusals. |
| MD3-07 | PASS | Installed persisted listing in both modes; TypeError reproduced as unwaived; ingest source unchanged. |
| MD3-08 | PASS | 50 + 10 + 10 + 3 refusals and 8 clean copies, all reproduced by me; 20 mutants classified. |
| MD3-09 | PASS | Fresh counts as tabled above; root 534 / 7082 collision remains failed and unwaived, with no lost collection. |
| MD3-10 | PASS | 720 pairs honest, and failed development attempts are labelled separately. |
| MD3-11 | PASS | Gates agree; log is append-only; only the 6 PAR rows and header change; CMD-F05 is the single permitted cell; 29 exact pins; UAT NOT RUN. |
| MD3-12 | PASS | Start and end boundaries are identical; I wrote only to my own scratch. |

## MQ-T matrix
| ID | Result | Evidence |
| --- | --- | --- |
| T01–T06 (neutral) | PASS | 24/1/6/66/1/3 nodes pass. T06 runs normal, -O and -OO. |
| T07–T13 (Chat) | PASS | 1/6/6/15/9/8/1 nodes pass. |
| T14 option R | PASS | 6 nodes pass, and the installed persisted proof matches. |

Mutation backing: 20 D2 mutants carry real CALL `AssertionError`s, and D1 mutants are covered by the verified D1 council.

## Debt and residual limits
- **Baseline debt (failed, unwaived, unchanged):**
  - Root Ruff: 534.
  - `test_display` collision: 7,082 = 6,929 + 153.
  - Raw format failures in 4 files.
  - No-description ingest `TypeError` (FU-009 / UAT workaround).
- **New regressions:** none found.
- **Residual limits:**
  - The ignored listing is compared at `--directory` granularity.
  - `.venv` is not byte-audited (uv `--no-sync`; the ephemeral env lives in my UV cache).
  - Human UAT20 is NOT RUN.
  - D1 mutants were not re-examined.

## Isolation
- One scratch, all writes inside it: `memq-d3-claude-r1.inlr71`.
- No source, doc, board or index changes. No checkout or worktree, no cleanup, no delegation, no network or providers, no real stores.
- Host-managed transcripts and tool-result files were written by the harness under `~/.claude/projects/...`. These are disclosed separately.

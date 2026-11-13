# INGEST-PACKAGE-IMPACT-001 — Round 4/4 independent read-only review (Opus seat)

**Verdict: CHANGES_REQUESTED**

Candidate `56a495b76e7b7f8a967633bf523dfa9c30f9ed73` on `feature/cmd-ingest-001`; correction delta reviewed from
`c96ecbea685a2627e033d3a9cb62a2f05b72afb7`. Request SHA256 `b9b11c7c95c7fe0f6c30c66e665597aa54456b04d6cd81675ce5d9877d085601`
was verified before reading. This review covers document readiness and source feasibility only. It grants no maintainer
impact satisfaction, Gate-A activation, construction, acceptance or delivery authority.

## Integrity

| Check | Result |
| --- | --- |
| Request hash (before read) | match |
| Helper pins: read_only_command.py `3acff26f…`, verify_identity.py `c4d9bf96…`, current-controls.json `9a6de4dc…`, protected-manifest `8efe9b8f…` | all match |
| Opening `verify_identity.py` (opening.json) | PASS, logical index `2b13729a…093d0f`, 17,730 protected files, 6 preserved items, errors [] |
| Closing `verify_identity.py` (closing.json) | PASS, same logical index, errors [] |
| REM at base `8390f368` | SHA256 `e1c90753…2a16`, matching the assessment's conditional-approval hash (reproduced) |
| Annex and Tools companion, base..candidate | empty diff (reproduced) |
| `packages`, `uv.lock`, `pyproject.toml`, `tests`, `docs/guides`, `docs/architecture`, base..candidate | empty diff (reproduced) |
| execution-log.md | bytes at `8390f368` and `c96ecbea` are byte prefixes of current (append-only, content not displayed) |

## Commands and exits (all reproduced)

| Command (via pinned wrapper, own scratch) | Exit | Output tail |
| --- | --- | --- |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 | Development board validation passed: 36 tasks |
| `… scripts/friday-dev-board.py render --check` | 0 | Planning dashboard is current |
| `… scripts/check-documentation-lifecycle.py` | 0 | 1037 Markdown files checked |
| `… scripts/check-package-metadata.py` | 0 | Validated 18 pyproject.toml files (root + 17) |
| `git diff --check 8390f368..56a495b7 -- docs/planning` | 0 | (none) |
| `git diff [--stat] c96ecbea..56a495b7 --` the five review_diff_paths | 0 | 5 files, +99/−28 |
| `git show <c>:REM` piped to shasum at three commits; `git log` REM; `git ls-files` transcript/finance/optimization | 0 | as reported |

## Procedural disclosures

1. Four wrapper invocations were refused before execution with "Command is outside this document-review profile" because zsh did not word-split the argv. They were rerun with explicit argv and exited 0, as shown above.
2. Two read-only Git calls (`git ls-files packages/friday-tui`, `git check-ignore`) ran directly, not through the wrapper. Neither writes the index. The closing logical-index hash is unchanged.
3. A grep for stale round/version strings covered raw README.md, next-phase.md, tactical-plan.md and gate-a-handoff.md as well as the five documents. It printed lines containing historical verdict labels for other units (MEMQ D2/D3, MAINT round 3, pilot) and a link label to the INGEST assessment-v0.2 verified report. It showed no raw peer report content and no prior-round or current-round INGEST-PACKAGE-IMPACT peer verdict. In my judgement this is outside the forbidden raw-peer-report/current-peer-verdict category, but I disclose it for the controller's decision.
4. No product or test imports or execution, installs, model/store operations or repository writes took place. Source and tests were inspected as text and AST only. All outputs are in the reviewer's scratch outside the checkout.

## Correction delta

- **PC-05: met.** Assessment lines 13–18 qualify the old approval by the exact hash `e1c90753…`, which I reproduced as the REM at `8390f368`. Lines 264–268 require the final directive to bind the amended REM and the final assessment. The annex and companion are byte-unchanged. No "frozen REM" claim remains in the five documents.
- **PC-06: met.** REM G1 (lines ~1331–1340) and the test-plan reconciliation section treat only case-level entries explicitly incorporated into the final directive as the annex's "named final-directive fixture/oracle exceptions". Annex final paragraph: "Keep old public signatures/classes and assertion bodies except the named final-directive fixture/oracle exceptions." Unmapped body edits stay prohibited, public signatures and classes stay, and named FC nodes stay unless an approved equivalent is mapped with executed coverage.
- **PC-07: met.** Source confirms the three registries: `friday_cli/commands.py:74` `CommandRegistry` and `:496` `arg`, both exported in `friday_cli/__init__.py`; `friday_chat/commands/registry.py:89`; `friday_commands/registry.py:41`. `friday_chat/app.py` uses the Chat registry, and Chat imports only display/config helpers from `friday_cli`. CLI `repl.py`, `main.py` and `server/api.py` are 5-line docstring placeholders. The architecture plan item 2, REM G2 and the guide handoff CLI README sentence all carry this distinction.
- **Runtime DI and Memory anchors: met.** `tests_runtime/test_di.py` and all 14 named Memory test files exist, along with `test_lifecycle/`.
- **Eight package READMEs: met.** All eight exist and are named in the guide handoff and in the REM path rows.
- **Executive summary and feature catalogue: met.** Exec summary line 62 says model changes "can require rebuilding compatible collections". FRIDAY-FEATURES line 23 calls `friday` a "Declared placeholder entry point", but no package declares `friday` (only `friday-chat` and `friday-finance-demo`). The new handoff row covers both claims.
- **Membership-derived 17: met.** Root `members = ["packages/*"]`, and 17 directories carry `pyproject.toml`. `packages/friday-tui` holds only untracked caches/`__pycache__` and has no pyproject.
- **Conditional test-only consumer paths: NOT met.** See finding 1.

## Mandatory findings

### 1. [Medium] The REM's conditional test-only allowlist names nonexistent consumer test directories

- **Requirement:** PI-17, PI-02 and correction disposition OPUS-A02 ("Name conditional test-only consumer suites … in REM paths"). The final directive must bind exact allowed paths.
- **Affected text:** REM "Proposed exact implementation paths" row: "conditional `tests_telemetry`, `tests_transcript`, `tests_mcp`, `tests_optimization`, `tests_finance`, `tests_speech`, `tests_sandbox`, `tests_moltbook` in their matching packages". The test-migration-plan paragraph "The REM's test-only allowlist covers the P-10–17 consumer suites…" repeats it.
- **Source evidence:**
  - Friday Transcript's tracked suite is `packages/friday-transcript/tests/`, which includes `test_mcp_provenance.py`, `test_models.py` and `test_sqlite_snapshot.py`. These are exactly the receipt/v1 suites P-11 says to "retain/adapt … in the owning suites".
  - Friday Finance's suite is `packages/friday-finance/tests/` (`test_basics.py`, `test_integration_massive.py`).
  - `packages/friday-optimization` has no test directory at all.
  - Root `testpaths = ["packages/*/tests_*", …]` does not collect either `tests/` directory.
  - The other five named directories do exist.
- **Risk:** A directive copying this allowlist would fail to authorize the real Transcript owning suite if a receipt or strict-version witness is needed there, forcing a stop or reconcile. It could also be read as permission to create parallel `tests_transcript/` or `tests_finance/` trees, which the root config would collect while the existing suites are not. Either outcome splits coverage and makes the migration map's old-to-new paths wrong. P-13 has no baseline suite to "retain".
- **Bounded fix:** In the REM row, replace the three names with `packages/friday-transcript/tests/` and `packages/friday-finance/tests/`. For Optimization, state that no existing suite exists and that any justified witness location (new package-local `tests_optimization/` or a root integration test) must be named in the directive. Mirror this in the test-migration-plan paragraph and P-11/P-13/P-14 rows. Note that the two `tests/` suites need explicit run selectors because root testpaths do not collect them.
- **Recheck:** Every conditional path in the REM row exists in `git ls-files`, or is explicitly marked as new. The test plan agrees.

### 2. [Low] The amended REM contradicts itself about the current version and round

- **Requirement:** PI-16 (links/current-state consistency) and PI-14 (single canonical bound version).
- **Affected text:** REM "Next decision" (lines 1403–1405) reads: "Review the revised assessment v0.3 … Fresh round 3 of the standing four-round cap reviews the amendment delta first…". The REM header (lines 22–26) correctly says v0.4 and round 4 is final.
- **Source evidence:** `grep` of the REM at candidate. The correction diff updated the header but not "Next decision".
- **Risk:** The REM bytes are to be bound into the final directive. A stale normative "next decision" naming the superseded assessment version and round could mislead about which assessment is under review or bound.
- **Bounded fix:** Rewrite "Next decision" to name assessment v0.4, round 4 as the final round, and the stop-for-guidance outcome, matching the header. Do not change other text.
- **Recheck:** `grep -n 'v0\.3\|round 3' REM` returns no current-state hits.

### 3. [Low] A current authority field is stale against the current gate

- **Requirement:** PI-16.
- **Affected text:** Safe current-controls snapshot, authority `current_scope`: "Package Impact Assessment v0.3 and amended REM: fresh council round3/4 … Two rounds already used". In the same snapshot, `next_gate`, `package_impact_assessment.version` ("0.4-draft") and `council.round` (4, completed 3) disagree with it.
- **Source evidence:** current-controls.json (`9a6de4dc…`). The raw authority was hash-verified only.
- **Risk:** Current routing gives two incompatible statements of the round, version and consumed budget at the final round, where stop-for-guidance depends on that count.
- **Bounded fix:** Update `current_scope` to v0.4, round 4/4 final, three rounds consumed, consistent with `next_gate`. Also check `conditional_maintainer_approval.current_authorization` for the same drift.
- **Recheck:** A safe snapshot shows all current fields agree.

## Advisories (non-blocking)

- **A-1:** The assessment says "the eight implementation rows also name their scoped package README updates". However, P-02's change type says "setup documentation" and P-06's says "user documentation", not README. The REM path rows do name both READMEs. Align the wording for readability.
- **A-2:** The handoff should name FRIDAY-FEATURES line 23's specific stale "`friday` … Declared placeholder entry point" claim. No CLI declaration exists, and AGENTS.md says it was removed.
- **A-3:** The architecture plan's "actual callers" requirement should note that the CLI component registry's present callers are CLI tests and legacy `tests/integration/memory` code. This avoids implying a maintained-app caller.

## PI-01–18 matrix

| ID | Result | Basis |
| --- | --- | --- |
| PI-01 | Met | 17 rows matching 17 pyproject-bearing members; 8 implementation (CLI conditional) plus 9 source-unchanged; tests and inheritance not treated as no impact. |
| PI-02 | Partially met | Rows trace to REM/annex/companion paths. The conditional test-path allowlist is inaccurate (finding 1). |
| PI-03 | Met | Ownership is consistent with source. Commands is stdlib-only with 54 `__all__` entries (AST) and `dependencies = []`. Dependency edges match pyprojects. |
| PI-04 | Met | INGEST and TOOLS-DOC are separated in the P-02 row, the basis section and the readiness table. |
| PI-05 | Met | Chat default via Tools extra, Certifi floor, LLM `embedding-limits` via Memory, inheritance by Runtime/CLI/Agent/MCP-full/Optimization (verified in pyprojects), lazy neutrality, unresolved versions. |
| PI-06 | Met | Pool/non-pool preservation, missing-field readiness, hosted-baseline uncertainty, no Qwen activation, baseline/replacement positives separate from refusals. |
| PI-07 | Met | Identity sidecar, same-dimension refusal, explicit fresh paths, `/read` availability, graph/recovery and strict v2 handoff, no reset or migration. |
| PI-08 | Met | document/512 defaults with overrides. The Chat 2,048-character slicer (adapters.py:385, 2793) is verified. Unsplit structured records, no URL or automatic route. |
| PI-09 | Met | Agent, multi-agent, metadata, telemetry, transcript and MCP consumers are owned correctly, with no transport or schema expansion. |
| PI-10 | Met | Memory is broadest. Admission before side effects, task/sink ownership, profile isolation, truthful counts, explicit `persist_directory`/`chroma_path`/`runtime_data_root` origin (verified in config). CLI conditional, no launcher. |
| PI-11 | Met | MCP and backups are causal consumers. Live-marker protection, FU-013/014 unwaived with no credit. |
| PI-12 | Met | Future source/integration/installed evidence is clearly distinguished from completed work, with no conformance promise. |
| PI-13 | Met | Readiness table exposes versions, assets, licenses, limits, signatures and path coverage as stop conditions. |
| PI-14 | Met, with finding 2 | Old-hash qualification, binding of exact version/commit/SHA256, renewed review for material change. The stale REM "Next decision" undermines single-version clarity. |
| PI-15 | Met | Concrete per-row upgrade, purpose, change type, retained behavior and evidence; no effort metrics. |
| PI-16 | Not met | Identities, links (0 broken), append-only log and preserved state all verified, but current-state round/version statements conflict (findings 2 and 3). |
| PI-17 | Not met | Restructuring permission, annex reconciliation, map and DI-35 are strong. The conditional consumer allowlist misnames real owning suites (finding 1). |
| PI-18 | Met | Canonical architecture, three-registry/placeholder distinction, 8 READMEs, guide rows including exec summary/features, source/example/independent-review acceptance. |

## Rubrics (independent, not averaged, not target-inflated)

**Coverage: 9.4 / 10**

| Area | Score |
| --- | --- |
| Inventory and classification | 2.7 / 3.0 (test-path inaccuracy) |
| Behavior, configuration and data | 2.0 / 2.0 |
| Ownership and deployment | 1.95 / 2.0 |
| Boundaries and proofs | 1.8 / 2.0 |
| Readiness and approval | 0.95 / 1.0 |

**Overall: 9.4 / 10**

| Area | Score |
| --- | --- |
| Accuracy | 2.7 / 3.0 |
| Architecture and delivery | 1.95 / 2.0 |
| Data, configuration and dependency safety | 2.0 / 2.0 |
| Evidence and reproducibility | 1.4 / 1.5 |
| Readability and change control | 1.35 / 1.5 |

The gate is not met: there are 3 mandatory findings and both scores are below 9.5. Under the request's protocol this is the final authorized round, so the outcome returns to the maintainer for guidance. All three fixes are bounded document corrections with no change to technical scope.

## Reproduced vs inspected, and limits

- **Reproduced:** hashes, identity checks, five administrative commands, diffs, REM hash lineage, log prefix, link resolution, AST API count, path existence and `git ls-files`.
- **Inspected only:** prose consistency, and source/test semantics read as text.
- **Not done:** no product or test execution, and no model, installed or format proof. These are future obligations, not current gaps.
- **Not re-run:** baseline debt (Ruff, root `test_display` collision, MAINT oracles) remains unwaived and was not rerun.

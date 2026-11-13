# REM-CMD-INGEST-001 + TOOLS-DOC-001 — Round 4 design council, seat OPUS

- Seat: **opus** (Anthropic, `claude-opus-5-5`, high effort), fresh context, read-only.
- Candidate `728cba77e816e5618a06262dd4aa1cbc6e50a376` on `feature/cmd-ingest-001`; correction base `36362be514ef387183a27d930cd41a8799e3d714`.
- Request SHA256 `0601d7c1f2db634e6efe20fd96aa38ea80539e129fdb0e1ecab3d5afe18c7c1c`. Helper and wrapper hashes verified before use (`080be4f9…a9d368`, `cb0669f8…fea248`).
- Own scratch: `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/2f8adb48-0c44-4d04-a526-6d83535fbb2c/scratchpad/opus-r4-review/`.

## Outcome

**VERIFIED. Score 9.5/10. Mandatory findings: 0. Advisory findings: 6 (OPUS-R4-A01..A06).**

The correction delta closes both round-3 mandatory requirements (IR-F01 and IR-F02) at design level, and source inspection shows they can be built. The full REM and companion are coherent, bounded and ready for Gate A and drafting of the final directive. The advisories below are narrow refinements. Each concerns a fail-closed or operational edge case, not an unsafe or contradictory design. This verdict grants no construction, Gate-A, acceptance or delivery authority.

## Rubric (honest, advisory)

| Dimension | Weight | Score | Basis |
| --- | --- | --- | --- |
| Scope, authority and boundedness | 1.5 | 1.45 | Board, authority, roster and iteration records agree (started, `design_only`, branch match, REM SHA = authority pin `61d93548…`). Non-goals and stop conditions are explicit. Minor: the prose is very dense in places, with an unreflowed line at REM:179. |
| Shared architecture and integration | 2.0 | 1.90 | The Core/Memory/Tools/LLM boundaries, v1/v2 dispatch and fingerprint separation are source-feasible. Residual: participant-fingerprint timing (A01), shared recovery root (A02), Runtime specifics for the trace table (A04). |
| Format extraction and coverage | 2.0 | 1.90 | The four-format contract, structural audit and fail-closed coverage are strong. Selected-release proof is correctly deferred to Gate A. |
| Chunking, embedding and data safety | 3.0 | 2.85 | Overflow, role and identity admission, the root-state matrix and no-fall-through rules are sound. Residual: the logical vector artifact version is not named in the closed table (A03). |
| Verification, reproducibility and reporting | 1.5 | 1.40 | DI-01..32 and TD-01..10 are meaningful and include mutants. A01–A03 edge cases are not yet named as test rows. |
| **Total** | 10 | **9.50** | |

## Correction delta first (36362be5..728cba77, technical paths only)

The REM gains about 128 changed lines and the companion only a status line. The policy record, correction brief, roster and iteration authorization are unchanged or new records. Sections added or changed:

- **Core lazy-edge inventory** (REM:175-179). It accurately inventories the existing Core imports: `profiles.py:75,80,108,113` and `interfaces/transcript.py:249-251,319-321`.
- **Gate A trace table** (REM:229-233). It consolidates existing obligations and adds no new experiment.
- **Inert service objects permitted, zero resourceful init** (REM:843-848; DI-29).
- **Exact normalized-directory direct clients, no fall-through** (REM:860-864; DI-28). This matches the actual `[memory_dir, memory_dir/vector]` probes at `pruner.py:110`, `synthesizer.py:179` and `fact_checker.py:136`.
- **Versioned Memory-to-Chat recovery handoff** (REM:904-948; path table row REM:1122; DI-32).
- **Explicit-origin CREATE_FRESH, graph/WAL preconditions, Runtime container reuse** (REM:1003-1039; matrix REM:1061-1071; DI-29).
- **Operator upgrade note** (REM:1087-1095).

## Prior requirement disposition (independently assessed)

| Requirement | Disposition | Evidence |
| --- | --- | --- |
| INGEST-R3-ASTRA-001 (IR-F01) | **Closed at design level** | See the IR-F01 analysis below. |
| Opus M-1 (IR-F02) | **Closed at design level** | See the IR-F02 analysis below. |
| SOL-R3-A01 | Addressed | REM:229-233 |
| Opus A-1 | Addressed | REM:175-179, path row REM:1101 |
| Opus A-2 | Addressed | REM:860-864, DI-28 namespace-fallback mutant |
| Opus A-3 | Addressed | REM:1033-1039 discloses the transcript/artifact relocation |
| Opus A-4 | Addressed | REM:843-848, DI-29 |
| Opus A-5 | Addressed | Matrix rows REM:1065/1067 and REM:1069-1071 are disjoint, with no history scan |
| Opus A-6 | Addressed; small residual in A06 | REM:1087-1095 |

### IR-F01 analysis (strict v1/v2 models, loaders, consumers, exports, fingerprints)

**Source facts:**

- `MemorySnapshotManifest.schema_version: Literal[1]` (`recovery_models.py:289-302`).
- `RecoveryBundleManifest.schema_version: Literal[1]` embeds `memory: MemorySnapshotManifest` and checks `participant_layout_fingerprint == memory.layout_fingerprint` (`contracts.py:417-470`).
- `AtomicJsonStore.read_model(path, model_type: type[ModelT])` validates through the supplied model type, and `write_model` round-trips through `type(model)` (`durability.py:198-220, 314`). A strict Pydantic discriminated envelope (a RootModel over `Literal[1]`/`Literal[2]` members) therefore fits without `Any`, casts or a generic store change. The REM's claim holds.
- The full consumer inventory (rg across packages, tests and scripts) is exactly `recovery_models.py`, `recovery.py`, the Memory maintenance and root `__init__`, Chat `contracts.py`, `artifacts.py`, `coordinator.py`, the reorganization and root `__init__`, plus the two test modules. This equals the new allowlist row at REM:1122 together with the existing `recovery.py` row. No unlisted consumer exists.
- Fingerprints are distinct:
  - Chat `FridayChatMaintenanceLayout._fingerprint_for` is a path-only v1 digest, used by leases (`lease.py:161-266`) and journals (`artifacts.py:230-236`).
  - Memory `MemoryRecoveryParticipant._fingerprint_layout` is a separate path digest (`recovery.py:218-231`).

  The REM keeps the Chat digest unchanged and moves only the Memory participant digest to v2 with binding and incarnation. This is coherent. Incarnation-sensitive protection for a path-reused namespace comes from the independent participant check, so leases and journals need no schema change.
- `_SnapshotEvidence.bundle` (`coordinator.py:365`), `_create_verified_bundle`, `_read_bound_bundle` and `_verify_bundle_participants` (`artifacts.py:195-228`) are exactly the seams the REM names. The no-v1-fallback-after-v2-failure rule and the closed dispatch can both be enforced there.

**Verdict:** coherent and buildable. Residual items: A01 (when the fingerprint is computed) and A03 (version of the nested logical artifact).

### IR-F02 analysis (explicit origin, graph/WAL, Runtime container)

**Source facts:**

- Chat: `memory.persist_directory: str | None = None` (`config.py:477`) with fallback `".friday/vector"` (`assembly.py:26`). Origin is therefore directly observable: `None` means unset.
- Chat: graph is `vector.with_name("graph.json")`. WAL comes only from configured `lifecycle.access_buffer.wal_path`. Recovery and log roots default under `vector_parent` (`assembly.py:26-53`). The REM's sibling-graph and configured-WAL rules match.
- Runtime: `from_sources` deep-merges defaults first, with `chroma_path` defaulting to `.friday/chroma` (`config.py:1239, 1365`). Raw origin must therefore be captured from YAML, `FRIDAY_CHROMA_PATH` and flat overrides before the merge (`config.py:1486, 1970`). The REM's requirements to "preserve the raw-key-origin bit before defaults/merging" and not to compare the resolved string against the default are exactly what this needs, and they are feasible.
- Runtime: graph is `runtime_data_root/memory/graph.json` via `resolve_runtime_state_path`. `runtime_data_root` defaults to `~/.friday/runtime` (`config.py:2179`), while `chroma_path` is cwd-relative. This confirms the REM's statement that the container is not the namespace.
- The packaged Chat template sets `persist_directory: .friday/vector` explicitly (`config_templates/config.example.yaml:236`). It is not auto-loaded, so a user who copies it has supplied an explicit value. This is consistent with the REM's "explicit value equal to default qualifies" rule; see A05.

**Verdict:** the rules are exact, disjoint and source-consistent. The matrix rows are mutually exclusive, the race and recheck rule is sound, and no automatic cleanup or adoption of existing paths is allowed.

## All 30 criteria

| ID | Result | Note |
| --- | --- | --- |
| IR-01 | PASS | Authority, branch, `design_only` and proposal-vs-construction separation are consistent across REM:13-21, the board (task `friday-command-refactor`) and authority.json current fields. |
| IR-02 | PASS | Allowlist before Docling, full conversion before Memory, refusal of partial/empty/diagnostic content (REM:330-361). |
| IR-03 | PASS | PDF order/OCR/page count, DOCX interleaving, declared omissions (REM:342-350, 371-374). |
| IR-04 | PASS | Visible-only scope, saved cache with missing/error refusal, merged/type rules, no recalculation or preview caps (REM:375-389, 400-407). |
| IR-05 | PASS | Slides, notes, hidden content, tables and declared omissions; no media fetch (REM:376, 391-398). |
| IR-06 | PASS | Raw-tail parsing for default file handlers only; `_parse_command_input` (`registry.py:1196`) unchanged; API54 preserved (REM:438-471). |
| IR-07 | PASS | document/512 for all sources, precedence, three strategies, budget includes overhead, overlap frozen at Gate A (REM:505-604). |
| IR-08 | PASS | Typed boundaries, no new cycles, existing edges inventoried, no double chunking (REM:92-114, 171-181, 587-595). |
| IR-09 | PASS | Optional catalog fields, verified identity, min-capacity rule; Qwen illustrative (REM:606-692, 716-723). |
| IR-10 | PASS | Roles, overhead, cardinality/index/dimension/finite checks, no truncation (REM:694-747). Matches the source: `graph_scorer.py:133,140` uses `embed_query`, `collection_manager.py:559+` uses `embed_documents`. |
| IR-11 | PASS | Certifi floor declared, locked and post-install verified with a negative control; offline assets; Gate-A effects envelope (REM:183-309). |
| IR-12 | PASS | Archive/cell/page bounds, encrypted/corrupt refusal, cancellation/quiescence, no OS-sandbox claim (REM:409-425, 950-969). |
| IR-13 | PASS | Route table and smart_read storage/cache provenance; companion split (REM:121-169; companion). |
| IR-14 | PASS | DI-01..32 and TD-01..10 include genuine fixtures, mutants, installed lanes and oracle preservation (REM:1145-1192). |
| IR-15 | PASS | Fresh stores, no hidden migration, recorded policy, future PR base `master` (REM:816-823, 976-1001). |
| IR-16 | PASS | Gate A is bounded with explicit stop conditions (REM:218-220, 248-269, 404-407, 965-968). |
| IR-R01 | PASS | Core entry and headless factory, raw-vs-derived records, no import cycle (REM:105-114, 138-153). |
| IR-R02 | PASS | One sidecar authority, exclusive pending→ready marker, same-dimension mismatch refusal, envelopes, no reembedding (REM:749-801). |
| IR-R03 | PASS | All embedding caller roles enumerated; no asymmetric enable while a caller is unclassified (REM:704-714, A.6). |
| IR-R04 | PASS | Optional parsing vs operation-time requirement; typed refusal; non-pool paths (REM:616-626). |
| IR-R05 | PASS | Memory text segmenter is not a fallback; missing extra affects only the four formats (REM:552, 567-576). |
| IR-R06 | PASS | Synchronous offline counter, asset root, server cross-check, worker-thread rules (REM:630-637, 262-269, 950-958). |
| IR-R07 | PASS | Text-free structural audit, mapping or refusal; Docling is the sole text supplier (REM:409-425). |
| IR-R08 | PASS | Truthful route classification; no new fetcher or automatic ingestion (REM:121-136). |
| IR-S01 | PASS | Matches the recorded maintainer answer; request mechanism, matrix, read-only startup, no legacy fallback (REM:976-1085; policy record). |
| IR-S02 | PASS | Narrow v2 snapshot binding, same-namespace restore, offline-only identity-free v1, direct-client admission (REM:855-902). |
| IR-S03 | PASS | RuntimeKernel/Core/CLI classification, lazy gates, hosted immutable identity, unknown graph-vector failure (REM:825-853, 639-649). |
| IR-S04 | PASS | Destination/incarnation receipts, unwired smart_read honesty, plain CSV limitation, inactive migration, exact flags (REM:162-169, 578-585; DI-30/31). |
| IR-F01 | PASS | See analysis. Advisories A01 and A03. |
| IR-F02 | PASS | See analysis. Advisories A02, A04 and A05. |

## Findings

**Mandatory: none.**

**Advisory** (each is a narrow, document-only refinement; none blocks Gate A):

- **OPUS-R4-A01 — When the v2 participant fingerprint is computed** (IR-F01, IR-S02; `recovery.py:209` computes `_layout_fingerprint` in `__init__` and binds it into `MemoryQuiescenceToken`, `recovery.py:105-125, 289`).
  - Issue: a v2 digest that includes sidecar binding and incarnation cannot be fixed at participant construction if the participant is assembled before the first lazy CREATE_FRESH.
  - Mitigation: state in the directive that the v2 participant fingerprint is derived from the admitted ready binding at operation/admission time, or that participants are constructed only after admission. Say how tokens relate to the digest.
  - Test: add a DI-27/32 case for a participant created before first fresh creation, then snapshot and rollback. The expected result is a correct digest, or a typed refusal rather than a stale-digest mismatch.
- **OPUS-R4-A02 — Shared explicit recovery or log root after a fresh selection** (IR-F02, IR-15; `assembly.py:39-45`, `coordinator.py:1757-1782`, `artifacts.py:230-236`).
  - Issue: if `maintenance.backup_directory` or `logging.log_directory` is explicitly configured and reused, old-layout journals make `_unfinished_journals` fail closed ("recovery root contains unverifiable run evidence"). Maintenance stays blocked until the user acts.
  - This is safe but undocumented. Mitigation: in the request-mechanism text and the startup diagnostic, tell users to select new recovery and log roots with the fresh state (or note that the defaults move with `vector_parent`).
  - Test: add a DI-29 row for a reused explicit recovery root that contains an old journal. Expected: actionable refusal with old artifacts untouched.
- **OPUS-R4-A03 — Name the nested Memory artifact versions in the closed table** (IR-F01, IR-R02; `ChromaLogicalSnapshot.schema_version: Literal[1]`, `recovery_models.py:217-224`).
  - Mitigation: extend the compatibility table (or its directive freeze) so a Memory v2 manifest accepts only an identity-bearing v2 logical vector artifact and identity-enveloped graph artifact. A v1 logical artifact referenced from a v2 manifest refuses.
  - Test: add a mixed-artifact mutant to DI-32.
- **OPUS-R4-A04 — Runtime specifics for the Gate A trace table** (IR-F02, IR-S03).
  - `di.py:248-249` eagerly calls `graph_storage_path.parent.mkdir(...)`, and the transcript parent is created at `di.py:265` during storage assembly. These are associated-path creation effects that must move behind the lazy gate in the unset or refused rows.
  - Runtime has no configured access-WAL setting today, so its WAL precondition is vacuous.
  - The default `runtime_data_root` (`~/.friday/runtime`) is home-level while `chroma_path` is cwd-relative, so a typical upgrade hits the existing-graph refusal unless `runtime_data_root` also changes. The diagnostic should name both settings.
  - Test: DI-29 asserts no mkdir under `runtime_data_root` in the refusal rows.
- **OPUS-R4-A05 — Packaged template origin** (IR-F02, IR-S01; `config_templates/config.example.yaml:236` sets `persist_directory: .friday/vector`).
  - Copying the template grants explicit origin. This is consistent with the stated rule, but the directive should decide whether the new template keeps that literal, comments it, or uses an obviously new path. It should also confirm the diagnostic for a legacy user who copied it, which lands in the unbound-refusal row.
  - Test: config test on the packaged template.
- **OPUS-R4-A06 — Upgrade note completeness** (IR-15; REM:1087-1095).
  - Mitigation: add a step to resolve or complete any unfinished or RECOVERY_REQUIRED maintenance journal with the old release before upgrading, because new tooling refuses v1 bound restore.
  - Cosmetic: reflow REM:179.

## Checks executed (all through the verified wrapper; exits from the audit log)

| Check | Command | Exit | Result |
| --- | --- | --- | --- |
| integrity-start | wrapper → `python3 -B check_integrity.py review-request.json` > start-integrity.json | 0 | PASS: 17606 protected entries, HEAD/branch/index match, no failures |
| board | wrapper → `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 | "Development board validation passed: 36 tasks" |
| dashboard | same uv prefix, `render --check` | 0 | "Planning dashboard is current" |
| docs | same uv prefix, `scripts/check-documentation-lifecycle.py` | 0 | "991 Markdown files checked" |
| metadata | same uv prefix, `scripts/check-package-metadata.py` | 0 | "Validated 18 pyproject.toml files" |
| whitespace | wrapper → `git diff --check 36362be5..728cba77` | 0 | No output |
| delta | wrapper → `git diff` and `git diff --stat` 36362be5..728cba77 filtered to REM/companion/policy paths | 0/0 | 2 files changed, +128/−14 |
| integrity-end | wrapper → same helper > end-integrity.json | 0 | PASS: identical identity, no failures |

All nine wrapped invocations are recorded with `GIT_OPTIONAL_LOCKS=0` and `PYTHONDONTWRITEBYTECODE=1`.

**Disclosed non-execution:** my first attempt at the admin batch passed a composed command string to zsh, which did not word-split it. The shell reported "no such file or directory" (exit 127) for the whole string. No wrapper, Git or uv process was spawned, and nothing was logged. The batch was then re-run correctly through the wrapper as shown above. This is not an unwrapped invocation.

## Evidence classes

- **Reproduced:** the eight required checks above.
- **Inspected statically (plain read-only `sed`/`rg`/`cat`/Python `-B` reads, no wrapper, no Git or admin):**
  - REM (full, 1226 lines), companion (full), policy record, correction brief, roster, iteration authorization.
  - authority.json current fields only (`branch`, `current_scope`, `product_code_authority`, `active_council_roster`, `document_ingestion_remediation`), and the board task entry and event titles.
  - Source: `recovery_models.py`, `recovery.py` (fingerprint/constructor), Chat `contracts.py`, `artifacts.py`, `coordinator.py`, `layout.py`, `assembly.py`, `durability.py`, `config.py:477`, packaged template line 236, Runtime `config.py` (`from_sources`, defaults, path resolvers), `di.py:245-300`, Core `profiles.py`, `interfaces/transcript.py`, `interfaces/memory.py`, the Chroma openers in pruner/synthesizer/fact_checker/mutation/recovery/vector, embedding role call sites, and `registry.py:1196`.
  - SHA256 of REM and policy recomputed (they match the authority pins).
- **Public sources:** none newly fetched. Upstream links in the REM were not re-verified this round and are treated as design references only.
- **Not performed:** product imports, tests, builds, installs, model or provider calls, store reads, peer reports, raw historical council reports, unfiltered aggregate diff, and personal state (`.friday-old`, exports, dirty YAML), apart from protected hashing and stat by the immutable helper.

## Private-output and command-category audit

- **Outputs:** every generated file is in my own scratch: start/end integrity, `chk-*.txt`, `delta-technical.diff`, `command-audit.jsonl`, and the wrapper-created `tmp/` and `uv-cache/` directories. No writes to the repository, the supplied inputs or any prior scratch.
- **Command categories:**
  - (a) Wrapped Git/admin: 9 invocations.
  - (b) Unwrapped plain static reads of permitted source, docs and inputs: `sed`, `rg`, `cat`, `ls` of the supplied inputs directory, and Python `-B` JSON/hash reads.
  - (c) Own-scratch reads and writes.
- No bare Git, no product-module import, no nested agents, no retries of the review.
- Isolation violations: none observed. End integrity matches start.

## Baseline limits (acknowledged, not evaluated as failures)

- Gate A Docling, dependency, OCR, counter and model readiness is intentionally pending; no installed behavior is claimed.
- Current `/ingest` character slicing, missing guards and placeholder reading are pre-remediation gaps.
- Historical root Ruff (534), the root `test_display` collection conflict, the seven legacy format failures and MAINT Chat 1413/15 are unwaived background and were not rerun.
- MAINT UAT/acceptance and the broader refactor remain separate. The PR 15 merge grants no INGEST construction authority.

## Report

Path: `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/2f8adb48-0c44-4d04-a526-6d83535fbb2c/scratchpad/opus-r4-review/review-report.md`. Its SHA256 is computed after writing and given in the seat's final message.

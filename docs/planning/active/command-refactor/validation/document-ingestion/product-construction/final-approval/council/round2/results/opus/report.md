# INGEST final-document council round 2/2 — Opus seat report

Seat: claude-opus-5-5, fresh context, read-only. Date 2026-11-13.
Candidate `b4eecbe804b862f606995c4c4e5197c9b9d37150` on `feature/cmd-ingest-001`.
Presented document commit `115e4cecdb659d2af043c11e73964aca0a590d78`.

## Verdict

- **Aggregate: CHANGES_REQUESTED**
- assessment_complete: **true** (C1–C3 and FD1–FD8 all assessed)
- Mandatory findings: **1** (M1)
- Overall: **9.365 / 10** (exact weighted sum; not rounded)
- Per document:
  - final-approval `README.md` v2: **ready**. I found no defect in it.
  - `package-impact-assessment.md` v0.8: **ready**. I found no defect in it.
  - `approval-request.json` rev 2 (the bound manifest that README links and the receipt pins): **not ready**, because of M1.
  - `execution-profile.json` rev 2: **ready**.

## Identity and boundary (newly reproduced by this seat)

- I computed the request SHA256 before reading the file: `aef9c61c…c79d048`. It matches.
- Entry, before any status call: the logical index (sha256 of `git ls-files -s -z`) is `e5341c15…34e4` and matches. HEAD, branch, porcelain status and empty staging all match. All 8 preserved metadata/hash records match. All 17 required inputs, all 7 optional references and the controller-checks pin match.
- Presented-revision binding: `git show 115e4ce:<path>` reproduces all four target hashes (README `a7f027e8…`, impact `f5334ee1…`, request `7fbc2fa7…`, profile `fa964adc…`). The working-tree bytes are identical. 115e4ce is an ancestor of HEAD. Between 115e4ce and HEAD, only metadata/council/receipt files change, and `presented-revision.json` is new. So the receipt names a commit that does not contain the receipt, and the binding is noncyclic.
- Exit checks are recorded in `exit-evidence.json`. The controller checks were hashed only; I did not use them as evidence of correctness.

## Correction assessment (C1–C3)

**C1 Certifi: closed.** I confirmed the stated baseline against the lock: `uv.lock` has certifi 2025.11.12, and no workspace `pyproject.toml` declares certifi. Both documents say the same things:
- I1/I2 record the locked version, module and CA origin where Certifi is installed, or its absence in dependency-free profiles.
- There is no early bump.
- I3-C1 introduces 2026.10.23 and the `>=2026.10.19` floor through Tools' `document-ingestion` extra and its lock delta.
- Enforcement runs through every applicable install, including the final I3-C5 normal/optimized headless and Chat profiles.
- Absence is recorded rather than Certifi being added just for the check.

These statements appear in README (lines 81–90) and in the impact assessment (Certifi bullet). The profile carries them in `certifi_*` and `phases`, and the request in `phase_dependency_checks`. The slice map's I3-C1 Tools-pyproject/lock assignments and the shared-contracts "Dependency declaration before use" section agree. So do directive §3.1 and line 494 ("after all installs" is satisfied by recording at I1/I2).

**C2 tokenizers: closed.** I confirmed against the lock: tokenizers is 0.22.1, and its only dependents are `chromadb` and `litellm`. README, impact, profile and request all say the same three things:
- The 0.22.1→0.23.3 move happens at I1-C2 and also affects Chroma/LiteLLM.
- Paired unchanged-legacy positives cover the move.
- A conflicting resolution stops I1-C2, and no unapproved selection is made.

In the file map, the LLM/Memory pyproject files and `uv.lock` are assigned to I1-C2.

**C3: substantively closed, but its bound digest carries M1.**
- The embedding prerequisite is prominent. README operator item 6 says that every guarded operation (recall, extraction, `/ingest`) needs the manifest and counter assets "even with a fresh store", and that `/read` stays independent. The impact assessment covers this in its "Two independent local bindings" section and the P-05 row.
- Phase activation under the already-started initiative is explicit in README lines 38–41 and in `approval_scope.board_mapping`. On the board, the initiative is `started` with an initiative-level `implementation_authority: granted`. The documents correctly say that this flag is not INGEST approval.
- The noncyclic receipt is correct (verified above).

However, the request digest that C3 binds contains the stale gate text described in M1.

## Mandatory finding

**M1 — The exact approval manifest's operative approval gate names the wrong impact version.**

Evidence: `approval-request.json` line 283, `gate_disposition.A4.requires`, says:

> "Chuck approves this request SHA256 at its presented commit and impact **v0.7**."

The same manifest's `current_package_impact.version` is `"0.8"` and pins the v0.8 hash. README, the impact title, `current-controls.json` and the review brief all say v0.8. This is the only "0.7" in the four target files.

Why it is mandatory:
- A4 is the condition that the maintainer's approval record must satisfy.
- Approval binds this exact digest, so the stale text would become part of what is approved.
- Read literally, the gate asks for approval of a superseded version label, which contradicts the hash-pinned v0.8. A future controller that checks A4 could either reject a correct v0.8 approval or record approval against "v0.7".
- C1 explicitly required the exact request to be aligned. FD5/FD6 require noncircular, internally consistent exact references.

The hash pin makes the intended target recoverable. It does not make the gate text correct.

Bounded document fix: change A4.requires to "…and impact v0.8". Better, reference `current_package_impact.sha256` instead of a version label. Then commit the document change, issue a new presentation receipt for the new commit/digest, and update dependent pins. No scope or technical change is needed.

Future acceptance implication: until this is fixed, the maintainer's approval record should explicitly state that A4 is satisfied by the v0.8 bytes `f5334ee1…`. Otherwise the approval binding is ambiguous. No third council is authorized, so whether a re-receipted one-word fix needs further review is the maintainer's decision.

## Weighted eight-area matrix

| ID | Weight | Rating | Contribution | Basis |
| --- | ---: | ---: | ---: | --- |
| FD1 | 1.50 | 9.6 | 1.440 | Maintainer decisions applied coherently. No vendor/parity revival. TOOLS-DOC separate; no CLI/TUI expansion. |
| FD2 | 1.75 | 9.6 | 1.680 | 17 rows match the `packages/*` membership (17 manifests). 8 owners / 9 source-unchanged. Certifi/tokenizer shared effects and Finance HTTPS disclosed. |
| FD3 | 1.25 | 9.6 | 1.200 | Tools process ownership, Core neutrality, Memory policy, LLM in parent. `/read` takes no lease. Same-entry text→document. Cancel/reap/shutdown ordering. |
| FD4 | 1.50 | 9.5 | 1.425 | Per-field precedence. Two independent bindings. Fresh-absent-layout rules. Undeclared-alias limit stated. |
| FD5 | 1.50 | 8.8 | 1.320 | I1/I2/I3/AG exits and UAT separation are clear. M1 corrupts the A4 approval gate text. |
| FD6 | 1.00 | 8.7 | 0.870 | 91 phase paths equal the map's 91, with no slice mismatch. Case counts 49/51/18/0 match the map. Receipt verified. M1 contradiction in the exact manifest. |
| FD7 | 1.00 | 9.6 | 0.960 | Old-to-new map, no retirements, Finance offline selector and live exclusion, I3-C5 authored docs with substantive review, AG code council. |
| FD8 | 0.50 | 9.4 | 0.470 | Clear "next task" and effects. The version mismatch slightly muddies exactly what is signed. |
| **Total** | **10.00** | | **9.365** | |

## Area notes

FD1/FD3: The two documents describe one implementation. The worker thresholds are deferred to I3-C4 as build-then-prove, and both documents explicitly reject a pre-coding spike. Multi-agent stays Memory-owned and Runtime-assembled, with no source edits. Graph-recall scoring stays unchanged (FC-08). Retained legacy dependency edges are inventoried and not repaired.

FD2: The source-unchanged rows correctly say "source-unchanged ≠ test-unchanged". Each one names its inherited dependency path, for example Optimization→Memory counters and MCP `full`→Agent→Memory. The Certifi effect on Finance appears in the Certifi bullet but not in the P-14 row (see advice A3).

FD4: Command→YAML→built-in precedence is applied per field. `smart_file.*` stops governing `/ingest` and is explicitly not an alias. Optional `max_input_tokens`/`expected_dimensions` cannot silently truncate or admit incompatible vectors. Unset or default-derived paths never authorize creation. A new Runtime root also moves transcript/artifact locations. The documents require an old-release snapshot and recovery before upgrade.

FD5: The approval scope allows all three slices to be approved together, with independent-verification exits and re-asking only on material expansion. That is bounded. The profile lists `effects_performed_now: []`, and all `*_allowed_now` flags are false.

FD6: The README links the unpinned `preparation-checks.json`. That file changed after 115e4ce, which is acceptable because the README describes it only as planning checks. Historical v0.6 and `approval-binding.json` are honestly labeled as historical.

FD7: Root-discovery omissions (integration/Transcript) are named. Counts are explicitly "not proof of coverage".

## Separate optional advice (non-mandatory)

- A1. The Certifi floor is declared only in Tools' extra. Say explicitly that text-only headless profiles meet the I3-C1+ floor through the universal lock selection (2026.10.23), not through a new declaration. Otherwise "enforce in headless profiles" could be read as implying another declaration.
- A2. Put the profile's `phases` map in execution order. I2 currently comes after I3-C5. Also name I1-C1 explicitly for the baseline record.
- A3. Mention the Certifi CA-bundle change in the P-14 Finance row, not only in the dependency section.
- A4. The impact assessment could repeat README item 6's "even with a fresh store" sentence next to the binding rule.
- A5. The controller request's `scope` field also says "impact v0.7". This is a controller input, not a target, but it shows the same stale label and is worth sweeping.
- A6. The board initiative's `implementation_authority: granted` is correctly neutralized in the documents. An agent following AGENTS.md step 3 alone could still misread it, so per-phase activation records should be explicit.

## Method and evidence limits

- **Source inspection by this seat:** I read both targets, the request, the profile, the authorization, the brief, the corrections, the receipt and current-controls in full. I made targeted reads of the slice and case maps (structure, counts, dependency-bearing assignments), shared-contracts (dependency declaration timing), directive §3.1 and line 494, the readiness RD-06 line, the board initiative fields, and the `uv.lock` certifi/tokenizers entries and their dependents. I also read the workspace members and the `pyproject` extras/declarations.
- **Newly reproduced identity checks:** entry/exit index, HEAD/branch/status/staging, input pins, preserved records, and the four presented-commit hashes via read-only `git show`.
- **Historical inspected evidence:** none was used as proof. The board `validation` list and a grep surfaced historical note text naming earlier scores. I did not open those reports and did not rely on them.
- **Not performed:** no reads of the Finance live test, dirty YAML, `.friday*`, exports, `.venv` or caches beyond the pinned metadata/hash checks; no product imports, tests, installs, network, model or store operations; no AST/inventory/archive replay; no nested agents; no repository writes. I did not hash-verify the profile's base-interpreter pin, because that is outside this review's scope.
- Read-only git was run with `GIT_OPTIONAL_LOCKS=0`, and Python with `-I -B`. All output is in this seat's new scratch directory, outside the checkout.

This seat stops here. No repair, delegation, approval or construction authority follows from this report.

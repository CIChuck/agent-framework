# INGEST final approval documents — Opus seat, round1/1

Seat: claude-opus-5-5 (claudeAgent), effort high. Fresh read-only review.
Candidate `c2fcee0db2fc5b8dbf3a4682bd31cd2ce95963a0` on `feature/cmd-ingest-001`.

## Verdict

- **Verdict:** CHANGES_REQUESTED
- **assessment_complete:** true (all eight areas FD1–FD8 assessed)
- **Mandatory findings:** 1 (MF-1)
- **Overall:** **9.30 / 10** (9.305 computed; reported without rounding up)
- **Per document:**
  - `final-approval/README.md`: nearly ready. It needs the MF-1 Certifi correction (lines 68–70).
  - `package-impact-assessment.md` v0.7: nearly ready. It needs the MF-1 Certifi correction (lines 199–202) and should add the A1 lock disclosure.
  - Bound `approval-request.json` and `execution-profile.json`: internally consistent. The profile already places Certifi verification at I3-C5, and the README and impact assessment should match it.

The package is coherent and well bounded, and close to decision-ready. One concrete contradiction in the dependency and phase-evidence text stops me from returning VERIFIED. It can be fixed in one or two sentences.

## Entry/exit evidence (newly reproduced identity checks)

Both checks ran with `GIT_OPTIONAL_LOCKS=0` and `PYTHONDONTWRITEBYTECODE=1`, using standard-library hashing and read-only Git only.

- Request SHA256 was computed before reading the request: `6cde584b…2289` (matches).
- Logical index = sha256(`git ls-files -s -z`) = `1c5fd5f6…d2b8` at entry and at exit. It matches the expected value. My check script computes it before `status`.
- HEAD and branch match. Status shows exactly the two dirty example YAMLs plus `?? .friday-old/`. Staging is empty.
- 25 pins all match: 15 required inputs, 7 optional references, controller-checks (hash only), safe controls and the instructions file. All 8 preserved metadata/hash records match exactly at both entry and exit.
- **Disclosure:** my first entry command hashed the raw `.git/index` and then ran `git status` (locks off) before I worked out the "logical index" definition. I computed `ls-files -s -z` right afterwards and it matched. A locks-off status does not write the index, and exit is identical. No identity change occurred.
- Additional identity checks:
  - All 20 `reviewed_design.inputs` hashes match the current files.
  - The round7 index hash, the v0.6 approval record hash and the README/impact/profile hashes in the manifest all match.
  - The pinned base interpreter exists and its hash matches. It was hashed, not executed.

Evidence files: `entry.json` and `exit.json` in this directory. Controller checks were hashed only and are not used as correctness evidence.

## Method and limits

I read in full: the request, authorization, review instructions, both targets, `approval-request.json` and `execution-profile.json`.

I made targeted reads and checks of:
- `slice-file-map.json` and `test-case-map.json` (structure, phase and exit assignments, counts);
- `shared-contracts.md` §2–3 (bindings, dependency timing, defaults);
- `requirement-reconciliation.md` (binding and late-attachment dispositions);
- `readiness-disposition.md` RD-06;
- directive §3.1 and the installed-profile lines;
- root and package `pyproject.toml` metadata, `uv.lock` package entries (certifi, tokenizers, workspace names) and the `friday_commands.__all__` count.

I did not read prior review reports, peer reports, history or memory. I did not read the Finance live test, the dirty YAML contents, `.friday*`, `.venv`, exports or caches; I hashed only the listed records. I ran no product imports, tests, builds, installs or network operations, and made no repo writes. This is a document review, not a conformance, vendor or package evaluation.

## Source-inspected confirmations

- **Workspace and owners:**
  - Workspace members are `packages/*`. There are 18 directories, but `friday-tui` has no pyproject and is untracked, and `uv.lock` holds exactly 17 workspace packages. This confirms the "17 by membership, not directory count" claim.
  - The 91-path union of I1/I2/I3 `phase_edit_paths` (18/47/43) matches the slice map's slice assignments exactly.
  - The map covers exactly the eight owner packages plus workspace docs and lock. 84 paths are edits and 7 are new.
  - No Agent or indirect-package path appears. `app.py` and the root dirty examples are excluded by rule.
- **Phase timing:**
  - Counter metadata and lock at I1-C2.
  - Tools extra and lock at I3-C1.
  - Chat edge and lock at I3-C3.
  - Final installed profiles, Certifi and origins at I3-C5.
  - This matches the README, the impact assessment and the profile.
- **Case map:** 49 mapped cases, 51 new witnesses, 18 modules, no new retirements. Finance live test is excluded. Finance `test_basics.py` and Transcript are offline non-default selectors. Root discovery omits `tests/integration`. All of this matches both documents.
- **Package claims:**
  - Commands has zero dependencies and `__all__` = 54.
  - Tools depends on Finance and declares `psutil` and `python-dateutil>=2.8.0`.
  - Memory depends on pinned `friday-framework-llm` and retains `tiktoken`.
  - Optimization declares Memory with no source import.
  - MCP `full` reaches Agent and then Memory.
  - Legacy Tools `documents`/`spreadsheets`/`all-formats` extras exist.
  - All match the indirect-impact rows.
- **`smart_read.py` (I3-C2):** scoped to the headless text-storage handoff, consistent with "existing text-storage handoff, not every Tools document entry point".
- **Embedding binding:** the shared contracts confirm that both bindings are as stated. Embedding uses an explicit path, then `FRIDAY_EMBEDDING_MANIFEST`. A missing binding gives a typed readiness refusal for embedding operations. `/read` and disabled Memory never resolve it.

## Eight-area weighted matrix

| ID | Weight | Rating | Contribution | Basis |
| --- | ---: | ---: | ---: | --- |
| FD1 | 1.50 | 9.6 | 1.440 | One coherent implementation. Maintainer model, Office and shared-process decisions applied. No vendor or parity campaign. TOOLS-DOC, CLI and TUI explicitly excluded. |
| FD2 | 1.75 | 8.8 | 1.540 | 17 rows accurate and source-backed. The Certifi baseline is misstated and its phase timing contradicts the profile (MF-1). The shared tokenizers lock effect is undisclosed (A1). |
| FD3 | 1.25 | 9.6 | 1.200 | Tools, Core, Memory and LLM ownership is clear. `/read` takes no lease. Text-then-document runs through the same entry. Cancellation and reap gate slot release. Headless reuse uses the same service. |
| FD4 | 1.50 | 9.4 | 1.410 | Two bindings, precedence, fresh-store absence rules, model-change policy and the alias-swap limit are explicit. The universal embedding-manifest prerequisite could be more prominent in the operator list (A2). |
| FD5 | 1.50 | 8.8 | 1.320 | I1→I2→I3→AG order is coherent and noncircular: the manifest binds the README and profile, and the approval binds the manifest. The per-install Certifi duty cannot be met at I1/I2 under the narrow-delta rule (MF-1). |
| FD6 | 1.00 | 9.6 | 0.960 | All manifest hashes, paths and counts are consistent. Historical v0.6 and round7 bindings are labelled honestly. "Not implemented, not approved" is clear throughout. |
| FD7 | 1.00 | 9.6 | 0.960 | Old-to-new map, no silent loss, offline and live exclusions, I3-C5 substantive docs with content review, and independent slice and aggregate review are all explicit deliverables. |
| FD8 | 0.50 | 9.5 | 0.475 | "What is finalized / your next task / what approval authorizes / what remains separate" is clear. |
| **Total** | **10.00** | | **9.305** | Reported as 9.30. |

## Mandatory finding

### MF-1 — Certifi floor described as already existing and verified "after every install"; this conflicts with the phase plan (FD2, FD5)

**Evidence:**
- README line 68–69: "**Preserve** the Certifi floor >=2026.10.19 … Verify it **after every private install**."
- Impact lines 199–200: "the required floor **remains** `certifi>=2026.10.19` **after every installation**."
- In the current repo, no `pyproject.toml` declares certifi. `uv.lock` has a single `certifi` at **2025.11.12**.
- The directive §3.1 and `shared-contracts.md` (Dependency declaration before use) introduce the floor only in Tools' new `document-ingestion` extra at **I3-C1**.
- `execution-profile.json` puts Certifi verification at **I3-C5**. It also forbids "unrelated package upgrade" in phase lock deltas, and I1-C2 is the "narrow LLM/Memory counter" delta.

**Failure scenario:** at the I1-C2 private install, or any I2 install, the locked Certifi is 2025.11.12. The approved README instruction to verify ≥2026.10.19 fails. The builder must then either stop the phase, as the profile requires for an incompatible intended resolution, or bump Certifi early as an unrelated upgrade outside the narrow delta. Either way, the construction approval forces a mid-build scope decision it was meant to settle. Separately, "preserve" and "remains" hide the real upgrade consequence. At I3-C1 the shared lock and CA bundle move about a year, from 2025.11.12 to 2026.10.23, for every HTTPS consumer.

**Bounded fix (documents only):** in README §Dependencies and the impact assessment's Certifi bullet, state the following:
- the current baseline (no declared floor; lock 2025.11.12);
- that the floor is introduced by the Tools extra and its lock delta at I3-C1;
- what I1/I2 installs do. Either they record the locked Certifi version and origin without enforcing the floor, or Chuck explicitly elects to include the Certifi bump in the I1-C2 delta;
- that from I3-C1 onward, and for every I3-C5 final profile including headless profiles that do not declare the extra, Certifi is verified at ≥2026.10.19 together with module/CA origin.

Align the `execution-profile.json` phase text if a different choice is made.

**Future acceptance implication:** I3-C1 and I3-C5 run bindings must show the Certifi version, origin and CA path for every installed lane (normal and optimized, headless and Chat). Earlier lanes must show the recorded locked version and no unrelated upgrade.

## Optional advisories (not mandatory)

- **A1 — shared tokenizers pin:**
  - `uv.lock` currently has `tokenizers 0.22.1`, used by `chromadb` and `litellm`.
  - Selecting `tokenizers==0.23.3` in LLM's extra moves the single workspace lock, so all Chat, Memory and Runtime consumers are affected even without the extra.
  - I suggest disclosing this beside Certifi as a shared-lock consequence. Also say that I1 unchanged-legacy positives cover it, and that a resolution conflict stops I1-C2 rather than prompting a different selection.
- **A2 — operator prominence:** add one item to the README's "Operator-visible behavior" list. After upgrade, every guarded embedding operation (recall, extraction, `/ingest`) needs a provisioned `FRIDAY_EMBEDDING_MANIFEST` or explicit path with local counter assets, even for a fresh store. The impact assessment states this, but the README list implies it only indirectly.
- **A3 — lifecycle mapping:** in one line, say how a recorded approval maps to board transitions (`approved` → `started` per phase activation). This is the AGENTS.md precondition for code generation.
- **A4 — presented commit:** name the exact commit that Chuck's approval will bind (the current candidate or a successor carrying council results), so "the presented commit" is unambiguous.

## Authority

Report only. No construction, effects, approval, acceptance or delivery authority follows from this review. No repair, delegation or additional round was performed.

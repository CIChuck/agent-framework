CHANGES_REQUESTED

# Sol independent construction-directive review

Unit CD-CMD-INGEST-GATE-A-001; round 1 of one authorized round. Reviewed 2026-11-11 as GPT-6.1 Sol (`gpt-6.1-sol`), high reasoning effort, through Codex in T3 Code. This is a fresh task-only review context, not the builder or controller session. No builder transcript, memory lookup, current peer report, delegation, remediation or external service was used. The injected general memory summary was not used as correctness evidence. Historical review names/verdict labels occur in required planning/navigation documents; they were encountered only as provenance, never adopted as evidence. The changed historical report path received added-navigation-only diff inspection; its report body was not reviewed. Explicit shared-checkout read-only exception applies.

Candidate: `f81453695007cacfa072fe295b8da7aa478438ba`, branch `feature/cmd-ingest-001`.
Construction source: `494eed4f1c15d79d29cf0acc5e2203d7c7ebe5ef`.
Full bounded range: `72c5d736a7b938b499f2eb5f933d0940183fae42..f81453695007cacfa072fe295b8da7aa478438ba`, exactly 18 planning-only paths.
Directive SHA256: `e44d4e4b28736d66a1de1e66314cb6da25343430dec0933be4ac9f1645ec91ad`, also independently reproduced from construction-source Git bytes.
Review mode: FULL independent design/source-feasibility and bounded readiness-planning aggregate; DOCUMENT READINESS, not implemented-harness verification.
Private scratch: `/tmp/igh-r1-sol-review-2oP7POrY` (macOS `/tmp` resolves to external `/private/tmp`).

## Authority and identity

The request was the first substantive input: SHA256 `651d8edfa6d1afb952418ee393b5f1369eadce2ef6b73eeb63eeb61c37320a44`. Its current-controls, protected-manifest and helper hashes were verified before use; the COMPLETE helper source was inspected before execution. Full authority hashes are recorded in `input-identities.json`, copied from the authoritative request and independently checked by both boundary runs. Opening boundary passed: logical index SHA256 `2873bdac566cf50f8c9acf1994aaaf02a23b58a31cc4c06cdb1e828b35ed0d46`, 17,773 protected files, 24 authority pins, nine preserved records, correct HEAD/branch/status, empty staging.

Controlling precedence is explicit maintainer instructions, repository policies, then the pinned parents and directive. Read AGENTS.md, all three named policies, council and independent-code-validator skills; the complete directive, HRC criteria, authorization and roster; complete readiness plan, isolation requirements, envelope, source observations, consumer worklist, impact assessment, test migration/architecture/guide plans, Tools companion and prior impact criteria/authorization. Relevant REM A/B/D and annex baseline identity/headless/proof-matrix clauses were inspected in depth, with heading inventory for surrounding deferred product obligations. This did not restart the parent product-design audit. Parent pins are checked as exact bytes, not accepted merely because old review text calls them verified.

For citations below, D means `docs/planning/active/command-refactor/directives/CD-CMD-INGEST-GATE-A-001-readiness-harness.md`; G means `docs/planning/active/command-refactor/validation/document-ingestion/gate-a/`; REM and Annex mean the pinned `remediation/REM-CMD-INGEST-001-pdf-docx.md` and `embedding-compatibility-contract.md` within the same command-refactor packet. Line references describe this frozen candidate.

## Numbered findings

1. **IGH-R1-SOL-001 — HIGH — Required launch commands leave ambient Python startup code outside the pre-effects boundary.**

   **Violated requirements:** HRC-03 (bootstrap/import/environment isolation before execution), HRC-05 (no-effects preflight), HRC-13 (meaningful bootstrap negative controls); D:90–109, 188–190, HR-02/03/10/11 at D:199–208; G/isolation-requirements.md, Production boundary and Manual operation and evidence. The maintainer requires an isolated test environment and no production changes.

   **Concrete evidence:** The required manual interface at D:180–185 starts both bootstrap and run-owned operations with `-I -B` and the offline test forms at D:215–216 do likewise. D:188–190 requires a standard-library bootstrap and rejection of the working `.venv`, but specifies neither suppression nor prior qualification of automatic system site initialization. `-I` disables user-site/environment influence; it does not disable system site initialization. `-B` prevents bytecode writes only. System `.pth` executable lines and `sitecustomize` run before `run.py` can reject the interpreter, install guards, sanitize child environments or record origins. A globally installed hook can perform file/network/process effects before a supposedly no-effects preflight. This is a startup-order hole in the prescribed interface, not evidence that a malicious hook currently exists.

   **Static corroboration:** `startup-source-evidence.txt` records the locally installed CPython 3.14.2 standard-library `site.py` path/hash and lines 211–214 (execute `.pth` import lines), 707–715 (system site packages and sitecustomize; isolated-mode conditional does not guard these), 719–722 (`no_site` gates automatic main). This is corroborating startup semantics, not target Python 3.13.10 qualification. No hook, executable exploit, harness test or target inference was run. The locally searched Homebrew Python 3.13 source location was absent (search exit 2); no installed-target proof is claimed.

   **Risk:** Out-of-run writes, imports or provider/network calls can precede all harness-enforced boundaries. Post-import origin reporting and protected-state comparison detect some effects after the fact and cannot supply the required prevention. Rejecting only the working `.venv` is insufficient for a system interpreter.

   **Narrow mitigation:** Amend the construction instructions and every launcher/test/child command to establish a trusted startup before application Python code: for example `-I -S -B` (plus `-O` where required), an explicitly qualified interpreter/stdlib, and deliberate import-path installation of only the frozen harness/private target after guards are installed. Do not invoke `site.main()` or process arbitrary `.pth` files to restore dependencies. If a different mechanism is chosen, require equally concrete pre-start guarantees. No production configuration change is needed; the amendment is confined to this test harness design/README/test obligations.

   **Required proof for later construction:** In wholly private test installations, place sentinel-writing/failing system-site `.pth` and `sitecustomize` hooks and show they never execute for preflight/init/run/report, normal and optimized test lanes, and spawned Python workers. Verify actual entry into the harness and intended outcomes with canonical origins; absence of a sentinel caused by setup/import failure earns no credit. Include clean-start positive controls and zero out-of-run writes/network calls. This review does not authorize executing these tests or implementing the mitigation.

No additional mandatory finding is asserted. The startup issue is counted once; its affected matrix rows below do not represent duplicate findings.

## Full HRC matrix

PASS means adequate design instructions for future construction, not executed runtime conformance.

| Criterion | Result | Evidence and assessment |
| --- | --- | --- |
| HRC-01 | PASS | D:3–14, 22–43, 74–86; G/council-round1/authorization.md and pinned current-controls separate draft approval, construction, stage promotion and window confirmation. Later explicit council authorization supersedes the directive's earlier no-council preparation sentence without activating effects. |
| HRC-02 | PASS | D:45–72 enumerates versioned code exclusively in tests/readiness/ingest/, generated state in .friday_test/, root-anchored `/.friday_test/` as the sole ignore change, and forbidden package/config/lock/env/store edits. Boundary helper confirms this candidate changes planning only. |
| HRC-03 | FAIL | IGH-R1-SOL-001; D:180–190/215–216 startup occurs before proposed guards. The rest of D:96–109 and isolation requirements correctly require private targets, minimal environment, explicit caches, subprocess and origin checks. |
| HRC-04 | PASS | D:103–109/200–201; G/isolation-requirements.md Test workspace and readiness-plan Private layout require physical ancestors/ownership, aliases/symlink/overlap refusal, safe members, immutable inputs/assets and new-only publication from run staging. Python audit limits are explicitly acknowledged; fail-closed enforcement remains a later implementation proof, not an OS sandbox claim. |
| HRC-05 | FAIL | D:90–102/110–115/173–192 defines coherent fresh init, bound continuation, selected/full/offline/report and scoped-vs-full results, but the required command form undermines no-effects preflight as in IGH-R1-SOL-001. |
| HRC-06 | PASS | D:82–85/116–121/201; G/envelope stages A0–A2, manifest_review, hosts/budgets and readiness-plan Stage promotion bind exact graph/artifacts/licenses, target Certifi verification after all installs, no arbitrary extras, executable builds or ambient fetch. Seeds are explicitly observations, not promoted transitives. |
| HRC-07 | PASS | D:141–171/202; G/model_window_policy and isolation LM Studio section require operator shutdown/restart evidence and actual log separation, run/config/dependency/asset/input binding, expiry/revocation, per-batch checks and exact requests/budgets; prohibit management APIs. No receipt supplied; requests remain gated. |
| HRC-08 | PASS | G/isolation LM Studio section and readiness-plan Shared window/A3 explicitly permit existing server/served weights while keeping Docling/OCR/tokenizer assets test-owned. D:115/160–165 blocks dependent model effects only, labels attestations, invents no log-directory switch or service rights. |
| HRC-09 | PASS | D:122–128/203; readiness-plan A2 fixes >=30 genuine fixtures (6/6/10/8), independent ordering/structure/formula/notes expectations and shared malformed controls. REM B defines fail-closed clipping/warnings and sole Docling text supply. Supplied originals remain unchanged, explicit and supplemental. |
| HRC-10 | PASS | D:129–134/204; readiness-plan A2/A3 and REM D require document/recursive/fixed, default 512 and overrides, final prepared text including context/special tokens, lossless split-or-refuse, source provenance, local matched counters, and real count/order/shape qualification. Preliminary counts and synthetic vectors receive no real-model credit. |
| HRC-11 | PASS | D:19–20/134/235–237; G/envelope excluded_effects and readiness-plan A0–A4 reserve integration stores for later. A0 consumer inventory supplies future directive bindings, not framework changes or store writes. Test/architecture/guide/Tools companion obligations remain later. |
| HRC-12 | PASS | D:135–139/167–171/205/239–244; envelope supplies numeric network/download/disk/RSS/time/admission/request/vector/token ceilings and 30-second quiescence. Only owned children may stop; no service restart, automatic user cleanup or resumption. Shared-server resource effects are expressly bounded, not eliminated. Startup exception tracked under HRC-03. |
| HRC-13 | FAIL | D:194–227 has substantive normal/-O private lanes, minimal/dependency selectors and no setup-failure refusal credit; root pyproject.toml:134 independently confirms tests/ exclusion. IGH-R1-SOL-001 requires extending bootstrap/startup proof and safe command forms before this row can pass completely. |
| HRC-14 | PASS | D:106–109/160–165/206–209/229–237 and readiness-plan A4 require observed vs attested, executed vs inspected/blocked/skipped, origins, exact manifests, protected-state proof, scoped/full reporting and no fabricated readiness. Existing planning-checks.json is inspected historical preparation evidence only; fresh admin results are separate. |
| HRC-15 | PASS | Pinned current-controls, authorization/roster, all routing deltas and fresh board/dashboard checks agree on one read-only pass and no construction/effects. Execution log is byte-prefix append-only. Authority history arrays preserve their prior prefixes; board diff removes only the prior next_gate and appends new records. Old labels are scoped historical statements. |
| HRC-16 | PASS | D:229–244, G/readiness-plan activation checklist, pinned current-controls and council authorization give precise stop/escalation and separate implementation review/approval. No automatic remediation/replacement loop, acceptance or delivery. Finding 001 must be resolved before this design is treated as meeting the full construction-readiness gate. |

## Complete HR design-obligation trace

| Obligation | Design trace and assessment |
| --- | --- |
| HR-01 | D:45–72,198; G/isolation Test workspace. Adequate exact placement, allowlist and protected-state requirements. |
| HR-02 | D:90–102,173–192,199. Operations defined; startup gap in no-effects preflight is finding 001. |
| HR-03 | D:103–109,200,219–224; G/isolation final paragraphs. Paths/imports/cache/child negatives and normal/-O explicit, but automatic pre-guard site execution needs finding 001 correction. |
| HR-04 | D:116–121,201; G/readiness-plan promotion/A1/A2. Missing/tampered/extra/wrong-host/license/binding refusal, explicit target Certifi floor, no setup-failure credit. |
| HR-05 | D:148–171,202. Missing/false/stale/expired/revoked/mismatched/incomplete receipt gives zero calls; simulated valid scope and no server-control route required. No current endpoint contact needed. |
| HR-06 | D:122–128,203; G/readiness-plan A2; REM B. Genuine deterministic baseline and independent content/structure expectations; supplied copies preserve originals; failures explicit. |
| HR-07 | D:129–134,204; REM D; readiness-plan A2/A3. Strategy/budget/prepared-input boundaries, preliminary/model-qualified separation and conditional real A3. |
| HR-08 | D:135–139,205; G/envelope budgets/document_probe_limits. Admission/time/resource cancellation, owned termination and per-batch window/stop checks specified. |
| HR-09 | D:191–192,206,235–237; G/readiness-plan A4. Readable/JSON reports, oracle/baseline defects, full/scoped qualification and isolation distinct. |
| HR-10 | D:188–190,207,219–223. Minimal stdlib offline lane versus optional profiles is explicit; finding 001 addresses how stdlib-only startup is actually established. |
| HR-11 | D:208,211–227; root pyproject.toml:134. Explicit unittest discovery and optimized selectors avoid false root pytest credit; startup command update required by finding 001. |
| HR-12 | D:209,229–244; G/readiness-plan A4. Private installed/source origins, protected state and independent implementation verification retained; no product/UAT/delivery credit. |

## Commands and evidence

All Git subprocesses used `GIT_OPTIONAL_LOCKS=0`. No status-producing Git command preceded the opening helper. Exact eight required administrative argv/cwd/time/exits/stdout/stderr are retained in `commands.json` and corresponding named `.stdout`/`.stderr` files. They ran through the inspected helper with reviewer-owned UV/XDG/Mypy/bytecode/temp paths, Python bytecode off, offline/frozen/no-sync/no-download flags.

Required helper invocation base:
`python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-council-r1-3kkwwzkk/inputs/review_tools.py <action> --request /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-council-r1-3kkwwzkk/inputs/request.json --scratch /tmp/igh-r1-sol-review-2oP7POrY`

| Fresh command/check | Exit/result |
| --- | --- |
| `shasum -a 256 <request>` before substantive input | 0; exact required hash matched |
| Python stdlib hash checks and complete helper read | 0; current-controls/protected-manifest/helper match |
| `mktemp -d /tmp/igh-r1-sol-review-XXXXXXXX` | 0; fresh private scratch created |
| Helper `boundary ... --label opening` | 0; PASS, no failures |
| Helper `admin ...` | 0; all eight checks exit 0 |
| Board validate / dashboard render --check | 0 / 0; 36 tasks valid; dashboard current |
| Documentation lifecycle / package metadata | 0 / 0; 1058 Markdown files; 18 metadata manifests |
| Planning worktree / staged / full range / preparation range whitespace | 0 / 0 / 0 / 0 |
| `git diff --no-ext-diff --unified=3 <full range> -- <each of 18 paths>` | 0 each; scoped inspection, historical report limited to added navigation |
| `git show <base>:<authority.json or board.yaml or execution-log.md>` and programmatic prefix/history comparison | 0; append-only history evidence retained |
| `git show <construction-source>:<directive>` plus SHA256 | 0; unchanged e44d4e4b... |
| Static `cat`, `nl -ba`, `sed -n`, `rg -n`, `wc -l` over named authorities, private diffs and root testpaths | 0; document/source inspection only |
| `python3 -I -B -S` stdlib scripts to read/hash site.py and write own evidence | 0; startup-source-evidence.txt |
| `rg --files /opt/homebrew/Cellar/python@3.13 -g site.py -g initconfig.c` | 2; directory absent, no target-source evidence inferred |
| Helper `boundary ... --label closing` and final request hash | Recorded in closing addendum below |

Evidence directory also contains `input-identities.json`, `history-and-source.json`, `board-history-check.json`, and per-path `diff-<index>.txt` for non-report paths. Supplied paths were read-only; no supplied output/cache argv was replayed. The exact supplied request and helper paths above are inputs only.

All 18 changed paths were assessed: generated dashboard; packet README/current authority/current routing; full directive; new append-only execution-log entries; tactical/next-phase/branch/Gate-A handoffs; complete authorization/criteria/roster; full envelope/isolation/plan/planning checks; historical report's current navigation delta only; and board delta/history preservation. Raw historical authority/report bodies and dirty YAML contents were not used as evidence. No .friday/.friday-old or personal state content was inspected.

## Limits, debt and next gate

No harness/product tests, root/package suites, root Ruff, live Finance module, builds, resolution, installation, conversions, generated fixtures, network/provider/model/service/store calls, endpoint observation or production data access occurred. Existing root Ruff534, test_display collection conflict and registry-formatting failures remain historical FAILED/UNWAIVED debt; this review neither reproduced nor waived them. Administrative passes establish planning structure only. Upstream candidate version/URL/license/asset observations were inspected as pinned seeds and remain unqualified until separately activated stages; no fresh upstream lookup was performed under the explicit network prohibition.

Actual model/window/counter facts are intentionally absent, and this is correctly gated rather than a missing implementation finding. Operator attestation cannot become observation merely because an endpoint responds. Actual log separation must be established; unsupported mechanisms block A3. The harness has zero service-management rights. An audit hook is not OS/native-code confinement; later construction must prove the boundary actually used and stop if it cannot. No OS-sandbox implementation or third-party containment success is certified by this report.

Coverage score: **10.0/10** — all 16 HRC criteria assessed (8 points, 0.5 each) and all 12 HR obligations traced (2 points, 1/6 each). Coverage counts review completeness, not candidate compliance.
Overall score: **8.9/10** — scope/authority 2.0/2; isolation/effects enforceability 2.2/3 (pre-start hole); clarity/feasibility 1.8/2 (unsafe required command forms); verification/evidence 1.9/2 (startup negative proof missing); manual usability 1.0/1 (clear stage interface and pending inputs). The mandatory finding controls the outcome regardless of either score or the 9.5 target.

Return this report for controller reconciliation with the other two independent seats. This one round supplies no remediation loop, replacement round, construction/effects activation, human acceptance, product integration or delivery authority.

## Closing preserved-state addendum

Closing helper exited 0 at 2026-11-11T21:57:03.011476+00:00; PASS with no failures. HEAD, branch, staging/status, logical index, all 17,773 protected files, all 24 authority pins and all nine preserved records match opening/request. Final request rehash exited 0 and remains `651d8edfa6d1afb952418ee393b5f1369eadce2ef6b73eeb63eeb61c37320a44`. No checkout changes or repairs were made. `integrity-opening.json` and `integrity-closing.json` are the fresh boundary receipts.

# CHANGES_REQUESTED

Astra seat, round 1: CD-CMD-INGEST-GATE-A-001. One mandatory high-severity design finding. This is document readiness and bounded source-feasibility review, not implementation verification.

## Frozen identity and authority

- Workdir: `/Users/chuckrussell/Dev/gendev/agent-framework`; branch `feature/cmd-ingest-001`.
- Candidate: `f81453695007cacfa072fe295b8da7aa478438ba`.
- Construction document source: `494eed4f1c15d79d29cf0acc5e2203d7c7ebe5ef`.
- Full bounded range: `72c5d736a7b938b499f2eb5f933d0940183fae42..f81453695007cacfa072fe295b8da7aa478438ba`, exactly 18 planning paths.
- Directive SHA256: `e44d4e4b28736d66a1de1e66314cb6da25343430dec0933be4ac9f1645ec91ad`.
- Request: `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-council-r1-3kkwwzkk/inputs/request.json`; SHA256 `651d8edfa6d1afb952418ee393b5f1369eadce2ef6b73eeb63eeb61c37320a44`, verified BEFORE substantive input reading.
- Current-controls SHA256 `6692e709d1167c48723fa853461d02d6538101cd4c9db5f95a730fb21b1d6508`; protected manifest `d1fc0015ea83ef13ae62c8f96b881f072b524d62471f89030dddde01dfb32256`; helper `7a7f2ef72d4b1e6592e6ba65d2762641865031a81e7bfdfc573b9ec5d56a11e5`: verified before use. Full helper source inspected before running it.
- All 24 authority pins reproduced at opening; exact manifest retained as `authority-pins.json`, including all 14 directive parents.
- Explicit maintainer direction and pinned request control; AGENTS, all three policies, council and independent-code-validator skills read. Current controls, council authorization/criteria/roster establish one read-only round; construction/effects/window remain unapproved. Historic no-council wording in the unchanged directive is superseded by explicit current authorization, not a new contradiction.

## Independence and scope

Reviewer: GPT-6 Astra (`gpt-6-astra`), high effort, Codex harness in T3 Code. Fresh task-specific review context; first boundary receipt at 2026-11-11T21:52:38.727019+00:00. No builder transcript, private reasoning, current peer report or peer conclusion supplied or searched. General environment instructions included historical memory/navigation summaries; none was queried or used as correctness evidence. Historical verdict labels were encountered in pinned parent/navigation text and were not adopted. No delegated work.

Explicit shared-checkout read-only exception used. Reviewer-owned scratch is `/tmp/igh-r1-astra-zsdvg9z1` (physical macOS alias `/private/tmp/igh-r1-astra-zsdvg9z1`), created fresh outside the checkout and all supplied directories. Only this scratch received reviewer evidence. Supplied helper uses private cache/temp paths and bytecode off. No dirty YAML content or personal state inspected.

## 1. IGH-R1-ASTRA-001 — High — Python startup can execute ambient code before isolation guards

**Violated requirements:** HRC-03 (isolation before execution), HRC-05 (no-effects preflight), HRC-13 (meaningful negative proof); HR-02, HR-03, HR-10. Directive required behavior 1–3, lines 90–109, requires no production defaults/inherited imports, no preflight effects and guards before effects. `isolation-requirements.md`, “Production boundary”, “Test workspace” and “Manual operation and evidence” prohibit live-environment imports and require refusal before effects.

**Concrete evidence:** directive lines 180–185 prescribe `<bootstrap-python> -I -B ...` and `<test-python> -I -B ...`; lines 188–190 only require stdlib bootstrap and rejection of an interpreter inside the working `.venv`. Lines 215–216 repeat `-I -B` for normal/optimized tests. There is no requirement to suppress system site initialization or establish a verified startup environment before Python begins executing startup hooks. `-I` removes user-site/environment path influence, but does not disable system `site` processing; `-B` suppresses bytecode writes, not arbitrary code execution.

Static inspection of the actual local target-version library at `/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/lib/python3.13/site.py` confirms: lines 206–207 execute import lines from `.pth` files; lines 644–648 import `sitecustomize`; `main()` lines 699–709 invokes site-package processing and `execsitecustomize`, while the isolated-mode condition only gates readline configuration; lines 713–716 gate initialization on `sys.flags.no_site` (`-S`). Source SHA256 `ea80b1f9fd676ec6d0c3ce8219d1ecfd103992e93e927c5d0a95a18443059f66`. Exact excerpts retained in `python-startup-source.txt`. An initial inspection of Homebrew Python 3.14 source was followed by this target-version inspection; no target interpreter or startup hook was executed for proof.

**Failure scenario/risk:** a bootstrap interpreter outside `.venv` can have an installed `.pth` or `sitecustomize` hook. Following the documented command executes that code before `run.py`, before a harness audit hook/environment allowlist, and before the working-environment refusal. Such a hook can import production modules or write outside the run even in a purportedly no-effects preflight. A later origin/protected-state check detects damage only after the prohibited effect. This is a hole in the proposed launch contract, not a claim that this workstation currently has such a hook.

**Narrow mitigation:** require a verified startup-safe interpreter/launcher contract for bootstrap and every Python child, including preflight, init, report and test lanes. A concrete approach is isolated, no-site, no-bytecode startup (`-I -S -B`) with explicitly controlled loading of the frozen harness and manifest-owned dependency roots only after path/environment/origin guards are established; do not re-enable ambient `site.main()` or process uncontrolled `.pth` files. Bind interpreter/stdlib origins and clarify handling of private venv/site paths under Python 3.13. An equivalently evidenced startup exclusion is acceptable. No production Python installation needs modification.

**Required proof:** require future private-fixture normal and `-O` witnesses with canary `.pth` and `sitecustomize` hooks, proving their bodies never execute, no production import occurs and no forbidden write/network request occurs before harness guards. Include a positive valid launcher run and separate invalid working-venv refusal; import/setup failure alone earns no refusal credit. Update the command examples and HR-02/03/10 proof obligations. This review did not run the exploit or any tests.

## HRC-01–16 matrix

References: D = complete directive; P = Gate-A readiness-plan.md; I = isolation-requirements.md; E = effects-envelope.json, all under the pinned command-refactor packet. PASS means adequate design requirement, never executed readiness.

| Criterion | Assessment | Evidence and rationale |
|---|---|---|
| HRC-01 | PASS | D 3–43, 74–86; current-controls and council authorization separate draft/parent approval/construction/effects/window/acceptance. No prior verdict transferred. |
| HRC-02 | PASS | D 45–72: exact test-only files, only root-anchored `/.friday_test/` ignore metadata change, no packages/root locks/working environment/config/store changes. Boundary and 18-path audit confirm planning-only candidate. |
| HRC-03 | FAIL | Finding 001: D 180–190 does not exclude startup hooks before the otherwise explicit private environment/import/cache/child requirements in D 90–109, I Test workspace. |
| HRC-04 | PASS with stated limit | D 103–109; I Test workspace; P 55–90 require physical ownership, ancestors, aliases/symlinks/overlap/archive refusal, new-only manifest publication and read-only shared inputs/assets. Implementable contracts; Python audit is expressly not an OS sandbox. Startup issue is separately tracked, not excused by this PASS. |
| HRC-05 | FAIL | D 90–102, 110–115, 173–192 coherently define modes/owned continuation/scoped reporting, but specified launch allows preflight effects before control (001). |
| HRC-06 | PASS | D 76–86,116–121; P 149–236; E candidate requirements, stage promotion/hosts/budgets. Exact manifests precede effects; post-all-installs Certifi floor and target origin proof required; seeds explicitly unqualified. |
| HRC-07 | PASS | D 141–171; I LM Studio section; E model_window_policy: run/config/dependency/asset/input/model scope, operator shutdown/restart/log evidence, expiry/revocation, every-batch checks, no management rights. Actual log separation required; no unsupported switch assumed. |
| HRC-08 | PASS | D 115,143–165; I served-model exception and test-owned Docling/OCR/tokenizer assets; P 98–128,274–286. Unknown operator facts correctly block A3 without blocking separately activated offline work. |
| HRC-09 | PASS | D 122–128,203; P 238–257 requires at least 30 genuine fixtures (6 PDF/6 DOCX/10 XLSX/8 PPTX), independent expectations plus malformed/limit controls. I Controlled documents requires explicit manifests, copied inputs and preserved originals. REM B 332–456 preserves fail-closed extraction/coverage. |
| HRC-10 | PASS | D 129–134,204; P 259–303; REM 582–630; annex baseline identity section. Three strategies, full prepared token envelope, 512/overrides, preliminary-count versus qualified deployment, synthetic versus real vectors clearly separated. |
| HRC-11 | PASS | D 16–20,134,235–237; E exclusions; consumer matrix future trace; P 127–128,264–270,297–303. No Memory/Chroma/graph/WAL writes in A0–A4; product/TOOLS-DOC/consumer integration/test migrations/guides remain later. |
| HRC-12 | PASS as stage contract | D 135–139; P 130–147; E numeric budgets and per-stage destinations. Owned child termination/quiescence and no server restart/resumption are explicit. Python-level controls are not represented as OS isolation. Startup exception remains finding 001. |
| HRC-13 | FAIL | D 194–227 gives substantial explicit minimal/dependency lanes and normal/-O negative proof; root pyproject.toml:134 confirms discovery excludes tests/. Startup canary proof needed to close 001; later call-phase guards cannot establish pre-launch containment. |
| HRC-14 | PASS | D 107–109,160–165,206–209,231–237; P A4 and I evidence section separate attestation/observation, inspected/executed/blocked/skipped, scope/readiness and origins/protected-state evidence. |
| HRC-15 | PASS | Hash-pinned current-controls plus authorization/roster agree on one read-only pass. Administrative board/dashboard checks pass. Structural authority comparison changes current readiness/control fields only; full execution-log prefix preserved. Historical report wrapper assessed mechanically only, never as verdict evidence. |
| HRC-16 | PASS subject to 001 correction | D 39–43,63–86,229–244 precisely gates edits, changes, effects and independent implementation review. Required future operator inputs remain unbound intentionally. No new approval, replacement round or remediation loop inferred. |

## HR-01–12 design trace

| Obligation | Design trace and disposition |
|---|---|
| HR-01 | D 45–72 and I workspace layout; HRC-02/04 PASS. Versioned tests versus generated runtime artifacts and only named ignore rule explicit. Future production boundary evidence required. |
| HR-02 | D 90–102,173–192; HRC-05 FAIL by 001. Modes are specified, but no-effects preflight startup must be corrected. |
| HR-03 | D 103–109,200; I final boundary paragraphs; HRC-03 FAIL by 001. Required path/archive/import/cache/process negative proof needs startup coverage. |
| HR-04 | D 116–121,201; P 149–236; HRC-06 PASS. Missing/tampered/extra/unknown-host-license/binding controls and no setup-failure credit are explicit. |
| HR-05 | D 148–169,202; HRC-07 PASS. Receipt-negative zero-call controls and positive exact endpoint/budget controls; no service-management capability. |
| HR-06 | D 122–128,203; P 238–257; HRC-09 PASS. Genuine fixtures and supplementary copies with independent content/structure expectations; no original edits or scanning. |
| HR-07 | D 129–134,204; P 259–303; HRC-10 PASS. Model-bound preparation/counting/real vector qualification remains conditional, no future evidence demanded now. |
| HR-08 | D 135–139,205; P budget table/E budgets; HRC-12 PASS. Owned termination/evidence/quiescence and stop/expiry before further batches. |
| HR-09 | D 191–192,206,231–237; P A4; HRC-14 PASS. Scoped/full result distinctions and oracle/baseline defects remain visible. |
| HR-10 | D 188–190,207,219–224; HRC-03 FAIL by 001. Stdlib/minimal profile intent is sound but interpreter startup can import ambient code before those guarantees. |
| HR-11 | D 208,211–227; root pyproject.toml:134; explicit selectors PASS. Normal/-O witness design requires the finding's startup extension. No root discovery claim. |
| HR-12 | D 209,229–244; I evidence; HRC-14/16 PASS. Private target/source origins, receipts, preservation and fresh implementation review retained; no UAT/delivery inference. |

## Read and inspected coverage

Read complete directive, all HRC criteria, authorization/roster, AGENTS and three policies, both skills, Gate-A plan, isolation requirements and effects envelope. Inspected all 14 pinned parent authorities at relevance appropriate to this bounded unit: assessment scope/readiness/change-control, REM Gate-A/Certifi/extraction/chunking/model qualification, annex baseline/replacement/identity constraints, complete migration/architecture/guide/Tools-companion planning contracts, package-impact criteria/round6 authorization, source-observation seed/asset inventory and qualification limitations, and consumer worklist/trace/stop boundaries. Did not restart the whole parent product-design audit or validate every historical consumer call site.

All 18 changed paths inventoried in `changed-path-audit.json`. Full new directive and Gate-A planning content read; changed navigation/handoffs examined in `navigation.diff`; planning diff retained in `planning.diff`. Board/authority current state read through pinned current-controls, with structural old/new authority comparison in `authority-structure.json`. Execution-log old content is an exact prefix (3300 lines retained, 57 added). Historical package-impact report wrapper comparison finds only lines 17–22 replaced by 17–23, preserving initial review record; no report body/old verdict was displayed or used as correctness evidence. `planning-checks.json` inspected only as historical preparation metadata; fresh admin results supersede its check claims for this review.

Static source limited to concrete claims: root pytest discovery, `.venv/bin/python` symlink to locate target-version stdlib without invoking it, and Python site startup behavior. No production package imports, deep product audit, user-YAML reads, model-cache reads or endpoint calls.

## Commands and evidence

Required helper invocations (all exit 0 when recorded in boundary/admin evidence):

```text
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-council-r1-3kkwwzkk/inputs/review_tools.py boundary --request /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-council-r1-3kkwwzkk/inputs/request.json --scratch /tmp/igh-r1-astra-zsdvg9z1 --label opening
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-council-r1-3kkwwzkk/inputs/review_tools.py admin --request /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-council-r1-3kkwwzkk/inputs/request.json --scratch /tmp/igh-r1-astra-zsdvg9z1
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-council-r1-3kkwwzkk/inputs/review_tools.py boundary --request /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-harness-council-r1-3kkwwzkk/inputs/request.json --scratch /tmp/igh-r1-astra-zsdvg9z1 --label closing
```

`commands.json` contains exact argv, cwd, timestamps, exits and private stdout/stderr paths for all eight required administrative commands. Four use `uv run --offline --frozen --no-sync --no-python-downloads python -B`: board validate (36 tasks), dashboard render --check, documentation lifecycle (1058 files), package metadata (18 manifests). Four Git whitespace checks cover planning worktree, staged state, full unit range and preparation range. All exit 0. Every Git command, including mechanical diff/show comparisons, used `GIT_OPTIONAL_LOCKS=0`. Helper's first Git command hashes `ls-files -s -z` before status.

Read-only shell inspection used `cat`, `sed`, `nl`, `wc`, `rg`, `readlink`, `shasum -a 256`, and Python stdlib JSON/hash/diff processing. Successful read commands exited 0. Programmatic `git show` for the four newly added files returned expected missing-base status (128), recorded as `base_exists:false`; not validation failures. Source-evidence extraction used `python3 -I -S -B` and read the target stdlib as text; it did not run a harness/test/probe. Initial request hash and supplied-input hash checks passed. No supplied output/cache path was replayed.

## Limits, baseline and scores

No harness exists; no future implementation proof is claimed. Tests, package resolution/install/build, conversion, inference, server/service operations, provider calls, stores, network, worktrees, staging, repairs and delegation were excluded and not performed. Root Ruff 534, root test_display collection conflict and registry formatting remain historical FAILED/UNWAIVED debt, not newly reproduced results. Admin green is not whole-repository green.

Python audit enforcement cannot alone guarantee native-code/subprocess containment. This design correctly requires describing its actual boundary and stopping if it cannot enforce it. Future implementation must substantiate that claim with origin/child/negative evidence; current receipt and path contracts do not constitute an OS sandbox. Operator production-offline/restart/log separation and immutable serving identity cannot be inferred from reachability; these are correctly future gated inputs. No separate LM Studio server is required.

Coverage: **10.0/10** — all 16 HRC criteria assessed (6 points), all 12 HR obligations traced (3), exact bounded candidate/authority/preservation/admin evidence covered (1). This is review coverage, not a statement that requirements all pass or that runtime feasibility has been measured.

Overall: **8.7/10** — scope/authority 2.0/2; isolation/effects enforceability 2.0/3 (startup gap); clarity/feasibility 1.9/2; verification/evidence 1.9/2 (startup-negative proof missing); manual usability 0.9/1 (launcher instructions need correction). No inflation to the 9.5 target. One mandatory finding prevents verification independently of score.

Return this single-round result for controller reconciliation. The narrow document correction is recommended, not performed or authorized by this report. No construction, effect activation, acceptance, delivery, replacement council or remediation loop authority is granted.

## Closing integrity

Closing result is appended below after substantive review and report preparation.

Closing boundary PASS, exit 0, 2026-11-11T21:57:36.992104+00:00 (`integrity-closing.json`). Candidate/branch/status/staging, all 17,773 protected files, 24 authority pins and nine preserved records match. Logical index remains `2873bdac566cf50f8c9acf1994aaaf02a23b58a31cc4c06cdb1e828b35ed0d46`. Final request hash matches `651d8edfa6d1afb952418ee393b5f1369eadce2ef6b73eeb63eeb61c37320a44`. No preservation failure.

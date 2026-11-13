# CD-CMD-INGEST-GATE-A-001 — manual readiness harness

Version: **0.3 — corrected DRAFT for council review**, 2026-11-11.
Construction approval: **PENDING**. Stage effects/window: **NOT ACTIVATED / NOT CONFIRMED**.

## Authority and objective

The maintainer authorizes bounded document correction and up to four fresh council
passes through the [current loop authorization](../validation/document-ingestion/gate-a/correction-loop/authorization.md).
This supersedes the earlier one-review-only limit for this paper correction, not
construction/effect permissions. Stop on success or after pass four. No directive
approves its own bytes and no reviewer grants acceptance or implementation.

Build, only after separate exact directive approval, a standalone manual harness
whose versioned code/config/probes/generators/tests live in `tests/readiness/ingest/`
and generated state in `.friday_test/`. It qualifies upstream dependency,
converter/chunker and selected embedding feasibility for the later product
construction directive. It does not implement `/ingest`, Tools adoption, Memory
storage, runtime assembly, test migration or production-guide changes.

| Governing input | SHA256 |
| --- | --- |
| [package-impact-assessment.md](../package-impact-assessment.md) | `f570318f704fe3c5ba29b62860148b45eb31d15243fcf0eb6acd76bc9d218176` |
| [REM-CMD-INGEST-001-pdf-docx.md](../remediation/REM-CMD-INGEST-001-pdf-docx.md) | `5f8978fcd71cb38f561fefcb9e2dd0c263ba97a8551cda97746fad5be2b3bdc7` |
| [test-migration-plan.md](../test-migration-plan.md) | `b422be6964d7dd3a7c464285a43721cea7f9d380edb4ac7817bcd55ff7b9396c` |
| [command-architecture-update-plan.md](../command-architecture-update-plan.md) | `449b3f967318035498577058fd91b14bb04b506c249cd4d53d547695a25d15a1` |
| [guide-update-handoff.md](../guide-update-handoff.md) | `0186c106f91da906213decb53ebc41c311b321ee3db65ed6072d46d641dae5a9` |
| [embedding-compatibility-contract.md](../embedding-compatibility-contract.md) | `1092a332684e3f6a5f9edc3f2355c768775b0f2c01b82bcc97242932334faabb` |
| [tools-document-adoption.md](../proposals/tools-document-adoption.md) | `8220e195f7b9b899fb377f5550920a3d9ac0699b33293a59c366ff6d2fa6d998` |
| [review-criteria.md](../validation/document-ingestion/package-impact/review-criteria.md) | `0bc426c0ed16c0feab720e7b4d597c0de28f924feb58e26945637457bb9aaf62` |
| [round6-authorization.json](../validation/document-ingestion/package-impact/round6-authorization.json) | `b8b23887d51bcccab3bd32ace39fdde33e18e5fdf2abcf85fbc71d21bdd9492b` |
| [readiness-plan.md](../validation/document-ingestion/gate-a/readiness-plan.md) | `94c37e845c0acc4c8f79568c57060dd65df01b20def54abf78c1cf177bba6cd2` |
| [effects-envelope.json](../validation/document-ingestion/gate-a/effects-envelope.json) | `4b6273c2a629affd02e388574a0b1715334456c921611e55e069122f7b0b4315` |
| [isolation-requirements.md](../validation/document-ingestion/gate-a/isolation-requirements.md) | `a50069c9ede478c2387ed819e15cc949223e14bd0635ee9dcc5aa14b0bb60264` |
| [execution-contract.md](../validation/document-ingestion/gate-a/execution-contract.md) | `ac09cc3115640f788fba8f3c29e0b981e18e43ae29846e5fe9585a3099f24a69` |
| [source-observations.json](../validation/document-ingestion/gate-a/source-observations.json) | `bbd408be71036faef3aa5b4298232635a4dade2f2e813444df6aae3a2e63fb80` |
| [consumer-readiness-matrix.md](../validation/document-ingestion/gate-a/consumer-readiness-matrix.md) | `12c2bcc68892f8b5b14023f67d34b190565b7ca22ed79c2a4a9013437c5e9e7c` |

The [execution/evidence contract](../validation/document-ingestion/gate-a/execution-contract.md)
contains normative detailed controls. The plan and envelope bind stages/candidates/
numerical limits; isolation requirements bind production boundaries. The nine
reviewed business inputs remain unchanged. At construction activation, freeze the
source/harness commits, exact directive and full authority/selection manifests.
A changed source/config/envelope invalidates the old run; promotion of explicitly
allowed later manifests follows the append-only ledger instead of changing init.

## Exact proposed edit scope

All executable code is test-only. No new workspace package or application entry point.

| Allowed path | Responsibility |
| --- | --- |
| `tests/readiness/ingest/README.md` | Verified manual setup/workflow, profiles, effective settings, explicit selectors and reports. |
| `tests/readiness/ingest/run.py`, `bootstrap.py`, `startup.py` | Externally verified single stdlib bootstrap, committed-byte sibling loading/guards and core orchestration. |
| `tests/readiness/ingest/config.py`, `paths.py`, `environment.py` | Typed config/paths and qualified no-config/credential/proxy/discovery tool profiles. |
| `tests/readiness/ingest/manifests.py`, `ledger.py`, `export.py`, `protection.py`, `window.py` | Hash-bound manifests/promotions, committed blob exports, preventive/detective evidence and safe loaded-model window. |
| `tests/readiness/ingest/stages.py`, `fixtures.py`, `reports.py` | A0–A4, genuine fixture generation and human/machine evidence. |
| `tests/readiness/ingest/config.example.json`, `requirements.in`, `fixtures/expectations.json` | Test-only schema/seed/independent expected content; model/window and operator metadata permissions unset. |
| `tests/readiness/ingest/tests/test_startup.py`, `test_paths.py`, `test_environment.py`, `test_manifests.py`, `test_ledger.py`, `test_export.py`, `test_protection.py`, `test_window.py`, `test_fixtures.py`, `test_cli.py`, `test_reports.py` | Explicitly selected offline core/profile regressions, simulated roots/server and normal/optimized proof. |
| `.gitignore` | Only root-anchored `/.friday_test/`, before runtime generation; no other ignore change. |
| This directive; the named Gate-A contracts/authorization/evidence; current packet README/authority/next-phase/tactical/handoffs; append-only log; board/dashboard | Bounded requirement, approval, stage/review and evidence records. Frozen historical reports are not rewritten. |

Production package/source/tests, root `pyproject.toml`/`uv.lock`, `.venv`, `.env`,
user YAML, `.friday/`, `.friday-old/`, exports, application databases, model settings
and production `.git` mutations are forbidden. Source object/index observations
are the exact read-only exception in contract section 3, not a working-tree copy.
Served LM Studio assets are used through the confirmed endpoint, never scanned
on disk. No broad staging, user-cache cleanup, service restart or extra source
path is implied. Committed exports stay read-only; metadata rehearsal changes
only a separately named derived overlay. Preserve/report its base/patch/result
and code equality; never claim the overlay shipped.

## Construction versus qualification permissions

Current authority covers corrected documents and read-only councils only.
After exact construction approval, offline C0 harness tests may create test-owned
unit roots, fake repositories/settings/caches/server responses and qualified
interpreter canaries. They may not install dependencies, call a real model, scan
real caches or execute upstream conversion implicitly. Required private validation
tools need their own exact activated offline manifest; do not borrow `.venv`.

A0–A4 effects require separate stage/run/budget/source/promoter activation and
manifest promotion. No runtime facts are inferred from document review. Unknown
flags, artifact/licensing/channel/model facts stop the dependent work. Neither
this draft nor a 9.5 score grants construction, a model window, production
resumption, push, merge or acceptance.

## Required behavior

1. **Trusted startup.** Follow contract section 1 for orchestrator and each private
   profile worker: qualified base/binary/stdlib/launcher, `-I -S -B`, `-O` lanes,
   exact-byte committed imports/guards before third-party code. No cached harness pyc,
   site hooks or path re-open after hashing. Contract1.1 binds all pre-init bytes;
   contract1.2 separately qualifies tool-spawned interpreters with actual trace and
   startup inventories, never pretending they inherit guarded flags or -O.
2. **No-effects preflight/init.** Preflight validates declarations/paths and prints
   deferred checks; no file creation, Git view, network/model/store call. Init
   requires an absent root, then creates owned state and exact committed harness/
   source copies. Pre-init config lives in `.friday_test/control/<run-id>/`.
   Never read dirty working-tree config to complete missing fields. Use the
   operator-approved single bootstrap and complete committed harness manifest
   before sibling execution, then switch to the verified frozen run harness.
3. **Isolated tools/paths.** Contract sections 2–3 define explicit cwd/config/target/
   cache/temp/credential/proxy/discovery suppression, safe paths and private Git
   object view. Leave real HOME unchanged; prove tool-origin neutralization beyond
   environment variables. No production config/global credential lookup or
   working-venv/import fallback. A1 inventories import-time dotenv/config/network
   channels; workers guard reads/probes, bind qualified LiteLLM neutralizers and
   count attempts at transport. Selected-source symlinks/gitlinks/escapes fail.
4. **Bounded containment/evidence.** Contract section 5 distinguishes intercepted
   before-effect prevention from native/child detection and residual limits.
   Cover declared production/default-cache metadata without payload/HOME scans.
   Detected outside changes fail isolation, never become prevention or permission
   to restore user state. Unknown/truncated coverage blocks qualification.
5. **Lifecycle.** Use the immutable init identity, single-writer append-only ledger,
   explicit candidate/promoted states and authorized promotions in section 4.
   No static all-manifests-up-front binding. `all` runs ready stages then exits
   awaiting-promotion/window; no human wait, self-promotion or silent repair.
   Offline prepare-model emits exact candidate batches before window confirmation.
6. **Cumulative budgets.** Preserve every numeric envelope ceiling. Track active
   qualification across resumes separately from human waiting; never reset two
   hours per stage. Reserve/charge uncertain attempts conservatively. Stop only
   owned work, keep evidence and obey existing subcaps/quiescence grace. No process
   or service management of production or LM Studio; stop/expiry gates new requests.
7. **Dependencies/assets.** Follow exact promoted URL/hash/license/platform/profile
   records, binary-only third-party requirements, local assets and private targets.
   Certifi meets the floor after all installation steps. No ambient fetch, unknown
   mirror, remote model code, arbitrary extra or hidden fallback. Fixture and
   validation dependencies are manifest-owned; executable pip is outside scope.
8. **Documents/chunks.** Preserve the plan's at least 30 genuine PDF/DOCX/XLSX/PPTX
   fixtures, independent content/order/table/notes/audit expectations and failure/
   limit cases. Explicit supplied originals are copied read-only, never scanned
   or converted in place. Document/recursive/fixed, 512-token default/overrides,
   full prepared-input limits and non-Docling text/payload coverage remain.
   Preliminary counts and synthetic vectors do not qualify actual model behavior.
9. **Embedding.** Contract section 6 requires an operator-confirmed production-offline/
   restart/log-separated window, exact already-loaded model and safe JIT/TTL/eviction
   conditions, promoted batch/ledger bindings, expiry/revocation, and one version-
   qualified native status profile. Keep the existing endpoint; no new server,
   settings change, loaded-model getter, admin API or authentication discovery.
   Status calls and embeddings share existing budgets. Recheck state around each
   batch and before further requests. Unknown facts block A3, not valid offline work.
10. **Reports.** Explicitly separate attested/observed, prevented/detected, candidate/
    promoted/qualified, executed/inspected/blocked/skipped, scoped/full and active/
    wall/human-wait metrics. Actual upstream and B01–B08 qualification uses run-owned
    clients/config, not full DI/Runtime assembly that could open default stores.
    A0–A4 make no Memory/Chroma/graph/WAL write; product integration stays later.

## Manual interface to implement

These are required interface shapes, **not commands available today**. README
must replace placeholders with verified paths and explain staged multi-invocation
operation, receipts, stop channel and exact exit/status meanings.

```text
<bootstrap-python> -I -S -B <approved-bootstrap.py> preflight --config <control-config> --harness-manifest <approved-manifest>
<bootstrap-python> -I -S -B <approved-bootstrap.py> init --config <control-config> --harness-manifest <approved-manifest>
<orchestrator-python> -I -S -B <run-root>/harness/run.py selftest --config <run-config> --profile minimal
<orchestrator-python> -I -S -B -O <run-root>/harness/run.py selftest --config <run-config> --profile minimal
<orchestrator-python> -I -S -B <run-root>/harness/run.py run --config <run-config> --stage all
<orchestrator-python> -I -S -B <run-root>/harness/run.py promote --config <run-config> --manifest <candidate> --sha256 <digest> --approval <promotion-receipt>
<orchestrator-python> -I -S -B <run-root>/harness/run.py run --config <run-config> --stage A2 --offline
<orchestrator-python> -I -S -B <run-root>/harness/run.py prepare-model --config <run-config> --model-profile <candidate-profile>
<orchestrator-python> -I -S -B <run-root>/harness/run.py run --config <run-config> --stage A3 --window-receipt <window-receipt>
<orchestrator-python> -I -S -B <run-root>/harness/run.py stop --config <run-config> --reason <safe-code>
<orchestrator-python> -I -S -B <run-root>/harness/run.py run --config <run-config> --stage all --window-receipt <window-receipt>
<orchestrator-python> -I -S -B <run-root>/harness/run.py report --config <run-config>
```

The pre-init bootstrap is externally hash-verified and stdlib-only; its complete
approved manifest binds all other executable bytes (contract1.1). Later entries
verify/compile the same bytes they checked; no pyc/path-loader substitution.
Selftest initializes the explicit guard before controlled unit-test discovery;
no bare external discovery bypass. Normal/optimized children inherit the explicit
startup contract, not PYTHON variables ignored by `-I`. Tool-spawned processes
are separately inventoried/observed; no universal child flags or -O claim. Minimal core runs without
Docling/model/provider packages; profile-requiring cases use explicit selectors
and skips earn no format/model proof. Root testpaths excludes `tests/`; README
must show the new selectors, not claim root pytest collected them.

A fresh all invocation emits an A0 candidate then exits awaiting promotion.
The authorized actor reviews/promotes it and resumes all for A1; promote asset/
fixture scope and resume A2. Offline prepare-model freezes a candidate batch,
which is promoted before the operator confirms its window. Resume A3 with that
receipt (or all --window-receipt); A4 aggregates evidence. `all` exits
AWAITING_PREPARATION if explicit prepare-model facts are missing, never prepares
or promotes them itself. stop is lease-free/sticky; report/prepare-model print
exact next receipt hashes. Missing inputs never become an interactive pause
or implicit approval. Report rendering success alone is not readiness PASS.

## Acceptance and future verification

| ID | Required evidence |
| --- | --- |
| HR-01 | Exact test-only code/edit scope and test-owned runtime paths; protected production state unchanged. |
| HR-02 | Manual preflight/init/full/selected/offline/report modes work without an agent; no-effects preflight has no startup/site side effects. |
| HR-03 | Explicit archive path/duplicate/member/expanded-byte/zip-bomb negatives and intercepted paths/imports/config/worker violations refused before effects; native/detective coverage separately proven and bounded. Outside/cache changes fail isolation. |
| HR-04 | Missing/tampered/extra artifacts, unknown hosts/licenses/config origins and stale run binding refused; no setup-failure rejection credit. |
| HR-05 | Window/loaded-state/JIT/TTL/eviction/identity/expiry/revocation negatives yield zero unauthorized calls; valid preloaded simulated flow and exact budgets succeed. |
| HR-06 | Deterministic genuine fixtures plus explicit supplied copies with independent expected content/structure; originals unchanged, errors not stored as content. |
| HR-07 | Three chunk strategies, complete prepared-input 512/override boundaries, source references and real versus preliminary/synthetic qualification. |
| HR-08 | Owned work only; cumulative resource/time/request limits survive resume/crash, stop gates new calls, no server restart or automatic cleanup. |
| HR-09 | Reports explicitly separate operator-attested/observed, prevented/detected, executed/inspected/skipped/blocked, scoped/full and manifest/promotion/budget states. |
| HR-10 | Core startup/import/selftests work with stdlib/harness only; profile workers use explicit private interpreters/sites; no working-venv fallback. |
| HR-11 | Explicit minimal/profile selectors and normal/-O commands; no root-discovery credit for tests/. Conform to a hash-bound isolated copy of root Ruff/format/mypy rules (including typed defs), with no new debt/suppression; activated private tools/config/caches only. Bare pytest or working-.venv discovery fails closed. |
| HR-12 | Stable source/private-target candidate, origins, exact receipts/protected-state evidence and separately authorized fresh implementation review; no UAT/delivery inference. |
| HR-13 | Committed-byte pre-init dirty/extra/pyc/path-swap controls and clean positives in normal/-O; guarded canaries never execute. Tool-spawned site inventory/trace and prelaunch unsafe-site refusal are a separate detective/residual class, with no invented flags. |
| HR-14 | Promotion ledger accepts correct explicit extension/resume, rejects tamper/order/stale hashes/concurrent writers, all exits awaiting prerequisites, and a receipt remains valid across execution-only descendants but not changed scope. |
| HR-15 | Fake parent dotenv, cost-map, credential/proxy channels refused or qualified/neutralized; A1 real-library controls separate from C0 fakes. Record import inventory, tool/system evidence, guarded read/probes and transport retry/request accounting; no personal settings read/alteration. |
| HR-16 | Committed blob export matches selected commit/tree/file object IDs; dirty/untracked/ignored traps excluded; production Git identity unchanged. |
| HR-17 | Simulated native/default-cache change is detected and fails isolation; intercepted refusal and explicit worker-guard positive proof; unknown/truncated metadata coverage refuses. No real protected target is modified. |
| HR-18 | One chosen native status API, already-loaded safe-policy evidence, nonloading request IDs and before/after state controls, with all requests counted and no management/configuration changes. |

Use private test-owned fixtures for every negative control. Required profile tools
and validation dependencies must be exact/pinned and separately activated; missing
tools block the relevant check, never justify using production .venv. Run focused
Ruff/format/type checks with explicit private config/cache, board/dashboard/docs/
metadata, and staged/combined-range whitespace checks in their authorized lanes.
The root rules apply to the new tests/ files too; no root config edit is authorized.
The exact private validation manifest is a C0 prerequisite for HR11, not a license
to borrow tools from production. A missing tool remains blocked and uncredited.
No product suite/live Finance/provider/store call is needed for C0 harness tests.
Preserve historical root debt, never report it waived or freshly green.

## Delivery and stops

Deliver the standalone code, actual manual walkthrough/config/manifest/window
examples, report/status semantics, future proof above and stable local candidate.
Use a separately authorized fresh read-only implementation validator before
claiming the harness implemented/verified. Current document councils do not satisfy
that later implementation gate. Source hashes and authority changes need a new
frozen review; no prior verdict is carried to changed bytes.

Stop on an unapproved source/path/effect, missing model/window fact, unsafe or
unknown tool/cache channel, changed binding, boundary violation, unsupported
upstream requirement or exceeded ceiling. Return exact evidence and the smallest
bounded decision needed. Do not enlarge resource budgets, modify production,
install into .venv, reset stores, repair unrelated debt, push or manage services.

# CD-CMD-INGEST-GATE-A-001 — manual readiness harness

Version: **0.1 — DRAFT for maintainer review**, 2026-11-11.
Work unit: readiness test infrastructure only. Construction approval: **PENDING**.
Execution/model window: **NOT ACTIVATED / NOT CONFIRMED**.

## Authority and objective

Chuck's `proceed` authorizes preparing these bounded instructions and reconciling
the readiness documents. His subsequent direction puts the code for this unit
in the `tests/` subfolder. This draft does not record approval of its own bytes.
Explicit maintainer direction controls, followed by the repository policies and
the pinned parent contracts below. The [validation policy](../../../../reference/policies/independent-validation-policy.md)
requires an approved construction directive before code generation.

Build a standalone harness that Chuck can run without an agent. Qualify exact
dependency installation, genuine document extraction, local chunking and selected
embedding capabilities using disposable test-owned state. Produce reproducible
manifests and readable evidence for the later product construction directive.
The harness does not implement `/ingest`, Tools adoption or framework changes.

| Parent authority | SHA256 |
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
| [readiness-plan.md](../validation/document-ingestion/gate-a/readiness-plan.md) | `c242934407c030d5ded36af9f3a1e2087f5e3f8a5aa11862b6fb32292b53f1cd` |
| [effects-envelope.json](../validation/document-ingestion/gate-a/effects-envelope.json) | `9ffe4bc59dba9d14babb85de661f561d7b14616198f9fd4486e4f03cb4c7641e` |
| [isolation-requirements.md](../validation/document-ingestion/gate-a/isolation-requirements.md) | `ec72dfbe953aa9ad9e0eae0e04e268b2af3142868a9a0883e73e2992178af546` |
| [source-observations.json](../validation/document-ingestion/gate-a/source-observations.json) | `bbd408be71036faef3aa5b4298232635a4dade2f2e813444df6aae3a2e63fb80` |
| [consumer-readiness-matrix.md](../validation/document-ingestion/gate-a/consumer-readiness-matrix.md) | `12c2bcc68892f8b5b14023f67d34b190565b7ca22ed79c2a4a9013437c5e9e7c` |

At activation, freeze the construction-source commit, this directive's hash and
the complete effective authority manifest. A changed parent requirement needs
reconciliation; a prior council verdict is not harness implementation evidence.
The approved impact assessment remains unchanged and need not be approved again.
No council is launched by this directive or the current preparation request.

## Exact proposed edit scope

All versioned executable/test/configuration code for this unit belongs under
`tests/readiness/ingest/`. No new workspace package or runtime entry point.

| Allowed path | Responsibility |
| --- | --- |
| `tests/readiness/ingest/README.md` | Actual setup, manual commands, prerequisites, stage meanings, troubleshooting and report interpretation. |
| `tests/readiness/ingest/run.py`, `bootstrap.py` | Standard-library launcher, explicit preflight/init/run/report operations, frozen run-owned execution. |
| `tests/readiness/ingest/config.py`, `paths.py` | Typed effective configuration, explicit roots, ownership, read/write/import/process boundaries. |
| `tests/readiness/ingest/manifests.py`, `window.py` | Exact dependency/asset/input manifests and operator-confirmed LM Studio window. |
| `tests/readiness/ingest/stages.py`, `fixtures.py`, `reports.py` | A0–A4 orchestration, genuine fixture generation and readable/machine-readable reporting. |
| `tests/readiness/ingest/config.example.json`, `requirements.in` | Test-only configuration with unset model/window facts and exact candidate seeds. No production YAML loading. |
| `tests/readiness/ingest/fixtures/expectations.json` | Deterministic fixture identities and independently declared content/structure expectations. Generated binaries remain untracked. |
| `tests/readiness/ingest/tests/test_paths.py`, `test_manifests.py`, `test_window.py`, `test_fixtures.py`, `test_cli.py`, `test_reports.py` | Offline harness regression/contract tests. No implicit live-model calls. |
| `.gitignore` | Add only root-anchored `/.friday_test/` before runtime generation. No other ignore-policy change. |
| This directive; Gate-A planning/evidence files; current packet README/authority/next-phase/tactical records; append-only execution log; board and generated dashboard | Record approval, exact activation/evidence and review state. Preserve historical gate text and frozen reports. |

Runtime artifacts belong only under the explicitly selected `.friday_test/`
workspace. File/module renames or added source paths return for scope reconciliation
before implementation; do not expand the allowlist ad hoc. The scaffold is a
proposal, not evidence these files exist.

Forbidden edits include `packages/`, root `pyproject.toml`/`uv.lock`, production
tests/configuration/guides, `.venv`, `.env`, `.friday/`, `.friday-old/`, exports,
existing model assets and personal stores. Readiness-only dependency metadata
rehearsals may alter a run-owned source export and must report those diffs; they
never modify the checkout or claim to ship a package change.

## Construction and effects separation

After exact directive approval, construct and validate the harness offline first.
Use simulated endpoint/manifest failures for the harness's own tests. Code approval
does not activate package downloads, dependency resolution, installation, model
assets, conversion or inference. Those require the plan's stage/run-root/budget
activation and exact promoted manifests. Record each permission separately.

Keep the seed requirements aligned with the pinned plan: Docling/RapidOCR,
the Certifi floor and model-bound local counter candidates. Fixture-generation
and validation-tool dependencies must be explicit in the promoted manifest;
never install arbitrary extras or depend on ambient tools. Third-party source
builds remain excluded. No server installation or service management is included.

## Required harness behavior

1. **Preflight and configuration.** Explicit project, run, input, asset, target,
   cache/temp, log and report paths; no production application defaults, YAML,
   credentials or inherited Python paths. Preflight reads metadata and prints
   planned paths/effects, but creates no files and makes no network/model/store
   calls. The example leaves endpoint/model/window facts unset. Essential guards
   use explicit exceptions and work under normal and optimized Python.
2. **Initialization and execution.** `init` requires a new absent run root. It
   binds source/config/manifest hashes, copies the harness and source export and
   establishes owned configuration/state. Execute probes from that frozen copy
   and isolated target, never production packages or the working `.venv`.
   Subsequent explicit stage/report commands may reopen that same owned run only
   if its binding still matches; a fresh assessment uses a new run ID. Never
   silently resume unknown state or reuse a vector store.
3. **Paths and subprocesses.** Enforce the pinned workspace/asset/input publication
   rules, including normalized physical paths, symlink/alias/overlap refusal,
   safe archive members, private caches/temp/logs and child process boundaries.
   Keep a minimal environment allowlist without repurposing HOME. Record module,
   executable and distribution origins before/after probes. Explain the actual
   containment layer and its limitations; Python audit containment is not an
   OS sandbox. A boundary failure prevents functional readiness credit.
4. **Stages and manual modes.** Implement the pinned A0 metadata/inventory, A1
   exact install, A2 converter/chunker, A3 embedding and A4 reporting stages.
   Support full and selected-stage operation plus offline A2 extraction/chunking
   with already qualified dependencies/assets. Each stage verifies prerequisite
   evidence; it does not silently execute prerequisite network/model stages.
   A missing model window blocks A3 without disabling valid offline work.
5. **Dependencies and assets.** Exact platform/version/URL/hash/license/size
   manifests and budgets precede transfer/use. Prove target Certifi meets the
   floor after all installation steps. No ambient asset fetch, global cache,
   backend fallback, unknown mirror or executable model code. Counter and
   embedding preparation must qualify for the selected deployment; preliminary
   counts cannot masquerade as qualified model-bound chunking.
6. **Documents.** Generate the plan's fixed baseline of genuine PDF/DOCX/XLSX/PPTX
   documents and required corrupt/encrypted/empty/partial/limit cases. Bind fixture
   hashes and independent expected text/order/table/notes/audit facts. Explicitly
   supplied real documents are optional supplemental cases, copied read-only
   under their input manifest. Never scan, edit or convert originals in place.
   Distinguish complete extraction, warnings, refusal and unavailable support;
   diagnostic text/placeholders are never treated as extracted document content.
7. **Chunks and embeddings.** Cover document/recursive/fixed, the 512-token default,
   overrides, full prepared-input limits, source references and contextual text.
   Cover the planned non-Docling text/web-payload boundary without inventing a
   maintained URL route. A3 checks real vector count/order/dimensions/finiteness
   and exact role/preparation facts. Synthetic vectors test protocol controls
   only. No Memory/Chroma/graph/WAL write is permitted by A0–A4.
8. **Resources and termination.** Enforce the exact envelope, including child
   processes, admission, timing/memory/disk limits and quiescence. Stop only
   harness-owned work; never kill or restart LM Studio or production. An expired
   window, stop request or changed binding prevents further model batches.
   No automatic cleanup/reset of user state or resumption of production.

## Shared LM Studio window

The maintainer permits the current local endpoint and served model to be reused.
An independent model-server process/port or duplicated served weights is not
required. The operator stops production, restarts the server and separates test
logs. The harness cannot perform those service operations or infer their success.

Before A3, require a structured, run-specific receipt containing:

- Run ID and effective config, dependency, asset and input manifest hashes.
- Exact local endpoint, selected service/model identity, artifact/revision,
  counter/preparation, dimensions and capacity qualification facts.
- Operator identity, production-stop confirmation/time and server-restart
  completion confirmation/time, with available session/restart evidence.
- Log-separation method and test-log destination/evidence. Do not assume an
  unsupported LM Studio log-directory switch or call an admin API to configure it.
- Test-window confirmation and expiry, allowed request/vector/token budgets,
  exact permitted API methods/paths and an explicit revocation/stop state.

Check the receipt before every model batch. Bind live observations where
available and label operator attestations honestly. Reachability or a generic
`--yes` is insufficient; stale, missing, expired, revoked, mismatched or incomplete
receipts block requests. Production stays stopped throughout A3. Do not read the
dirty production YAML to fill missing fields. The operator supplies exact values
to test-owned configuration. No receipt or endpoint is pre-approved by this draft.

Only the activated local embedding/capability API requests and manifested test
inputs are allowed. No management endpoints, other provider, model load/unload,
configuration change, production store or background maintenance. After tests,
report completion; the operator owns production resumption. Endpoint reuse is an
explicit service exception, not a waiver of application/data/config isolation.

## Manual interface to implement

Publish working commands in the harness README after implementation. The following
interface is required but **not runnable today**. Replace placeholders with actual
verified interpreter/config/run paths in the delivered instructions:

```text
<bootstrap-python> -I -B tests/readiness/ingest/run.py preflight --config <test-config>
<bootstrap-python> -I -B tests/readiness/ingest/run.py init --config <test-config>
<test-python> -I -B <run-root>/harness/run.py run --config <run-config> --stage A2 --offline
<test-python> -I -B <run-root>/harness/run.py run --config <run-config> --stage A3 --window-receipt <receipt>
<test-python> -I -B <run-root>/harness/run.py run --config <run-config> --stage all --window-receipt <receipt>
<test-python> -I -B <run-root>/harness/run.py report --config <run-config>
```

Preflight/init bootstrap must be standard-library-only and reject a bootstrap
interpreter inside the working `.venv`. `init` copies the harness; later operations
run that copy. No production-model contact is permitted in preflight/init/report.
Full runs cannot silently treat skipped A3 or unqualified model facts as complete
readiness. Reports may describe a scoped offline pass with the full gate incomplete.

## Acceptance and verification matrix

| ID | Required evidence |
| --- | --- |
| HR-01 | All source/config/tests located under `tests/readiness/ingest/`; runtime output under `.friday_test/`; exact allowlist and production protected-state checks pass. |
| HR-02 | Manual preflight/init/selected/full/offline/report operations work without an agent. Preflight creates nothing and issues no network/model/store request. |
| HR-03 | Guards refuse production/out-of-root paths, aliases/symlinks, unsafe archive members, working-environment imports, global-cache fallback and unowned subprocesses before effects, normal and `-O`. |
| HR-04 | Manifest controls refuse missing/tampered/extra assets/dependencies/inputs, unknown license/host and changed run bindings. Setup/import failures earn no semantic-refusal credit. |
| HR-05 | Missing, false, stale, expired, revoked, mismatched or incomplete window receipts cause zero model calls; a valid simulated window allows only the exact endpoint and budgets. No server-control route is called. |
| HR-06 | Genuine generated fixtures and supplied-document copies have repeatable manifests and independent expectations; originals remain unchanged. Format/limit failures produce explicit outcomes. |
| HR-07 | All three chunking strategies and 512-token/override boundaries are characterized; preliminary versus model-qualified counting is explicit. Real embedding qualification remains conditional on A3 activation. |
| HR-08 | Resource/time/admission/cancellation controls stop only owned work, preserve evidence and prevent subsequent batches after stop/window expiry. |
| HR-09 | Human-readable and JSON reports distinguish executed/inspected/blocked/skipped checks, oracle/baseline defects, fixture results, isolation and full versus scoped readiness. |
| HR-10 | Readiness code imports and its offline unit tests run without Docling/model/provider packages. Optional execution profiles use only their manifest-owned dependencies. |
| HR-11 | README supplies explicit offline test selectors and normal/optimized commands. Root `testpaths` excludes `tests/`; do not claim root pytest discovers the harness. |
| HR-12 | Source and installed/private-target checks, exact receipts, protected-state evidence and required independent implementation review are retained. No product-implementation/UAT/delivery claim is made. |

Run the harness tests explicitly from the frozen run copy, with bytecode off and
temporary paths inside the run. A baseline command shape is:

```text
<test-python> -I -B -m unittest discover -s <run-root>/harness/tests -p 'test_*.py'
<test-python> -I -B -O -m unittest discover -s <run-root>/harness/tests -p 'test_*.py'
```

The minimal lane must cover the core guards and CLI without document/model
packages. Fixture/converter cases needing additional dependencies use explicit
profile selectors; skipped cases earn no HR-06/07 qualification credit.
Tests must make controlled code imports from that copy without weakening path
guards. Cover the bootstrap separately without permitting product imports. Add
focused Ruff/format/type checks for the exact new files using pinned private tools;
run board/dashboard/docs/metadata and staged/range whitespace checks. No unrelated
package suite, live Finance module, provider credential or production process is
needed to validate harness construction. Preserve known failed baseline debt.

## Delivery and stop conditions

Deliver code plus actual setup commands, config/input/window examples, fixture
expectations, scope diff, reproducible reports and a stable local candidate.
Before claiming implementation verified, use a separately authorized fresh
read-only validator against this exact scope; do not launch an unrequested council.
Keep inspection, offline harness execution and activated real upstream/model
qualification separate in evidence. Product integration/tests/guide rewrites stay
in the later INGEST construction directive.

Stop on a production boundary breach, unapproved effect, missing model-window
fact, unsafe dependency/asset, exceeded budget, changed source/authority, new path
or any unsupported upstream requirement. Return concrete evidence and the smallest
required scope/decision change. Never silently relax extraction, isolation or
compatibility requirements. Do not push, install into production, reset stores,
repair unrelated debt or restart services under this directive.

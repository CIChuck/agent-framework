# INGEST-001 — manual readiness harness and production isolation

Version: **0.3 — corrected startup, tool, export, promotion and model controls; not implemented**, 2026-11-11.
The [readiness plan](readiness-plan.md) and [effects envelope](effects-envelope.json)
bind these requirements. Detailed execution semantics are centralized in the
[execution contract](execution-contract.md). No harness, environment, model service or store has been
created or activated by this document.

## Maintainer condition

Chuck requires:

> One thing I want to ensure is that there will be no changes made to the production environment during this readiness test construction unit of work. All code, configuration, test input, and test output should be isolated from the production environment.

This follows the manual-execution requirement and agreement to a project-local
`.friday_test/` workspace. Chuck subsequently permits the existing LM Studio
endpoint to be reused after production is shut down and the server restarted,
with test logs separated. He directs versioned code for this unit into the `tests/`
subfolder. The latest `proceed` authorizes this planning reconciliation and the
bounded harness instructions. The [new four-pass correction authorization](correction-loop/authorization.md)
separately permits document remediation/review. It does not activate inference
or establish shutdown/restart; product/harness construction remains separately approved.

## Production boundary

Treat the working application installation and its stores as production. The
shared LM Studio test-window exception below is explicit; it does not extend to
application files, stores or other services. Do not modify or run the working
package source/test trees, `.venv`, `pyproject.toml`, `uv.lock`, user YAMLs, `.env`, `.friday/`,
`.friday-old/`, exports, application databases, graph/WAL/recovery state, model
configuration, model caches or existing background processes. Production `.git/`
index/refs/config/worktrees must not be mutated; source object/index reads are
limited to the explicitly declared read-only export/boundary contract. Operator-managed
LM Studio restart and transient inference effects during the confirmed test window
are the bounded exception; the harness may not manage that service.

Versioned readiness-only harness, probes, fixture generators, sample test
configuration, manifests and harness tests belong under `tests/readiness/ingest/`,
as listed by the proposed construction directive. They must remain separate
from production packages and execute from a frozen copy in the test run root.
Source export and existing-input reads are explicit, read-only preparation
operations; they never authorize modifying their originals. Export only selected
blobs from recorded commits via the private Git view, not a working-tree copy. Production modules
must not be imported from the live checkout or working `.venv` by a test process.
This planning clarification changes only planning documents and current metadata.

## Test workspace

Resolve the project root explicitly; do not derive destinations from the shell's
current directory or an application default. Use:

```text
<project>/.friday_test/
  inputs/
    generated/
    supplied/
  assets/<manifest-sha256>/
  control/<run-id>/         # Pre-init configuration and later promotion/window inputs
  runs/<run-id>/
    harness/
    source-export/
    source-git/             # Private read-only object view/config, not a worktree
    target/
    config/
    wheelhouse/
    cache/
    fixtures/
    vector/                 # Reserved for later approved integration tests
    graph.json              # Reserved for later approved integration tests
    state/
    logs/
    reports/
```

Init requires a new absent run directory. Later explicit commands may reopen only
that owned hash-bound run after validating the append-only promotion ledger; new
manifests extend that ledger through explicit promotion, not identity mutation. Validate ownership of an existing
test workspace before creating a run. Resolve all read/write roots, check each
ancestor and refuse aliases, symlinks or overlapping production destinations.
Probe processes may write only within their approved run root; verified input
and asset directories are read-only during probes. The promoted A2 publisher may
create one new shared manifest asset directory from verified run-local staging;
it must never overwrite an existing directory. Explicit input preparation may
likewise publish a new manifest-named generated/supplied input directory from
run-local staging; existing inputs and originals are never overwritten. No output path, log handler,
database, cache or subprocess may fall back to production defaults.

All dependency installs, builds, generated code/configuration, Python bytecode,
temporary files, UV/XDG/Hugging Face/Transformers/Torch caches, logs, extracted
text, chunks and reports belong to the run. Set dedicated cache/temp directories
without repurposing HOME. Use an explicit environment allowlist; do not inherit
application configuration, provider credentials, Python paths or proxy settings.
Use qualified `-I -S -B` startup for every Python entry/worker and explicit private
imports; no ambient site hooks or `.pth` processing. Neutralize each tool's user/
system config, credentials, proxy and parent-discovery channels, not just env vars.
Model calls and network access require their stage-specific destination allowance.

Keep `.friday_test/` out of Git through an explicit ignore rule in the future
approved harness scope, before generating files there. Git retains harness
sources, generators, manifests and sanitized reports only; supplied documents,
models, environments and local results are not committed. The test workspace
is persistent for manual inspection, but each run is independent. Reuse assets
only after manifest/hash verification; never silently reuse a Chroma test store.
Cleanup may target only identified test-owned state and is never automatic
cleanup, reset or migration of production data.

## LM Studio reuse while production is offline

The maintainer permits the existing endpoint and served model to be reused. A
separate LM Studio process/port and copied served-model weights are not required.
This supersedes the earlier independent-service restriction only for the shared
model service. Production application state is never part of the test workspace.

The operator must first stop the production application, restart LM Studio for
testing and establish separated test logs. Before any model request, a receipt
must bind run ID, endpoint, model identity/artifact/counter facts, effective
configuration/input/asset hashes, operator identity and confirmation times,
server-restart evidence, log-separation method/destination and window expiry.
Create the receipt only after its promoted inputs/batch/ledger hashes exist. Bind
the already-loaded model and safe JIT/TTL/eviction settings. A selected qualified
native status profile checks loaded state around batches; a downloaded listing
is insufficient. All status requests count toward the same call budget.
Record what the operator attests versus what the harness can observe. A mere
reachable endpoint or `--yes` flag cannot establish the prerequisites.

The harness must neither stop/start/restart LM Studio or production nor invoke
model-management APIs. It may issue only the explicitly allowed model/capability
requests inside the confirmed window and budgets. Production remains stopped
throughout. Window expiry, revocation or a changed model/config/input/manifest
requires new confirmation before further batches. No automatic fallback to a
different endpoint, production profile, credential or model is permitted.

Bind and verify the actual log-separation mechanism; do not invent support for a
server log-directory flag. Test logs retained by the harness belong under the run
root. If production/test log separation cannot be established, A3 is blocked.
Existing immutable served-model assets may remain where LM Studio keeps them;
the harness does not scan, change or copy that model directory. Operator-supplied
model identity must still qualify; endpoint reuse does not prove token/dimension
or preparation compatibility. Docling/OCR/tokenizer assets remain test-owned.

No window receipt is recorded by this planning update. Production shutdown,
server restart, model calls and production resumption have not been performed by
the agent and must not be inferred from future-tense instructions. The operator
owns resumption after tests. Offline stages can run under their own activation
without this window. Same-host resource effects are bounded, not eliminated.

## Controlled and supplied documents

Generated fixtures remain the repeatable baseline with known source content,
hashes and expected extraction/chunking results. Accept real documents only from
an explicitly supplied input manifest. Copy them read-only into the test workspace
before conversion; never convert in place, scan production stores or write
sidecars alongside the originals. Record expected passages/tables/questions and
preserve original hashes/metadata. Apply the same admission/resource limits.

Supplied content may reach only the explicitly activated local LM Studio endpoint
during the confirmed production-offline window; no external provider or upload is permitted. Reports containing source
text remain private unless a separately selected sanitized summary is retained.
No supplied documents are selected by this planning update.

## Manual operation and evidence

The harness must run without an agent and document exact setup, configuration,
prerequisite, full-run and individual-stage commands. The CLI does not exist yet;
publish working commands only after implementation. Offline extraction/chunking
must run without model access. Embedding requires the confirmed shared-endpoint window and
model qualification inputs. Dry-run/preflight must make no network/model/store
calls and must show effective paths, planned effects and skipped/blocked stages.

Reserve the isolated vector/graph/state paths for later approved command-to-store
integration tests. A0–A4 currently qualify upstream feasibility and make no Memory
store writes. Fresh test stores never reset, attach to or migrate production data.

Refuse controlled Python/path/config/startup/receipt violations before their
intercepted effects. Separately classify native/non-Python prevention and detection
as contract section 5 requires. Do not promise universal before-effect prevention
from Python audit hooks. Bounded before/after snapshots cover explicitly declared
production state and tool/library default caches without reading cache/model
payloads or scanning HOME. Missing/truncated coverage or an unknown default channel
blocks that profile. Detected outside writes fail isolation and stop the run;
they are neither prevented nor excused, and no automatic restoration is allowed.

Require normal/optimized startup canaries, positive and negative controlled
profiles, explicit child guards and fake-default-cache detection witnesses under
test-owned roots. Never plant a real canary or deliberately write in production.
If the approved boundary cannot be substantiated, stop without isolation credit.

Record opening/closing protected-state checks, effective path/import origins,
dependency/asset versions and hashes, endpoint/process identity, resource use and
per-stage passes/failures/skips, candidate/promoted state and cumulative active
time versus human waiting. Record operator-attested versus observed fields and
preventive versus detective controls explicitly. Report reproducibility and isolation separately
from functional correctness. A passing fixture does not excuse a boundary breach.

# INGEST-001 — manual readiness harness and production isolation

Version: **0.1 — requirements recorded, not implemented**, 2026-11-11.
The [readiness plan](readiness-plan.md) and [effects envelope](effects-envelope.json)
bind these requirements. No harness, environment, model service or store has been
created or activated by this document.

## Maintainer condition

Chuck requires:

> One thing I want to ensure is that there will be no changes made to the production environment during this readiness test construction unit of work. All code, configuration, test input, and test output should be isolated from the production environment.

This follows the manual-execution requirement and agreement to a project-local
`.friday_test/` workspace. These clarify the readiness scope; they do not approve
product construction, effects execution, new dependencies or a council.

## Production boundary

Treat the working application installation and its live services as production,
including local LM Studio. Do not modify or run the working package source/test
trees, `.venv`, `pyproject.toml`, `uv.lock`, user YAMLs, `.env`, `.friday/`,
`.friday-old/`, exports, application databases, graph/WAL/recovery state, model
configuration, model caches or existing background processes.

Versioned readiness-only harness sources, fixture generators and manifests may
be added only within the exact future harness scope. They must remain separate
from production packages and execute from a frozen copy in the test run root.
Source export and existing-input reads are explicit, read-only preparation
operations; they never authorize modifying their originals. Production modules
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
  runs/<run-id>/
    harness/
    source-export/
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

Every run directory must be new and absent. Validate ownership of an existing
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
Model calls and network access require their stage-specific destination allowance.

Keep `.friday_test/` out of Git through an explicit ignore rule in the future
approved harness scope, before generating files there. Git retains harness
sources, generators, manifests and sanitized reports only; supplied documents,
models, environments and local results are not committed. The test workspace
is persistent for manual inspection, but each run is independent. Reuse assets
only after manifest/hash verification; never silently reuse a Chroma test store.
Cleanup may target only identified test-owned state and is never automatic
cleanup, reset or migration of production data.

## LM Studio separation

The same model identity may be qualified in a test service. The production
LM Studio endpoint, process and settings are excluded. A separate port alone
does not establish isolation: record an independently owned test process or
server, its endpoint, private data/config/log/cache paths and exact model facts.
No readiness probe may start, stop, reload, switch models in or send requests to
the production service. Reusing it would change its queue, logs and potentially
caches even if its configuration remained unchanged.

Obtain any model assets for the test instance only through the explicit promoted
manifest and activation. Never scan, modify or copy a personal model directory
by inference. Explicitly supplied model files may be copied read-only into the test asset root
only after their source paths/digests and copy allowance are bound. Probes and the
test service use those isolated copies, not production model files; caches and
generated state also belong to the test instance. No model download or test-service startup
is authorized by this requirements record.

If an isolated instance cannot be established, A3 stays blocked. A0/A1 and offline
A2 may proceed only under their own activation. Synthetic vectors can test the
harness protocol but cannot establish real embedding-model readiness. Shared-host
CPU/RAM/disk contention remains possible; resource limits apply. A guarantee of
zero production performance impact requires separate hardware and is not claimed
for a same-host test directory.

## Controlled and supplied documents

Generated fixtures remain the repeatable baseline with known source content,
hashes and expected extraction/chunking results. Accept real documents only from
an explicitly supplied input manifest. Copy them read-only into the test workspace
before conversion; never convert in place, scan production stores or write
sidecars alongside the originals. Record expected passages/tables/questions and
preserve original hashes/metadata. Apply the same admission/resource limits.

Supplied content may reach only a separately activated local test embedding
service; no external provider or upload is permitted. Reports containing source
text remain private unless a separately selected sanitized summary is retained.
No supplied documents are selected by this planning update.

## Manual operation and evidence

The harness must run without an agent and document exact setup, configuration,
prerequisite, full-run and individual-stage commands. The CLI does not exist yet;
publish working commands only after implementation. Offline extraction/chunking
must run without model access. Embedding requires explicit test-endpoint and
model qualification inputs. Dry-run/preflight must make no network/model/store
calls and must show effective paths, planned effects and skipped/blocked stages.

Reserve the isolated vector/graph/state paths for later approved command-to-store
integration tests. A0–A4 currently qualify upstream feasibility and make no Memory
store writes. Fresh test stores never reset, attach to or migrate production data.

Before effects, fail closed on a production path/endpoint, missing explicit test
configuration, out-of-root write, live-checkout import, global-cache fallback or
unowned process. Require negative witnesses for these cases, child-process
coverage and normal/optimized execution. Describe the actual containment layer;
a Python audit guard is not an OS sandbox. If the boundary cannot be enforced,
stop rather than certify isolation from intent alone.

Record opening/closing protected-state checks, effective path/import origins,
dependency/asset versions and hashes, endpoint/process identity, resource use and
per-stage passes/failures/skips. Report reproducibility and isolation separately
from functional correctness. A passing fixture does not excuse a boundary breach.

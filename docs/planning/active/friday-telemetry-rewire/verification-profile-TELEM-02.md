# Approved TELEM-02 verification profile

Status: approved by Chuck Russell. Date: 2026-10-06.
Bound to [CD-002](directives/CD-002-otel-adapter-lifecycle.md) and its exact manifest.
Accepted TELEM-01 profile remains immutable historical/unit-specific authority.

## Isolated execution and baselines

Use a fresh stable tracked snapshot with protected tracked runtime artifacts omitted
before checkout (same267-file omission set if unchanged); never copy/read original
.env, .friday, Chroma, transcripts, credentials or unrelated dirty files. Verify
omissions do not intersect source/config/tests. All source imports must resolve the
snapshot, not editable original paths. Freeze full imports/conftests/helpers and
synthetic subprocess/transport preflight before collection. Compare preparation
basee8b075a and final candidate with identical installed tools/settings and safe
source effects; new-source-only checks are explicitly absent on baseline.

Use installed Python3.13.10, Ruff0.14.10, Mypy1.19.1 and existing SDK/exporter1.39.1;
record actual versions plus grpc/protobuf. No installs/sync/downloads/builds.
Allowlisted environment: offline/no-sync/no-download uv with original installed
.venv read-only, private temp/cache roots, PYTHONDONTWRITEBYTECODE=1,
LITELLM_LOCAL_MODEL_COST_MAP=true, ANONYMIZED_TELEMETRY=False. No HOME override,
provider credentials/live flags/OTEL_*/GRPC_*/proxy/certificate settings. PYTHONPATH:
unchanged external network guard, all isolated */src, Chat tests_chat helper, root.
Native gRPC bypasses some Python socket hooks: do not claim the guard alone proves
no egress. Preflight and intercepted constructor target/options must prove both new
collector tests use literal127.0.0.1 ephemeral targets and no inherited settings.
Under approved [A02](directives/CD-002-A02-native-retry-disable.md), assert the exact
channel options on mocked insecure/secure branches and both existing native nodes:
grpc.enable_http_proxy=0, grpc.enable_retries=0 and bounded send/receive sizes.
Verify one public Export call per batch, finite timeout and wait_for_ready=False.
No additional native retry fault-injection experiment is required or authorized.

Before full suites, freeze all13 synthetic listener node IDs (existing11 plus the
exact2 named in CD-002), server/client constructor/teardown/helper hashes, allowlist,
expected effects and native guard limitation. Only approved normal-user sandbox
escape for those effects; no sudo or nonloopback test traffic. Static endpoint
config negative tests must mock construction before SDK opens a channel. All HTTPS
credential/secure-channel construction is mocked: assert root_certificates,
private_key and certificate_chain are each None, native-default-public-root policy,
ordinary hostname verification, approved options and no plaintext fallback. Reject
certificate/env override keys before construction and prove no custom-file/credential
loader calls. No real TLS handshake, remote channel, certificate provisioning or native
trust-store loading occurs in this unit's tests. The production contract explicitly
allows runtime-selected bundled/system public roots; Python guards and these mocks
do not prove native filesystem behavior. Protobuf tests cover both signed64-bit
integer boundaries and rejected overflow/unencodable strings before SDK/encoder logging.

## Mandatory checks

Run against the stable candidate with uv run --no-sync (offline/no-sync env above):

```text
pytest packages/friday-telemetry/tests_telemetry/test_otel_contract.py packages/friday-telemetry/tests_telemetry/test_telemetry_factory.py packages/friday-telemetry/tests_telemetry/test_otlp_collector.py packages/friday-telemetry/tests_telemetry/test_mcp_telemetry.py
pytest <six original CD-001 telemetry-focused modules>
pytest packages/friday-chat/tests_chat packages/friday-telemetry/tests_telemetry -rA
pytest --import-mode=importlib --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py --ignore=packages/friday-llm/tests_llm/test_live_lmstudio.py --collect-only
pytest --import-mode=importlib --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py --ignore=packages/friday-llm/tests_llm/test_live_lmstudio.py -rA
pytest --import-mode=importlib <all aggregate owning test trees> <same two --ignore arguments> -rA
ruff check <exact CD-002 changed Python files>
ruff check <exact 2155a0f-to-candidate aggregate changed Python files>
ruff check .
mypy --python-version 3.13 <exact CD-002 source files>
mypy --python-version 3.13 <exact 2155a0f-to-candidate aggregate changed source files>
python scripts/friday-dev-board.py validate
python scripts/check-documentation-lifecycle.py
```

The six original focused modules are the five Chat telemetry/CLI/runtime/app/
config-compatibility files and telemetry test_providers.py listed in CD-001.
Expand every placeholder into pinned exact paths before execution; new files add
seven unit source and twelve unit Python targets if the approved manifest is fully
used. Regenerate aggregate counts, do not retain old98/63 lists. Parse all changed
Python via ast.parse(feature_version=(3,13)). Run genuine synthetic Chat observer,
Composite and managed OTel lifecycle, concurrency/negative consumer and scalar/
privacy/API compatibility probes, including old/current registry invariance.
Record each check separately, including intended negative diagnostic identities.

Native `uv lock --offline --check --no-python-downloads --no-build` must pass with
unchanged lockfile, all18 project floors and frozen dependency selection hashes.
Run selected delta and aggregate git diff --check. No exact3.13.4 interpreter or
Python3.10 run/download is required. Missing SDK/optional dependencies are covered
by scoped import mocks, not installs or silent skips. Optional SciPy/live-gated
baseline skips may remain only at unchanged existing nodes/reasons; any new skip
or failure is a finding. Require both full root and Chat commands to exit zero.

## Lint, typing, baseline and review disposition

At original preparation basee8b075a, root Ruff exits1 with579 findings:327
original debt plus252 raw closeout-script findings. The evidence-only packaging
correction preserves all18 scripts byte-for-byte in gzip, with original manifests
retained. The candidate must reproduce327 after this correction, never
waive the additional252. Record both raw results and the exact compression proof.
The corrected327 are separately approved current-unit debt under WVR-004. Independently match
its327 exact identities, four archive hashes, unchanged registry source/AST,
seventeen lint-config hashes, Ruff version and py313 at baseline/final. Every other
finding fails; no global exclusions/ignore changes. Raw root lint is never called
PASS. Both changed-unit and aggregate Ruff must exit0 (registry remains unchanged
and therefore absent from changed targets). Mandatory typing fixes include removing
otel.py's existing whole-file ignore; no typing/syntax/API exception is proposed.

Evidence includes actual command/cwd/revision, env names/nonsecret values, expanded
paths, source-resolution and SDK hashes, excluded live modules, node IDs, collection
counts, every failure/skip, timestamps/exits, logs, raw lint multiset and dispositions,
tracked-before/after preservation, transport targets/cleanup and cancelled/timeout
outcomes. Historical accepted validation is retained as history, not substituted for
new candidate gates. Documentation-only proposal checks are not product verification.

Freeze separate current-unit authority manifest and stable delta/aggregate requests.
Fresh independent readiness follows approvals; separate builder then fresh product
validator. Accepted TELEM-01 evidence and expiry decisions are never rewritten.

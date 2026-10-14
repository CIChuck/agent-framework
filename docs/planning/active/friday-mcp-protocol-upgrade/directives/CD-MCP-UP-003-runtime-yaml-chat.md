# CD-MCP-UP-003: Runtime, YAML and Chat MCP integration

Status: **Proposed; maintainer approval pending.** Prepared 2026-10-12.
Initiative: `friday-mcp-protocol-upgrade`; work unit: `MCP-UP-03`.

## Authority, objective and baseline

Connect the accepted MCP clients to the real headless Runtime and Friday Chat
through `tools.providers.mcp.config.servers` in config.yaml. Deliver explicit
modern/auto stdio selection and Streamable HTTP 2026-07-28 /2025-11-25 selection,
with strict per-transport config, remote policy, credential references, admission,
owned lifecycle and untrusted call handling. Match all applicable mandatory rules
of the already pinned MCP **2026-07-28** tools/transport client profile and its
explicit **2025-11-25** HTTP compatibility profile. Runtime integration and SDK
interop do not claim optional-feature, OAuth or whole-initiative conformance.

Apply [AGENTS.md](../../../../../AGENTS.md), its engineering/lifecycle/independent
validation policies, approved [build plan](../build-plan.md), [protocol contract](../protocol-contract.md),
[tactical plan](../tactical-plan.md), [conformance matrix](../conformance-matrix.md),
all prior frozen manifests and accepted MCP/telemetry contracts. This exact
[UP-03 integration contract](../up03-integration-contract.md) and
[verification profile](../verification-profile-UP-03.json) bind this directive.
The [proposal manifest](../proposals/UP-03-authority-manifest.json) pins all inputs,
28 exact product paths and baseline; it grants no construction authority.

Chuck Russell accepted corrected HTTP MCP-UP-02B with “accepted proceed” on
2026-10-12. [Exact acceptance receipt](../acceptance/MCP-UP-02B.json),
[accepted-unit archive](../../../../archive/completed/2026/friday-mcp-protocol-upgrade-up-02b/README.md)
and [independent VERIFIED report](../validation/VAL-UP02B-02/report.md) remain
immutable. Product baseline/closeout commit is
`4dfc2c69eedef3017d7af42daa3341de1ad55038`; reviewed HTTP candidate is
`14dba178feff8789111db88d981f1d0e85e6a748`. Earlier stdio/core unit is accepted.
Use branch `feature/friday-mcp-protocol-upgrade` and a private sparse snapshot.

Before source edits obtain exact approval of this directive/contract/profile/
manifest; record a separate receipt and approved execution manifest without
rewriting these proposed controls. Run board validate/next/show and check
started/granted/named branch, current UP-03 unit authority and every input hash.
Acceptance of HTTP and instruction to proceed with planning do not approve an
unseen later construction directive.

## Exact product scope

Existing 24 paths; edit only for requirements below:

- `packages/friday-core/src/friday_core/mcp.py`
- `packages/friday-core/tests_core/test_mcp_contracts.py`
- `packages/friday-mcp/src/friday_mcp/client/manager.py`
- `packages/friday-mcp/src/friday_mcp/client/__init__.py`
- `packages/friday-mcp/tests_mcp/fixtures/http_sdk_server.py`
- `packages/friday-mcp/tests_mcp/fixtures/http_compat_server.py`
- `packages/friday-mcp/README.md`
- `packages/friday-runtime/src/friday_runtime/config.py`
- `packages/friday-runtime/src/friday_runtime/mcp_loading.py`
- `packages/friday-runtime/src/friday_runtime/mcp_registration.py`
- `packages/friday-runtime/tests_runtime/test_mcp_runtime_config.py`
- `packages/friday-runtime/tests_runtime/test_mcp_loading.py`
- `packages/friday-runtime/tests_runtime/test_mcp_registration.py`
- `packages/friday-runtime/README.md`
- `packages/friday-chat/src/friday_chat/config.py`
- `packages/friday-chat/src/friday_chat/tools/mcp.py`
- `packages/friday-chat/tests_chat/test_mcp_config_compatibility.py`
- `packages/friday-chat/tests_chat/test_mcp_chat_bridge.py`
- `packages/friday-chat/tests_chat/test_mcp_execution_security.py`
- `packages/friday-chat/README.md`
- `packages/friday-chat/src/friday_chat/config_templates/config.example.yaml`
- `packages/friday-chat/src/friday_chat/config_templates/cli-config.example.yaml`
- `docs/guides/10-configuration.md`
- `docs/guides/17-mcp-client.md`

New four paths:

- `packages/friday-runtime/src/friday_runtime/mcp_clients.py`
- `packages/friday-runtime/tests_runtime/test_mcp_http_integration.py`
- `packages/friday-chat/tests_chat/test_mcp_http_integration.py`
- `packages/friday-mcp/tests_mcp/client/test_manager_profiles.py`

Authority/approval/acceptance, board/dashboard, separately referenced current
process state, execution log, planning/build/review evidence and normative ledger
are process paths. Preserve all old frozen bytes, including the initiative index.
No dependency/lock/metadata edits, HTTP transport/parser/policy or stdio/SSE
source edits, Friday-server work, RuntimeKernel refactor, Chat turn/selection
refactor, telemetry/provider changes, memory/transcript source edits, CLI command,
external config includes or queued tool-manifest continuity implementation.
Do not edit the user's dirty packages/friday-chat/config.example.yaml or audit/
local-state files. Packaged templates above supply clean supported examples.

## Required behavior and architecture

Implement the exact [integration contract](../up03-integration-contract.md).
It expressly amends only Core integrated_transport/trust_posture and tool
transport metadata for explicit remote admission; local defaults and all privacy
and workspace restrictions remain. The directive supplies no general exception
to FridayV2 parity boundaries or unrelated accepted security policy.

1. Validate a strict transport union before effects. Preserve absent-transport
   stdio/legacy defaults. Add explicit stdio protocol_profile and explicit dated
   HTTP protocol_version; forbid mixing process and remote fields. Remote entries
   require trust_level:remote, HTTPS, auth selection and canonical per-peer network
   policy. Enabled HTTP additionally requires the matching global remote opt-in.
2. Keep environment references unresolved through YAML/load/validation/model_dump.
   Resolve one explicitly named credential only at enabled connection assembly.
   Prevent Chat's generic interpolation from expanding credential_env. Invalid
   config/token/URL/errors never echo supplied values or unsafe exception chains.
3. Use the accepted actual-connect endpoint policy backend unchanged, with
   production fixture-http permission false, verified TLS/original hostname,
   per-peer address/port enforcement on every connection and no redirect/proxy/
   cookie behavior. No once-only DNS check or injected arbitrary HTTP client.
4. Implement the typed public managed-server factory seam and Runtime construction
   module specified in the contract. Preserve legacy manager APIs; reject duplicate
   factories/config ambiguity before I/O. Manager adopts clients before await,
   owns adapters and exact original-name routing. No private attribute injection.
5. Pass lower-only protocol limits and single new-profile startup/call deadlines.
   HTTP startup retries are zero; only existing stdio connection retry behavior
   remains. Never replay tools/call. Preserve 2025 session generation recovery and
   modern cancellation by reusing the verified transport, rather than duplicating
   their state machines in Runtime.
6. Preserve complete discovery/atomic registration, canonical name/collision/filter/
   budget decisions, workspace scope, required/optional peer behavior, rollback,
   idempotent public stop and retained cleanup ownership. Populate real remote
   transport/trust in safe provenance. Preserve primary failures and cancellation.
7. Admit only the two narrow schema additions described in the contract: canonical
   root 2020-12 declaration and validated modern HTTP header annotations. Validate
   using the accepted pure header_bindings helper before stripping protocol-only
   schema fields from model exports. Preserve original client wire bindings, scalar
   validation and exact Unicode/Base64 encoding. Keep all earlier unsupported
   schema features rejected. Recount raw and exported byte/token admission costs.
8. Real Chat must select and execute admitted remote tools through its existing
   registry/turn path. Preserve exact routing, downstream result sanitation,
   quarantine/provenance/transcript association, explicit memory opt-in and native
   tools. Supply safe failures for unsupported/input-required/invalid/tool-error
   results, with no link/resource retrieval or interactive continuation.
9. Keep provider-neutral TelemetryInterface and accepted correlation/observation
   lifecycle. No duplicated logical observations or global exporter/provider/
   tracing changes. Credentials and raw peer/application data stay out of evidence
   and operational diagnostics. Langfuse remains queued after full MCP acceptance.

## Dated research and clause proof

Use the complete frozen [modern sources](../research-sources/manifest.json) and
[additional dated sources/schemas](../research-sources/up02b/manifest.json).
The authoritative [modern Streamable HTTP specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)
and [2025 compatibility transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
remain pinned by capture hashes. Both schema captures are pinned to upstream
commit `271ecc9accafdd9b83a3c869fa67c22953b2af80`. No moving latest URL changes
this target; any specification revision requires a separate authority amendment.

Review all 18 complete captures and original clause/schema ledgers, not snippets
or SDK claims. Before product edits produce an UP-03 mapping of every applicable
mandatory clause/selected schema field to INT-AC-01..10 and planned positive/
negative evidence. Distinguish terminological MUST/SHALL occurrences, server-only
and nonadvertised optional duties, accepted transport proof and new assembly
obligations. At candidate freeze replace planned evidence with actual source/
test/receipt references. Unexplained mandatory exclusions block validation.

## Acceptance criteria and required tests

| ID | Required positive, negative and regression proof |
| --- | --- |
| INT-AC-01 | Both real YAML loaders retain identical canonical config; legacy stdio default and explicit modern/auto; explicit modern/2025 HTTP; discriminator/unknown/mixed fields, booleans-as-integers, invalid disabled/required configs fail before factory/DNS/subprocess/credential lookup |
| INT-AC-02 | Both global/per-peer remote opt-ins; default HTTPS/443/public policy; exact private-address/port opt-ins; userinfo/query/fragment/insecure/mapped/wildcard/CIDR/mixed-DNS rejection; actual connector receives validated address and original TLS hostname on changing DNS |
| INT-AC-03 | none/bearer_env behavior; unresolved literal references in both loaders/dumps; missing/empty/control/oversized token fails safely; disable/auto_connect=false makes zero lookups; reconnect resolves only named synthetic reference; token/header/URL/error sentinels absent from errors, chains, logs, telemetry and stored provenance |
| INT-AC-04 | Public typed factory/manager APIs; default programmatic stdio/SSE compatibility; exact profile and lower-limit binding; manager adoption before partial startup; mixed peers and distinct factories; duplicate/malformed factories never invoke; borrowed providers and existing public imports preserved |
| INT-AC-05 | Real headless Runtime startup/discovery/transactional registration/call/stop for both HTTP revisions; complete required/optional peer outcomes; canonical naming, native/MCP collisions, include/exclude and25/50/8192/token caps; valid root dialect/header annotation stripping without mutating wire catalog; malformed annotations/unsupported admission schemas produce safe rejection |
| INT-AC-06 | Real Chat YAML+public runtime factory -> start -> existing per-turn selection -> remote call -> sanitized model result -> atomic safe provenance/transcript -> stop; both dated revisions; native tools/count/token/result limits unchanged; required/optional failure, malicious output/quarantine, memory disabled/explicit opt-in and absent automatic peer instructions |
| INT-AC-07 | One new-profile deadline across connect/discovery/recovery; exact issued tools/call count one under ambiguous drop/status/session/cancellation/timeout; zero HTTP outer retry; multiple concurrent calls with late old404 preserve a healthy recovered peer; primary failures and cleanup ownership remain observable |
| INT-AC-08 | Public Runtime/Chat partial startup/registration failure/repeated stop/retry release only owned tools/tasks/pools/streams/children, never replace incomplete owner or close borrowed provider; cancellation-resistant cleanup and native registration preservation are inspected, not inferred from connection flags |
| INT-AC-09 | Existing TelemetryInterface recorder injection observes one logical call lifecycle with correct correlation/outcome and safe metadata; disabled telemetry and borrowed provider unchanged; no ambient/global provider mutation or outgoing trace/baggage; no duplicate observation through2025 recovery |
| INT-AC-10 | Complete18-source clause/schema reconciliation, real wire counterparts, exact 28-path and dependency/control/artifact preservation, accurate disabled/default and both-profile docs/examples; full required profile with independently reproduced inherited debt/skips; fresh independent unit VERIFIED |

Exercise both public application entry points, not only manually constructed
provider objects or parser tests. Keep Core/MCP/Runtime/Chat/Telemetry source
boundaries through typed public contracts. New fixtures use only synthetic tools,
results/counters and generated private CA/TLS material; counterpart SDK remains
pinned fixture-only mcp 2.3.0. Extend the two existing named HTTP peers for verified
TLS, authenticated synthetic-match facts, exact headers/counters and malformed/
ambiguous replies using existing locked public APIs; no new dependency or parser.
No model/provider invocation is needed: existing controlled application service
factories and deterministic model replies exercise the real MCP registration,
selection/execution and safe persistence boundaries.

## Verification, effects and inherited debt

The exact argv/order/check IDs are in [verification-profile-UP-03.json](../verification-profile-UP-03.json).
Use the existing private Python 3.13.10 environment, current locked versions,
private HOME/cache/TMP, offline/no-sync and the unchanged guard/runner hashes.
Use a new preserved accepted pre-UP03 baseline, not the pre-HTTP baseline.
Before every execution freeze current source, full argv/environment/guard hashes
and the pre-inventoried fixture effects. All child exits and full raw streams are
retained. Do not infer success from the orchestration runner's own exit code.

Planning baseline: all eight existing touched source files pass narrow Ruff and
Mypy. Full Core/MCP/Runtime/Chat Mypy checks 109 files and exposes exactly four
inherited no-any-return diagnostics in untouched friday_core/profiles.py.
Construction must keep touched/new source clean and compare full diagnostics
against this exact baseline, without new ignores/casts or lowering checker rules.
Root Ruff's 327 inherited complete diagnostic/fix objects remain a separately
reported exact baseline; no added/removed object or newly waived failure. Root
pytest must pass and its exact skip reasons/warning sections must match the
accepted baseline. Existing live LM Studio/scipy skips remain separate from
synthetic proof. Any new deterministic failure blocks completion.

Permitted construction/verification effects, only after exact approval: private
sparse snapshots with protected paths excluded before checkout; the two named
HTTP fixture children on allocated literal127.0.0.1 HTTPS ports, private generated
CA/cert/key; existing named synthetic stdio peers and original cross/root
loopback/private-store fixtures; controlled resolvers/connectors with no public
connection; only explicitly installed synthetic credential mappings/references
and deterministic model/service doubles. Test TLS keeps hostname checking and
CERT_REQUIRED; no YAML flag may enable insecure HTTP or TLS bypass. Generated
keys and private runtime stores are excluded from archived artifacts.

No public DNS/TCP, live peer/model/exporter, paid effect, credential/store access,
ambient token/OTEL reads, shared environment sync/install, npm/browser, arbitrary
subprocess, user-state write, external message or publication. No dependency
change is allowed. Reuse pinned SDK/httpcore/jsonschema/referencing/IDNA libraries.

## Stops and independent handoff

Stop on authority/hash/branch/scope disagreement, a dependency requirement, any
unexpected effect, unvalidated network path, new suppression/lint/type/test
failure, loss of owner/security/provenance invariants or mandatory spec conflict.
Do not opportunistically fix unrelated code. Retain evidence and prepare a bounded
amendment rather than broadening this directive. The source budget is exactly28
product paths; a required edit outside them needs new exact authority.

Freeze a stable committed candidate, original/aggregate selected diffs, authority
manifest, clause/criterion ledger, effects, counterpart/library hashes, full argv/
environments/receipts and exact debt/skip comparisons. Dispatch the repository-
required fresh-context READ-ONLY independent validator for the complete UP-03 unit,
including preserved accepted core/HTTP/application regressions. Builder never
self-VERIFIED or accepts its result. Findings require bounded remediation and a
new frozen review; after two unsuccessful cycles return unresolved findings.
Only independent VERIFIED permits a completion proposal. Maintainer acceptance,
later UP-04/UP-05/UP-06 directives, full initiative aggregate review and delivery
remain separate. This planning packet is neither implementation nor conformance
proof for the still-unwired integration.

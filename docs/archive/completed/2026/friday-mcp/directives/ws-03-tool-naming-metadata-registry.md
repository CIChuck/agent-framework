# Construction Directive: MCP-WS-03 Tool Naming, Metadata, Filtering, And Registry Integration

Status: Approved by repository maintainer on 2026-09-28
Approval evidence: "ws-03 approved" in the active conversation
Implementation branch: `feature/friday-mcp-ws03-registry`
Frozen work-unit base: `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`
Prepared: 2026-09-28
Original draft date: 2026-07-24
Initiative: `friday-mcp`
Workstream: `MCP-WS-03`
Preparation base: `56251144345888f721c9fc9235ad8a54bbbb23db`
Accepted WS-02 product candidate: `a257f041d1d68f8aea2f5b9773df1b88acd82379`
Readiness evidence: [WS-03 readiness checkpoint](../execution/WS-03-readiness-checkpoint.md)
Tactical tasks: `MCP-03-01` through `MCP-03-08`

The maintainer explicitly approved this complete reconciled directive with
"ws-03 approved" on 2026-09-28. That decision grants this bounded slice only;
later workstreams remain draft. Record started branch/board evidence before
product edits. Acceptance and delivery remain separate gates.

## Authority And Dependencies

Apply explicit maintainer scope decisions, repository engineering/security and
[independent-validation policy](../../../../../reference/policies/independent-validation-policy.md),
then the approved [build plan](../build-plan.md),
[tactical sequence](../tactical-plan.md), accepted WS-00/01/02 decisions, and this
directive once approved. Later-slice drafts do not grant current authority.
Read AGENTS.md, board validate/next/show, packet index and execution log first.

WS-00 accepted deterministic bounded normalization and a typed read-only metadata
sidecar in `friday_core.mcp`; do not reopen that strategy or extend the mandatory
native ToolDefinition protocol. WS-01 accepted strict stdio-only runtime config,
default `mode: selected`, canonical-name filters and no stored argument hashes.
WS-02 was explicitly accepted on 2026-09-28 after complete
[VAL-007](../validation/VAL-007-report.md) verification. Its immutable
`RuntimeMCPProvider.prepared_tools` is size-bounded untrusted discovery, not
safe/executable registry entries.

After approval, record the authority commit and create
`feature/friday-mcp-ws03-registry` from the reconciled approved planning
checkpoint stacked on the accepted WS-02 branch. Update board branch/start
evidence before product edits. Freeze that full work-unit base for review.
Do not push, merge or change unrelated branches.

## Objective And Non-Goals

Consume the accepted discovery handoff exactly once per runtime start; validate,
normalize, sanitize, filter and cap it; transactionally register executable
wrappers in the existing registry; publish typed sidecar/diagnostics before
agent binding validation; remove owned MCP entries on failure/shutdown.

No Chat turn selection/budget/commands, model-aware tokenizer, execution result
truncation/sanitization/provenance, memory/transcript storage, telemetry emitters,
health CLI, MCP resources/prompts/server exposure, SSE runtime enablement,
refresh, external includes, credentials, paid/live/provider/network tests,
native-library refactoring, workspace cleanup or delivery operations.
WS-04/05 and later own those capabilities. Local harmless execution probes here
prove dispatch compatibility, not production output safety or complete app UAT.

## Exact Proposed Edit Boundary

Product source is limited to:

1. `packages/friday-core/src/friday_core/mcp.py` — backward-compatible metadata
   completeness and safe registration diagnostic codes only.
2. `packages/friday-mcp/src/friday_mcp/client/adapter.py` — compatible wrapper
   protocol fields, a public typed validated-registration construction path,
   immutable export snapshots and meaningful annotations.
3. `packages/friday-runtime/src/friday_runtime/mcp_registration.py` — new bounded
   admission/sanitization/filter/preflight module with typed decisions.
4. `packages/friday-runtime/src/friday_runtime/mcp_loading.py` — registry ownership,
   public read-only metadata/registration diagnostics, counters and cleanup of
   only owned registrations; preserve transport/manager lifecycle.
5. `packages/friday-runtime/src/friday_runtime/di.py` — invoke registration after
   successful discovery, before boot completion; guard registration failure
   through existing public provider cleanup.
6. `packages/friday-runtime/src/friday_runtime/tool_loading.py` — optional typed
   MCP reason context for binding failures only; native filtering unchanged.
7. `packages/friday-runtime/src/friday_runtime/kernel.py` — pass safe provider
   binding context; no startup signature, agent factory or LLM routing changes.

Tests/fixtures are limited to:

8. `packages/friday-core/tests_core/test_mcp_contracts.py`
9. `packages/friday-mcp/tests_mcp/client/test_adapter.py`
10. `packages/friday-runtime/tests_runtime/test_di.py`
11. `packages/friday-runtime/tests_runtime/test_kernel.py`
12. `packages/friday-runtime/tests_runtime/test_mcp_loading.py`
13. `packages/friday-runtime/tests_runtime/test_mcp_registration.py` (new)
14. `tests/integration/mcp_fake_server.py` — bounded fake catalog/call modes only;
    preserve existing noisy/cleanup modes.
15. `tests/integration/test_mcp_runtime_lifecycle.py` — only integration assertions
    affected by approved registry behavior; preserve lifecycle regressions.
16. `tests/integration/test_mcp_registry.py` (new)

17. `docs/planning/active/friday-mcp/execution/WS-03-implementation-report.md`
    (new) records execution, public API notes, checks and remaining gates.

Controller owns board/index/log/queue, requests, validation reports and closeout.
No agent registry/native tools/core mandatory protocol/security package,
MCP manager/base/stdio/schema utility/protocol/config source, dependency metadata
or other paths are edit targets. In particular, the old
`friday_runtime/tools.py` target does not exist and is not to be invented.
Stop before extending this exact boundary.

## Required Behavior And Decisions Proposed For Approval

### MCP-03-01 — Reuse Accepted Canonical Naming

Use `normalize_mcp_tool_name(s)` from the public core contract. Default config
`mcp_` yields `mcp_<normalized_server>_<normalized_original>`, with the accepted
ASCII lowercase/underscore alphabet, leading letter and 64-character cap.
Prefix overrides use the same function. Do not concatenate a second prefix,
truncate, suffix-disambiguate or change WS-00's normalizer.

Route execute to the exact original MCP tool name, never the normalized name.
Malformed/unusable/overlength source names are rejected with safe diagnostics.
Bound original-name provenance to the existing 256-character metadata limit;
do not truncate the routed original name to force acceptance.

### MCP-03-02 — Fail-Closed Collisions And Transactional Publication

Preflight normalizable contenders from the eligible handoff for collisions with
each other and the existing native registry before filters or any MCP insertion.
Collision is fatal regardless of optional server status; exclusions must not
silently conceal a name collision. Diagnostics use canonical names, configured
safe server IDs, provider labels, counts and bounded shape/fingerprints for
untrusted original names, not raw names or exception text.

Build all validated wrappers and metadata before mutating the registry. Use only
public register/list_names/get/unregister APIs of the explicit registry owner;
never `_tools` or adapter/manager private state. Track the owning registry and
only names inserted by this provider. If commit fails partway, roll back those
MCP names and metadata, preserve every native entry, clean clients through the
existing owner, and raise a static error. Genuine cleanup/rollback failure must
retain inspectable ownership for later public retry, not claim atomic success.

Public stop/failure clears model-accessible MCP registration/metadata before
disconnecting clients, even if transport cleanup subsequently fails. Repeated
stop/retry/start uses the existing retained owner and never duplicates entries.
No saved/private caller reference may be needed for asserted public cleanup.

### MCP-03-03 — Typed Read-Only Sidecar, Not Native Protocol Expansion

Expose a public `RuntimeMCPProvider.tool_metadata` read-only mapping keyed exactly
by current registered MCP names, accessible through existing
`RuntimeKernel.mcp_provider`. Populate via the accepted
`MCPToolMetadata`/`build_mcp_metadata_index`; native lookups return no MCP
metadata. Do not attach required metadata properties to native tools or rely on
wrapper attributes surviving the native registry's rewrapping.

Proposed additive core metadata fields: optional nonnegative
`schema_byte_size` and `discovery_state` with a backward-compatible
`not_checked` default and a registered `discovered` value. Retain existing
provider/server/original/canonical/prefix/transport/trust fields and populate
estimate, sanitization and filter state. Original untrusted names must not
appear in automatic repr/log/diagnostic output; a bounded typed provenance
field is not permission to print it. No schema/description/command/env/result
or argument hashes in this sidecar.

Existing constructors and input payloads must remain accepted. Document the
additive serialized fields for future consumers; do not claim an older strict
DTO version can parse new output without migration. No persisted provenance
format or storage path is implemented in this slice.

Add only fixed `missing_include`/`registration_failed` diagnostic codes needed
by this slice. Public typed per-tool registration decisions may live in the
new runtime module; they contain safe IDs/reason codes/counts, not raw peer JSON.
Preserve existing discovery/lifecycle diagnostics and distinguish discovered,
rejected, filtered, selected and actually registered counts without double
counting earlier WS-02 rejections. Metadata and registry must never disagree.

### MCP-03-04/05 — Explicit Filtering And Missing Includes

MCP wrappers use fixed category `mcp` and conservative fixed tags such as
`["mcp"]`; peer-controlled category/tags cannot broaden selection or lower trust.

Match tool filters only against exact canonical names; no glob, original-name,
alias or refresh behavior. Preserve existing provider category semantics:

- selected: union category matches and explicit includes; no selections means
  zero MCP registrations, although bounded discovery still runs;
- all: begin with the eligible catalog, restrict by include_categories if
  supplied, then union explicit includes;
- exclude categories/names always win.

For this proposed slice, every explicit include is a required tool request.
If absent after admission, sanitization, caps or exclusions, abort startup with
static error and typed `missing_include` diagnostics, even if its server is
optional. This is stricter than unchanged native-provider silent-missing
behavior and requires approval. Required server alone still requires connection/
discovery success, not registration of every listed tool. Optional invalid tools
can be skipped unless explicitly included or required by agent bindings.

Preserve binding validation after MCP publication. A profile's unavailable MCP
binding fails with safe reason context where known: filtered, rejected/capped,
server unavailable or unknown. Do not promise exact per-tool explanations for
catalog entries that WS-02 discarded before retaining their names. Native
unknown-tool behavior remains compatible.

### MCP-03-06 — Preserve Upstream Caps And Recheck Final Exports

Consume only `prepared_tools`; use manager.get_client(server_id) to construct
wrappers. Do not call get_all_tools/get_server_tools/adapter.get_tools or repeat
tools/list. WS-02 already caps raw catalogs before the handoff; WS-03 must not
rediscover/backfill capped-away entries or increase those budgets.

Revalidate handoff JSON and apply registration count/schema limits before any
insertion. Respect configured server/catalog order for cap admission. Recompute
UTF-8 byte size for complete final plain and OpenAI exported definitions,
including canonical name, sanitized description and parameters; use the larger
size for the per-tool byte cap and a conservative one-token-per-byte estimate
for aggregate `max_schema_tokens`. Do not present it as tokenizer/model parity.
The full exported definition, not only inputSchema, is the cost boundary.

Inspect exports after registry rewrapping too; sanitizer/wrapper-generated
fields must not create a cap bypass. Do not spend native-tool budget here or
implement the per-turn memory-floor fallback. WS-04 owns final per-turn budget
accounting. Default limits and WS-02 early admission remain unchanged.

### MCP-03-07 — Schema-Specific Sanitization With Structural Integrity

Names/descriptions/schema strings are untrusted. Use a bounded explicit
registration sanitizer, not default warn/log-only output wrapping. Existing
public security detection/normalization interfaces may be reused without
editing them, recording/persisting raw results, or emitting detection samples.

Validate a documented supported inline JSON Schema subset before export:
object root, correctly typed properties/required/items/combinators/constraints,
finite JSON values. Bound traversal to depth 32 and 4096 nodes, with total
text/work further constrained by configured byte caps. Reject unsupported/external reference features
rather than fetching or silently discarding behaviorally significant semantics.
Support type/properties/required/additionalProperties/items, enum/const/default,
allOf/anyOf/oneOf/not, standard numeric/string/array/object constraints, and
plain title/description annotations. Validate nested shapes and required-name
consistency. Reject references, schema IDs, definitions, conditional/dependent
extensions and other unimplemented keywords; no network resolution. State the
exact accepted keyword list in tests/docstrings. These deliberately conservative
first-slice limits/subset are proposed policy, not existing guarantees. Never
scan only a prefix then mark the whole schema safe.

Normalize safe free-text annotations and redact/drop instruction/role-delimiter
content there. If detected in executable structure, keys, parameter names,
enum/const/default values or other semantics whose modification could change
the tool contract, reject the whole tool with a static code. Preserve safe
property keys, required membership, types, numeric bounds, enums and defaults
exactly; never rewrite JSON wholesale into a wrapped text result. Unknown
keywords/extensions must be explicitly supported or rejected, not silently
removed. Reject failures to validate or completely scan.

Do not invent universal injection detection guarantees. Test known critical
patterns, zero-width/entity/control/delimiter evasions, nested/late content,
unsupported refs and escaped strings. Keep raw content out of logs, typed
diagnostics and automatic repr. A sanitized export remains external content,
not trusted system instructions. WS-04/05 must verify schema safety/handle
output at later model boundaries.

### MCP-03-08 — Adapter Protocol And Execution Compatibility

Implement all current ToolDefinition members, including category/tags and
plain/OpenAI to_schema. Add a public typed construction path taking accepted
metadata and sanitized immutable definition input; use explicit checks, not
casts/private fields, to cross the runtime/MCP boundary.

Preserve existing standalone constructor/prefix/adapter APIs and original-name
execution routing. The integrated path uses the canonical metadata name
directly, not legacy concatenation. Remove adapter.py's broad mypy ignore and
annotate touched public/semi-public methods without weakening project typing.
Do not edit untouched protocol/schema utility suppressions.

Defensively snapshot untrusted input and return independent adapter schemas so
peer/input or adapter-export mutation cannot change validated registration or
reroute execution. The native registry subsequently owns its own export snapshot;
its existing public schema dictionaries remain mutable to trusted in-process
callers. Do not claim whole-registry immutability or silently refactor native
exports. Document that residual contract; later prompt consumers must copy and
verify exports before use. Include post-registry cost/structure checks. The
public registry callable must actually dispatch a local harmless tools/call
with exact original name and arguments, not merely pass isinstance or a mock
registration. No Chat/model result safety claim follows from that probe.

## Acceptance Criteria And Required Coverage

- `MCP-03-AC-01`: accepted normalizer/prefix/length/error behavior; no double
  prefix; same original names on different servers route to their correct peers.
- `MCP-03-AC-02`: MCP/MCP and MCP/native collisions fail before insertion,
  using safe source diagnostics; no overwrite or exclusion-based concealment.
- `MCP-03-AC-03`: exact typed immutable sidecar for registered MCP entries,
  backward-compatible DTOs; consistent costs/states/counters and native lookup.
- `MCP-03-AC-04`: selected/all/category/include/exclude semantics, default zero
  selection, excluded and capped tools absent; strict explicit missing includes.
- `MCP-03-AC-05`: upstream and final-export count/byte/schema-budget caps,
  deterministic admission, no second discovery RPC/backfill/cost bypass.
- `MCP-03-AC-06`: bounded complete schema/description sanitization, preserved
  safe semantics, unsupported/deep/invalid/injection content rejected or safely
  redacted before exposure, sentinel-free diagnostics and peer/adapter snapshot
  mutation resistance; native registry's trusted-caller mutability documented.
- `MCP-03-AC-07`: full protocol conformance and legacy adapter compatibility;
  harmless real registry-callable stdio dispatch uses exact original name.
- `MCP-03-AC-08`: registry and metadata publish before agent binding checks;
  existing native/disabled/empty MCP behavior and profile errors remain sound.
- `MCP-03-AC-09`: transactional rollback, registry insertion failure, successful/
  optional/required startup, binding failure, cancellation, repeated start/stop,
  retained-owner cleanup/retry and every REM-003/004 noisy-peer regression.
- `MCP-03-AC-10`: exact scope, additive public boundaries, meaningful typing,
  source/report accuracy, no later-slice/external effects or new broad ignores.

Every criterion needs unit evidence and appropriate real-public-runtime coverage.
Tests own their local doubles/tasks/processes and settle them in finally,
including failed assertions. Distinguish defensive fixture cleanup from
successful public cleanup assertions. Preserve production cleanup budgets;
VAL-006's seven-second detector is not a shutdown SLA.

## Required Verification Commands

Every uv command uses `UV_CACHE_DIR=/private/tmp/friday-uv-cache`; tests/imports
also use `LITELLM_LOCAL_MODEL_COST_MAP=true`. Local fake peers/doubles only.

```text
uv run pytest packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp/tests_mcp/client/test_adapter.py packages/friday-runtime/tests_runtime/test_mcp_registration.py packages/friday-agent/tests_agent/test_registry.py tests/integration/test_mcp_registry.py -q
uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime packages/friday-agent/tests_agent/test_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/test_mcp_registry.py -q
uv run pytest packages/friday-tools/tests_tools -q
uv run pytest packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py -q
uv run pytest tests/integration -q --tb=short
uv run ruff check packages/friday-core/src/friday_core/mcp.py packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp packages/friday-runtime tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
uv run mypy packages/friday-core packages/friday-runtime packages/friday-mcp
uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py
uv run mypy --python-version 3.13 packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
uv run python scripts/friday-dev-board.py validate
uv run python scripts/friday-dev-board.py render --check
uv run python scripts/check-documentation-lifecycle.py
git diff --check
```

Record command exit codes, full failures and meaningful narrower evidence.
Declared baselines: default-target installed NumPy syntax; unchanged integration
board-count assertion (22 versus 23); unfiltered core-inclusive Python 3.13 mypy
reports four existing no-any-return errors in untouched profiles.py at
77/82/110/115. A supplemental import-silent core check is not a substitute for
those unfiltered commands. No new error in touched source or unexplained
regression may be classified as legacy.

Native tools tests are compatibility evidence, not permission to repair that
package. If they fail, establish the unchanged predecessor baseline and report
it; do not waive unknown failures, add broad ignores or change dependencies.

## Documentation, Review And Acceptance

Implementation report must record approved authority/base, exact path manifest,
public adapter/sidecar/diagnostic additions, sanitizer supported subset/bounds,
filter decisions, final-export cost basis, transactional ownership, all criteria
and check results/baselines, synthetic cleanup evidence and residual limits.

Commit a stable candidate. Controller pins the approved authority revision/
hashes, exact base/candidate/diff, all ten criteria and required checks for a
new fresh-context read-only work-unit validator. Expected identifier VAL-008,
reserved only; no request, dispatch or verdict exists at preparation.
Review all WS-03 changes and interaction with accepted WS-00/01/02, including
independent real callable routing, cap/sanitization bypass attempts and failure/
cancel/rollback/public-shutdown probes. Builder cannot approve its own work.
Full feature-branch aggregate before merge remains a later separate gate.

Only independent VERIFIED permits proposed work-unit closeout; only an explicit
maintainer decision records acceptance. Any remediation needs its bounded
directive/authority and fresh review under policy; no automatic fix loop.
Wider initiative remains started and local throughout this slice.

## Stop Conditions

Stop before product edits if approval/branch/board/directive disagree or a
predecessor cannot be confirmed accepted. Stop before expanding exact paths,
changing mandatory native protocols/configuration/defaults/normalizer, adding
dependencies, reaching private cross-package/subprocess internals, changing
transport/manager retained ownership, or performing broader lifecycle redesign.

Stop for unsupported schema semantics or sanitizer behavior that cannot be made
safe within this scope; do not silently weaken rejection/caps or relabel unsafe
content sanitized. Retain/report ownership if rollback/cleanup cannot complete.
Return any authority conflict, newly reproduced baseline requiring scope,
missing independent-review capacity, or external-effect requirement to the
controller/maintainer without treating it as implementation approval.

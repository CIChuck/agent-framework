# MCP-WS-03 Readiness And Approval Checkpoint

Date: 2026-09-28
Status: Planning complete; explicit implementation approval required
Initiative: `friday-mcp`
Preparation branch: `feature/friday-mcp-ws02-lifecycle`
Preparation HEAD/base: `56251144345888f721c9fc9235ad8a54bbbb23db`
Accepted WS-02 product candidate: `a257f041d1d68f8aea2f5b9773df1b88acd82379`
Acceptance evidence: explicit maintainer message "WS-02 accepted"
This turn's authority: subsequent "continue" for the next planning gate

## Result And Authority Boundary

WS-00/01/02 predecessors are independently verified and explicitly accepted.
The board remains `started`, granted only for those bounded slices, `normal`,
local, on the WS-02 branch. The current next gate authorized WS-03 directive
reconciliation, not implementation. Read AGENTS.md, engineering/lifecycle/
independent-validation policies, build/tactical plans, accepted closeouts,
VAL-002/007 evidence and current contract/adapter/registry/provider/config code.

The [reconciled directive](../directives/ws-03-tool-naming-metadata-registry.md)
is still a draft. It supplies exact edit paths, ten acceptance criteria,
ordering/rollback/cleanup ownership, schema/filter decisions, tests, required
commands, baselines and stop conditions. Product source/tests/configuration
remain byte-identical to accepted WS-02; no new agent, implementation branch,
candidate, review request/verdict, live call, credential use or delivery exists.

## Current-Code Evidence And Reconciliation

| Topic | Verified current boundary | Proposed WS-03 action |
| --- | --- | --- |
| Discovery handoff | `mcp_loading.py` publishes frozen `MCPDiscoveredTool` tuples with non-repr untrusted JSON. WS-02 already enforces raw count/size/cost caps; selected/registered counts stay zero. | Consume only this eligible handoff, no second tools/list or backfill; publish sanitized wrappers before binding validation. |
| Naming | `friday_core.mcp.normalize_mcp_tool_name(s)` already defines deterministic ASCII/length/collision behavior. Runtime prefix defaults to `mcp_`. | Reuse it directly; retain exact original name for dispatch, reject unusable/overlength names and native collisions. |
| Metadata | WS-00 selected typed immutable sidecar; `MCPToolMetadata` already carries provenance/estimate/sanitization/filter state, but lacks explicit byte-size/discovery fields. | Public provider sidecar, additive optional fields and static diagnostic codes; no native protocol expansion. |
| Adapter conformance | Existing wrapper lacks category/tags; concrete runtime protocol probe is false and DefaultToolRegistry rejects it. Legacy name concatenation preserves a hyphen while accepted normalizer emits underscore. | Fixed MCP category/tags, canonical validated construction path, compatible legacy constructor, meaningful annotations and exact original-name execution. |
| Registry | Public register rejects duplicates, rewraps external tools in DecoratedFunctionTool and offers unregister. Wrapper-specific metadata would not survive that rewrapping. | Preflight/transactional insertion, registry ownership and rollback of only MCP names; independent sidecar and final post-rewrapping export cost checks. |
| Mutable exports | Read-only ephemeral probe confirms get_schema parameters alias the native registry's stored dictionary. | Snapshot peer/adapter inputs/outputs and document trusted in-process registry mutability. Whole-registry immutability is not claimed or repaired in this slice; later model-facing consumers must copy/verify exports. |
| Startup/shutdown | DI builds native registry, awaits provider.start, then kernel validates profile tools. REM-003/004 retain owners across cleanup failure and bound noisy-peer teardown. | Insert guarded registration before boot/profile completion; remove owned MCP entries/metadata before client disconnect; preserve all transport/ownership controls. |
| Filters | Strict MCP config has exact canonical names, selected/all and category filters, with no mode/config additions needed. Native loader silently ignores unmatched includes. | MCP-only deterministic filters; explicitly included absent/rejected/capped/excluded tools fail startup. Native behavior remains unchanged. |
| Sanitizer | Public ToolOutputSanitizer is output-oriented; default quarantine action warns and preserves detected content. Serializing/wrapping a whole schema would not preserve executable schema semantics. | Dedicated bounded schema traversal/validation and strict annotation sanitation; reject unsafe semantic fields and unsupported keywords/references. No raw result/quarantine storage. |
| Draft scope drift | Old draft names missing runtime tools.py and authorizes whole native package directories/mandatory protocol editing. Actual provider handoff/integration hooks are elsewhere. | Replace with seven exact source targets, nine test/fixture targets and one report; no native, manager/transport or config/dependency edits. |

## Decisions Included In The Approval Request

1. Use the accepted sidecar and normalizer, rather than another protocol or
   metadata strategy. Permit only optional additive metadata fields and fixed
   missing-include/registration-failure codes in the core contract.
2. Require every explicit MCP include to resolve to a final registered tool,
   even for optional servers. Exclusions win; an explicitly included tool
   excluded by category is an unsatisfied request, not silent success. Required
   server alone still requires connection/discovery, not all listed tools.
3. Fail closed on all eligible normalized MCP/MCP or MCP/native collisions,
   before filters/insertion, with safe source labels instead of raw names.
4. Preserve WS-02 early admission; no rediscovery or capped-catalog backfill.
   Recheck complete final plain/OpenAI definitions including native registry
   category/tags overhead. Conservative one-token-per-byte estimates are not
   model-tokenizer parity; per-turn memory-floor accounting remains WS-04.
5. Adopt a conservative inline schema subset, depth 32 and 4096-node traversal
   bounds, with byte caps. Normalize/redact free annotations, preserve safe
   executable semantics and reject unsupported/reference/unsafe semantic
   content. Pattern detection is not a universal injection-proof guarantee.
6. Make registry publication and sidecar ownership transactional and undo only
   owned MCP names on insertion/binding/startup failure or shutdown. Genuine
   cleanup failure retains inspectable owners for public retry.
7. Preserve standalone MCP APIs and all native tool APIs. Snapshot peer and
   adapter inputs/exports; do not promise global immutability of the existing
   trusted-caller native registry. No complete Chat/UAT/output-security claim.

The directive spells out all ten criteria and permitted execution effects.
Approval is for the reconciled file as a whole; these choices are not already
implemented by preparation or implied by predecessor acceptance.

## Read-Only Preparation Checks

All uv commands used `UV_CACHE_DIR=/private/tmp/friday-uv-cache`; diagnostic
imports/tests also used `LITELLM_LOCAL_MODEL_COST_MAP=true`. No provider endpoint
or network was used. Introspection objects were ephemeral, not repo edits.

- Board validate: passed, 23 tasks; next/show matched the preparation gate.
- Concrete adapter probe: `isinstance(wrapper, ToolDefinition)` false; category
  and tags absent; registration rejected; registry stayed empty. Legacy name
  `mcp_fake_read-file`, accepted normalization `mcp_fake_read_file`.
- Native registry snapshot probe: mutating an ephemeral get_schema return
  changed its subsequently exported parameters. No repository object/state was
  involved; this identifies the existing trusted-caller mutable contract.
- Focused compatibility: 88 passed in 0.32 seconds:

```text
uv run pytest packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp/tests_mcp/client/test_adapter.py packages/friday-runtime/tests_runtime/test_di.py packages/friday-agent/tests_agent/test_registry.py -q
```

- Ruff passed:

```text
uv run ruff check packages/friday-core/src/friday_core/mcp.py packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp packages/friday-runtime tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
```

- Existing meaningful runtime/MCP Python 3.13 typing passed, 42 files:

```text
uv run mypy --python-version 3.13 packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
```

- Both unfiltered core-inclusive invocations reproduced exactly four historical
  no-any-return errors in untouched `friday_core/profiles.py:77/82/110/115`,
  already recorded in VAL-002. This is not an adapter-fix verdict; that module
  still has its legacy ignore, which the future slice must remove.

```text
uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py
uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
```

- Supplemental core check with `--follow-imports=silent` passed one file;
  imported errors were not reported in that invocation. It does not replace
  either unfiltered command or establish an aggregate passing type gate.
- Default-target runtime/MCP mypy reproduced installed NumPy syntax at
  `.venv/lib/python3.13/site-packages/numpy/__init__.pyi:737`, requiring a newer
  syntax target than unchanged Python 3.10 repository settings.
- Initial focused command accidentally named nonexistent runtime
  `test_tool_loading.py`: exit 4, no tests ran. Corrected to actual test_di.py
  and existing agent registry coverage; the successful 88-case run is above.
  No product failure or missing future implementation test is inferred.
- No WS-03/new-file test suite, broad integration or full native-tools suite was
  run in preparation. Their required future commands are in the directive.
  The unchanged integration board-count baseline remains separately documented
  by accepted VAL-007; this turn does not claim to have rerun it.
- Frozen product comparison passed:

```text
git diff --exit-code a257f041d1d68f8aea2f5b9773df1b88acd82379 -- packages tests pyproject.toml uv.lock
```

Preparation source fingerprints (SHA-256 at the base above):

```text
7cd153b20ace37e824b48a5434db6b00f5911ebac0acf3c0629996ea1c6d4227 packages/friday-core/src/friday_core/mcp.py
d6b54d41b79d14c11bc19e188298b9aa1383f8139ef1f80afed796d14eb1783f packages/friday-mcp/src/friday_mcp/client/adapter.py
853909d272b0cca5ce98db4c70db978fa0f4d1d5ce650e1cfcf83e6cf2c68630 packages/friday-runtime/src/friday_runtime/mcp_loading.py
96a10e3359cfd87d2630b22e2a348157509b21522ed7e5cccb9f73819cb86342 packages/friday-agent/src/friday_agent/tools/registry.py
```

## Preserved Work And Exact Stop Point

Unrelated manifest stays modified `.DS_Store`; deleted `family-tree.md`;
untracked `docker-bench-security/`,
`packages/friday-chat/config.example.yaml.pre-typed-llm-20260828.bak` and
`packages/friday-sandbox/docker/Dockerfile.audit`. Never broad-stage this checkout.

Only WS-03 draft/readiness and board/index/queue/log/dashboard planning records
change in this turn. Approved WS-00/01/02, remediation authorities, accepted
closeouts and historical validation reports remain untouched. No fresh product
verification or acceptance is claimed; accepted predecessors are not reopened.

Exit gate: explicit maintainer approval of the complete reconciled WS-03
directive. Then record approval, prepare its named branch/base and start, build
only exact scope, commit stable candidate, obtain fresh independent VAL-008
work-unit aggregate review, and request separate acceptance. Future identifier
is only reserved; fresh-agent capacity must be checked at dispatch, not assumed.
No additional remediation/acceptance/delivery authority is implied.

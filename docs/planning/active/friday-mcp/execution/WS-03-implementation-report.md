# MCP WS-03 Implementation Report

Date: 2026-09-28
Status: Builder candidate; independent verification and maintainer acceptance pending
Branch: `feature/friday-mcp-ws03-registry`
Work-unit base: `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`
Approval/start authority commit: `b54069654bb3e21a6265fbabcd23f6991e286ab0`
Accepted predecessor product: `a257f041d1d68f8aea2f5b9773df1b88acd82379`
Authority: [approved WS-03 directive](../directives/ws-03-tool-naming-metadata-registry.md)
Maintainer evidence: "ws-03 approved" on 2026-09-28

This report is builder evidence, not an independent VERIFIED verdict. Candidate
hash is pinned by the controller's subsequent VAL-008 request (not self-referential
text in this commit). Wider initiative remains started and local. No later slice,
acceptance, push, merge, release, deployment, credentials or live/network effects.

## Exact Implementation Manifest

Seven approved source paths:

- `packages/friday-core/src/friday_core/mcp.py`
- `packages/friday-mcp/src/friday_mcp/client/adapter.py`
- `packages/friday-runtime/src/friday_runtime/mcp_registration.py` (new)
- `packages/friday-runtime/src/friday_runtime/mcp_loading.py`
- `packages/friday-runtime/src/friday_runtime/di.py`
- `packages/friday-runtime/src/friday_runtime/tool_loading.py`
- `packages/friday-runtime/src/friday_runtime/kernel.py`

Eight approved test/fixture paths:

- `packages/friday-core/tests_core/test_mcp_contracts.py`
- `packages/friday-mcp/tests_mcp/client/test_adapter.py`
- `packages/friday-runtime/tests_runtime/test_di.py`
- `packages/friday-runtime/tests_runtime/test_kernel.py`
- `packages/friday-runtime/tests_runtime/test_mcp_loading.py`
- `packages/friday-runtime/tests_runtime/test_mcp_registration.py` (new)
- `tests/integration/mcp_fake_server.py`
- `tests/integration/test_mcp_registry.py` (new)

Plus this report: sixteen implementation paths total, within the seventeen-path
allowlist. Existing `test_mcp_runtime_lifecycle.py` needs no assertion edits and
remains unchanged. Board/index/queue/log/review records are separate controller
metadata. Native registry/protocol/source, manager/transport/config/security
source, dependency metadata and defaults remain unchanged.

## Public Contracts And Assembly

- Additive `MCPToolMetadata.schema_byte_size` (optional nonnegative integer) and
  `discovery_state` (`not_checked` default, `discovered` at admission). Existing
  constructor/input payloads remain valid. Newly serialized fields require
  migration for older strict DTO readers; no persistence format is implemented.
  `original_name` is retained as bounded provenance but excluded from repr.
- Only diagnostic codes `missing_include` and `registration_failed` are added.
  Original discovery/lifecycle diagnostics remain safe and available.
- Adapter implements the complete existing ToolDefinition, fixed category/tags
  `mcp`, plain/OpenAI exports and exact-original-name execution. Standalone
  constructor/prefix/get/adapt/cache behavior remains available. Adapter broad
  mypy suppression is removed; untouched protocol/schema suppressions are not
  expanded. Wrapper repr and adapter debug logging never echo peer names.
- New public `MCPValidatedDefinition` is an immutable, non-repr JSON snapshot;
  `MCPToolWrapper.from_validated` requires admitted/check-complete metadata and
  uses its canonical name without another prefix. The runtime supplies sanitized
  definitions; this API is not a substitute for caller validation.
- Provider exposes read-only `tool_metadata`, safe `registration_decisions`,
  `binding_context`, inspectable `registration_registry` and `owned_tool_names`.
  Exact metadata keys match owned published MCP names; native lookup is absent.
- Pure admission returns typed plans/decisions. `selected` is distinct from
  actually `registered`; successful provider publication promotes decisions.
  Shutdown changes removed registered decisions to unavailable and sets current
  registration count to zero. Discovery selection/history remains descriptive.
- DI registers after bounded discovery and before boot/binding validation. Both
  direct DI registration failure and public kernel failure clean through the
  existing public provider owner. No startup signatures/agent routing change.
  Optional typed binding context adds known safe MCP reasons; native errors and
  native provider selection remain unchanged.

## Admission, Sanitation, Filters And Costs

- Consume only immutable `prepared_tools`, once per start. Construct wrappers
  with public `manager.get_client`; never rediscover, backfill upstream caps,
  use cached adapter discovery or access private cross-package registry state.
- Accepted normalizer supplies deterministic ASCII names, prefix/leading-letter/
  64-character rules. Exact original names are never truncated or rerouted.
  Normalizable contender collisions against peers/native names are fatal before
  filtering and insertion, even for optional/excluded tools. Diagnostics use
  canonical/configured IDs and fixed codes, not raw names or peer exceptions.
- Selected mode unions MCP category and exact includes; default selects zero.
  All mode uses eligible catalog restricted by supplied categories then unions
  explicit includes. Exclusions win. Every explicit include must survive full
  admission/filter/caps or startup fails, even for optional peers. Required
  server status alone does not make every catalog tool mandatory.
- Complete inline-schema subset is documented in the new module: type,
  properties, required, additionalProperties, items, enum, const, default,
  allOf/anyOf/oneOf/not, title/description, minimum/maximum,
  exclusiveMinimum/exclusiveMaximum/multipleOf, minLength/maxLength/pattern,
  minItems/maxItems/uniqueItems, minProperties/maxProperties. Boolean subschemas
  are supported; root must explicitly be an object. Required membership must
  match local properties. Refs/IDs/defs/conditionals/formats/extensions and every
  unknown keyword are rejected, not resolved or silently dropped.
- Finite JSON, supported nested shapes and all strings/keys are completely
  traversed within depth 32, 4096 nodes and configured whole-definition byte
  bounds. Annotation normalization checks decoded HTML entities, Unicode NFKC,
  zero-width/control evasions and comment-split patterns; known instruction/role
  attacks redact whole annotations. Executable semantics/keys/parameter names/
  enum/default/const attacks reject the entire tool. Safe structural semantics
  are preserved. Public pattern detection is used without persistence/logging
  of detections, samples, results or raw peer JSON.
- Final costs use larger UTF-8 serialized size of complete plain/OpenAI export,
  including canonical name, sanitized description, parameters and native
  category/tag overhead. One byte per token is a conservative bound, not model
  tokenizer parity. Configured count/per-tool byte/aggregate caps and ordered
  admission are rechecked; actual native-rewrapped exports must exactly match
  the preflight definition/cost or transaction fails.
- Input/adapter/export mutation cannot alter validation/routing. The existing
  native registry intentionally retains mutable schemas for trusted in-process
  callers after initial publication: whole-registry immutability is NOT claimed.
  Later prompt consumers must copy and verify again. Sanitized schemas remain
  external content, not trusted system instructions or injection-proof text.

## Transaction And Resource Ownership

Build all wrappers/metadata before inserting. Track explicit registry owner and
objects observed through public get, including insert-then-raise failures.
Rollback removes only matching owned MCP objects, preserving native entries or
trusted replacements. Stop removes registration/sidecar before awaiting client
disconnect. Metadata trims to remaining owned registrations if genuine rollback
fails; public owner/names remain inspectable for later stop retry. No falsely
successful atomic-cleanup claim is made.

Existing retained transport/manager ownership and production attempt budgets
remain unchanged. Public kernel/provider stop settles normal/noisy children;
cancelled noisy shutdown unpublishes first, retains client cleanup ownership,
then a later public stop joins/reaps it. Tests/fixtures use finally to settle
processes/tasks even on failed assertions; defensive fixture cleanup is separate
from public cleanup assertions. The old seven-second detector is not an SLA.

## Acceptance-Criterion Evidence Map

| Criterion | Builder coverage |
| --- | --- |
| AC-01 | Normalizer compatibility, prefix/length rejection, independent exact original-name routing to two real peers. |
| AC-02 | Peer/native collisions before exclusions/schema validation; no overwrite or partial insertion; safe failures. |
| AC-03 | Additive DTO/default tests, immutable sidecar/native absence, final costs/states, discovered/selected/registered/rejected/filtered counts without double counting. |
| AC-04 | Pure and real selected/all/category/include/exclude matrices, default zero, strict optional/unavailable/rejected/capped missing includes. |
| AC-05 | Whole export overhead caps, aggregate/count deterministic admission, upstream-capped include rejection; real callable reports exactly one tools/list. |
| AC-06 | Supported subset preservation, malformed/unsupported/deep/node/nonfinite rejection, known annotation/semantic/late-content attacks, mutation isolation, repr/diagnostic redaction. |
| AC-07 | Full protocol, legacy adapter tests, real native-rewrapped registry callable with exact original name/arguments/peer. |
| AC-08 | Publication before actual profile binding, safe filtered errors, direct DI failure cleanup, unchanged native/disabled/empty behavior. |
| AC-09 | Partial insert/insert-then-raise, failed rollback/public retry, successful cleanup/restart, failed client cleanup/recovery, registered noisy cancelled stop/public retry and all WS-02 regressions. |
| AC-10 | Exact source/test manifest, meaningful adapter/runtime typing, no new broad ignores/dependencies/config changes, explicit report/residual gates. |

## Required Checks And Baseline Separation

Every uv check uses `UV_CACHE_DIR=/private/tmp/friday-uv-cache`; tests/imports
also use `LITELLM_LOCAL_MODEL_COST_MAP=true`. Exact commands are in the directive.

| Required command group | Result |
| --- | --- |
| Focused core contracts / adapter / registration / native registry / real registry integration | Exit 0, 146 passed (5.44s). |
| Complete core/MCP/runtime + native registry + lifecycle/registry integration | Exit 0, 430 passed (51.54s). |
| Friday tools compatibility | Exit 1, 233 passed / 2 failed, one unrelated deprecation warning (12.14s). Both failures reproduce on unchanged predecessor; see below. |
| Three Friday Chat compatibility targets | Exit 0, 46 passed (1.50s). |
| Full integration | Exit 1, 57 passed / 1 declared board-count failure (49.90s). |
| Exact required Ruff scope | Exit 0, all checks passed. |
| Default mypy core/runtime/MCP | Exit 2, installed NumPy syntax baseline prevents checking. |
| Python 3.13 core mcp.py (unfiltered) | Exit 1, four historical profiles.py errors, checked 1 root source file. |
| Python 3.13 runtime/MCP + three integration files (unfiltered) | Exit 0, no issues in 45 files. |
| Python 3.13 core mcp.py + runtime/MCP + integration (unfiltered) | Exit 1, only four historical profiles.py errors, 46 root files. |

Supplemental full-core Python 3.13 inspection reproduces four historical errors;
no import-silent check substitutes for required commands. Early incremental
isolated-core commands reported success before full-core traversal populated
dependency checking; final unfiltered results explicitly retain those errors.
Initial typed readonly-mutation test errors were corrected in the test without
ignores or typing configuration changes; final combined command has no touched
source/test error. Earlier focused integration exposed native global-catalog
test ordering; an explicit fixture-native registration now makes real registry
tests independent of that unrelated global reset. Earlier post-failure kernel
registry-access assertions were corrected to provider public cleanup checks.
These initial failures are not silently classified as baseline passes.

Exact remaining failure outputs:

```text
.venv/lib/python3.13/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater [syntax]
profiles.py:77: Returning Any from function declared to return "VectorStoreAdapter" [no-any-return]
profiles.py:82: Returning Any from function declared to return "VectorStoreAdapter" [no-any-return]
profiles.py:110: Returning Any from function declared to return "GraphStoreAdapter" [no-any-return]
profiles.py:115: Returning Any from function declared to return "GraphStoreAdapter" [no-any-return]
tests/integration/test_development_board.py:75: expected "22 tasks", actual "Development board validation passed: 23 tasks"
test_filesystem_readers.py:286: DOCX dependency-only assertion rejects "Failed to read DOCX: File is not a zip file"
test_filesystem_readers.py:306: XLSX dependency-only assertion rejects "Failed to read Excel file: File is not a zip file"
```

Native baseline reproduction: read-only Git archive of exact work-unit base
`2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`, packages + root pyproject, into
`/private/tmp/friday-ws03-baseline.5Hazyc`. All archived package src directories
precede installed editable imports via task-specific PYTHONPATH. Original venv
interpreter runs `python -m pytest packages/friday-tools/tests_tools -q` in
that archive. Exit 1, exactly 233 passed and the same two named failures
(12.45s); warning path proves archived memory source loaded. Native package
source/tests and profiles.py are unchanged. No baseline repair or waiver.

Final board/dashboard/documentation/whitespace and stable candidate range checks
are controller-recorded in the request/log. No tests contact live MCP/model
services. Fake tools/call results prove routing only, not WS-05 output safety.

## Remaining Gates

Fresh-context read-only VAL-008 must inspect the full WS-03 work-unit diff and
accepted WS-00/01/02 interactions, independently reproduce required checks and
adversarial public cleanup/routing/safety/cap probes, and return exactly VERIFIED,
CHANGES_REQUESTED or BLOCKED. Builder cannot approve this candidate. Only after
VERIFIED may controller propose closeout; explicit maintainer acceptance is
still required. WS-04/05/later work, full feature-branch aggregate, live UAT and
delivery retain separate authority gates. Preserve unrelated dirty paths.

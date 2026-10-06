# REM-004 remediator handoff — frozen candidate

Construction completed within approved A06/WVR-003 scope. No commit, staging, authority/planning/configuration/dependency modification performed by remediator. Formal independent verification and required aggregate/broad gates remain root-owned; this handoff does not declare VERIFIED.

## Frozen scope

`final-product-manifest.json` pins all91 allowed paths and the exact88 changed product/test paths. Three unchanged allowed paths are the protected CommandRegistry, existing core test_interfaces, and CLI test_cancellation. The four archived probe files and commands.py retain their original hashes; commands.py is15992e7f38fe874f0104a164180679c7e76d7e09413d68152ef5cc77c0f99308. Final source/test writes are frozen. `final-product-diff.patch` contains only these88 paths. Root metadata and unrelated dirty checkout changes are excluded. No original application state, live provider/exporter, real network, install/sync or lock change was used.

`completion-expanded-lists-final.json` records98 aggregate changed Python files, the exact63 source paths and union Ruff targets. Frozen final sparse snapshot is `remediator-a06-final-02` at1b28d373bb613e754947e4b13c7f7280314c560e with88 exact allowed overlays and protected tracked runtime directories omitted before materialization.

## Required changes

- R4-01: real autouse agent fixture snapshots/restores decorator registry in finally; new existing-runtime-file regression unwraps the actual fixture, checks prior declaration/metadata identity and removal of test declarations, tests both normal completion and early generator close, and restores all outer registry state even on assertion/close failure. No production reload or weakened assertions.
- R4-02: optional dependency paths use scoped builtins import failures for exactdocx/openpyxl, exact published extras/metadata; malformed containers assert installed reader failure; valid documents/spreadsheets are synthetictmp_path. Installed dependency state cannot skip missing-dependency coverage.
- R4-03: URL literal IP classification precedes resolver. Public literal allows, private/link-local/multicast/reserved literals reject; private override, scheme/blocked-host policy retained. Mixed domain results reject any private address and original resolver-failure policy retained. DNS/transport sentinels fail on attempts; public domain tests use synthetic answers; existing HTTP tests use respx.
- R4-04: child declares readiness after fake runtime/app initialization; parent triggers via one byte only after readiness and starts unchanged0.8s acknowledgement budget immediately before trigger. Bootstrap20s, childtrigger10s, syntheticwork1s, completion3s, wait/kill-reap5s bound cleanup. Ownership checks use actual app maintenance gate, background and fake transcript. All descriptors/child are cleaned in finally.
- R4-05/R4-06:132 live findings fixed by exact reviewed manual sites and necessary imports/doc wraps; pinned Ruff safe import-block edits only, no blanket unsafe fix/suppression/config change. CommandRegistry whole file untouched under exactA06/WVR003 exception. Public module TypeVar names retained, no artificial attrs/bases. Existing datetimeUTC and TimeoutError aliases are identical at runtime. Default generator args, typing.Self, annotation-only aliases and four bounded generic functions modernized.
- R4-06b: Chat response local is union of the two published response models with existing branch narrowing; Memory uses separate typed/legacy response locals. Request calls, defaults, projection, raw identity, model/usage omission, reasoning, tool-call translation and service exceptions unchanged. No cast/Any/ignore/coercion added.

## Narrow guarded evidence

Every receipt pins source snapshot/hash, guard, exact command, offline/no-sync environment, isolated temp/cache roots, log hash and tracked-unchanged result. See `completion-verification-receipts.json`.

|Check|Result|
|---|---|
|Old committed source + new registry/literal regressions, tests-only overlay excluding fixed agent fixture|19 expected failures,1 pass (the pre-existing loopback shortcut)|
|Current reader/web modules|107 passed|
|Current real-fixture2 + exact native/MCP7 nodes|9 passed|
|Current PTY whole module|2 passed|
|Published Memory whole file + selected Chat response nodes, no listener fixture|44 passed|
|Aggregate changed source typing, installed Mypy1.19.1 Python3.13|Success,63 source files|
|Final union changedPython/live-scope Ruff|Raw exit1, exactly1 approved UP046 at commands.py74:23; no other diagnostic|
|AST syntax all aggregate changedPython|98 parsed under3.13|
|Final private API consumer/runtime probes|Pass, detailed below|

The final response import-only reorder occurred after its44-case pass; source semantics and test AST are unchanged. Root must run mandatory whole-agent then exact-seven order, whole owning packages, unchanged Chat/telemetry modules, root pytest/full collection, full-root Ruff (expected326 archived+1 approved=327), exact aggregate typing and formal independent source/API validation against the frozen candidate. No broader listener-owning suite was run by remediator. The historical original PTY timing failure is retained in root evidence; the new synchronized script is not claimed to reproduce that old failure.

## API contract evidence

`final-api-probe-results-02.json` and guarded log pin original/current source and consumer hashes for all six UP046 classes. Each baseline and final class rejects both Parent→Child and Child→Parent with four intended return-value errors, while same-type positive accepts. Thus the five converted classes remain invariant and untouched CommandRegistry remains invariant. Existing genuine direct CommandRegistry conversion changes it to contravariant; initial stop/alternatives/compatibility matrix evidence remains retained and approved A06/WVR003 is its sole exception.

Moltbook original/final parent/child Pydantic schemas, dumps, public subscripting and missing required child-field rejection are identical. Positive function consumer accepts typed and legacy MemoryLLMClient annotations, bounded structured return types, coroutine return inference, metric formatting and Pydantic validation; negative consumer rejectsstr model bounds exactly twice. Runtime validate_return_type accepts valid model data and rejects non-model type and missing required fields. Six classes' same-type positive and both cross-type negatives are meaningful, separate from aggregate typing.

The first final private bound-negative probe erroneously resolved installed editable imports as untyped when only the consumer was targeted; that attempted log is preserved. The successful second probe explicitly includes the defining five source files, checks6 files, and observes the exact two intendedtype-var rejections; no product change resulted.

`alias-site-review.json` records all12 UP040 sites;11 stay insideTYPE_CHECKING and are absent at runtime in both forms. MemoryLLMClient's runtime alias object changes toTypeAliasType as standardPEP695 syntax. Tracked Python consumer inventory has no isinstance/issubclass, get_args/get_origin, __args__/__origin__ or alias identity introspection caller; annotation consumers preserve typing. External runtime alias introspection compatibility is not claimed.

Response coverage: Memory31 cases cover both published branches, contentNone/empty/value, reasoning, optional/zero sampling, limits/timeouts, warningonce, valid structured model and exact legacy identity, malformed/non-object JSON, invalidrequired model field, invalidlegacy _parsed_model rejection, and exact service exception identity. Selected Chat13 cases cover both models, contentNone/empty/value, omittedusage values, model/reasoning, translatedtoolcalls, raw identity, forwarding/defaults, typedcontent_filter refusal with emptyprojection/raw finish_reason retained, serviceexception identity and malformedpublic tool-call ValidationError propagation unchanged from both mocked service branches. Legacy public response has no refusal field; no invented field/coercion was added. All upstream methods are mocked; model/schema construction is synthetic.

## Safety and remaining ownership

`completion-test-preflight-final.json` pins9 changed test/source files,36 direct helper hashes, import inventory, exact child hash and execution effect/targets. The fixture's trackedrunpy helper, warnings/global restoration, mocks/respx, fake runtime, boundedPTY subprocess and no-listener selected nodes were reviewed. Root must independently review this plus full selected-package setup/teardown before mandatory broad collection/execution.

No actual new scope/API stop remains. Initial actual CommandRegistry compatibility stop was reconciled by maintainerA06/WVR003 and freshCDR011 READY. Incomplete in-scope reader assertions, app-gate child reference, new response test empty request inputs and necessary imports were corrected; their failure logs are retained. No additional failure was waived. Remediator awaits root-owned validation results for any exact bounded corrections.

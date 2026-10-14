# CHANGES_REQUESTED

Independent full work-unit review of CD-MCP-UP-001 / MCP-UP-02A. Two mandatory conformance gaps remain. All required automated gates were rerun; their passing results do not resolve these independently reproduced gaps.

## Candidate and authority

- Candidate: `4f3574c8d3fe6cca25d9835eda811ebda262429c`.
- Product candidate parent recorded by request: `d4030a25f6e4a97aaef9df90659b9ab8ae9aaa24`.
- Construction base: `9e11fb7aec73745cb38dc1702e54481935945ecb`.
- Original accepted product baseline: `46005353046553477417a730f05ff21ead64a00d`. Baseline snapshot HEAD is preparation commit `8f80463e78ea4836fcbe1d87b882656365d2de23`; its 30 intervening changes are process documentation only. Independent comparison confirms no package/source/test/checker/root metadata/lock differences from the original product baseline. [Baseline identity](baseline-identity.json).
- Exact reviewed diff: `9e11fb7..4f3574c`; complete binary diff retained in [full.diff](full.diff).
- Clean isolated checkout, branch `feature/friday-mcp-protocol-upgrade`, before and after review. Candidate source, tests, authority, board and evidence were not edited. [Freeze receipt](freeze-closeout.json).
- Authority manifest SHA-256: `1d9c8dded9ebf1922269b03100aee3520e4bc58f46a4b9dfe92c5359a28622c1`. All 28 listed controls match their declared hashes, including approved directive/A01/approval, accepted MCP safety and telemetry controls. Original approved existing-product hashes match the accepted baseline. [Independent inventory](inventory.json).
- All ten full captured normative sources match both stored and decompressed hashes; authoritative dated schema is `2026-07-28`, upstream commit `271ecc9accafdd9b83a3c869fa67c22953b2af80`, SHA-256 `742750af0bb8c716e7030c4977c992b55d1adc4407e9e66997db5846baedc2cd`. Decoded inputs retained in [normative](normative/).
- Exactly twelve product paths changed; no unauthorized product paths. Other diff paths are board/packet/execution/validation records, including lossless compression of archived process scripts. All 136 stored/decompressed builder evidence artifacts match their manifest; this is integrity evidence, not adoption of the builder's conclusions. [Integrity receipt](candidate-evidence-integrity.json).
- Candidate lock exactly equals the decompressed approved proposal, SHA-256 `aab33ed773dcdb50a65dd86af84bd1e6e26dc3486da7b04588082d72a7b18ce2`. IDNA `3.11 -> 3.20` is the sole existing-version-set change; the twelve added SDK dependency packages match the approved inventory. No dependency synchronization was performed during review. [Inventory](inventory.json).

## Independence and review provenance

Reviewer: `/root/mcp_up02a_validator`, an independent Codex subagent in a fresh delegated context. Model family is described by the runtime as GPT-6; exact backend/model version is not exposed. Review date: 2026-10-12 UTC. Context contains the frozen request/environment/constraints and controller status messages, not the builder's private session or reasoning. No builder verdict was inherited or used. Archived environment preparation scripts/receipts were inspected to establish interpreter, isolation and permitted effects; checks below were independently executed against current source.

First independent check timestamps, final timestamps, exact commands/environments, guard hash and stdout/stderr hashes appear in [command-ledger.json](command-ledger.json). Review mode: full work-unit, read-only; neither an initiative aggregate acceptance nor maintainer acceptance.

## Findings

### VAL-UP02A-001 — medium — recognized modern errors can trigger legacy fallback

Affected source: `packages/friday-mcp/src/friday_mcp/client/base.py:220-235`.

Requirement: approved `protocol-contract.md:43-46` permits auto fallback only on a **non-modern** error/timeout, according to stdio. Frozen `basic/versioning.md`, Backward Compatibility, says a recognized modern JSON-RPC error identifies a modern server and the client stays modern. Frozen `basic/transports/stdio.md:136-143` likewise distinguishes recognized modern errors from all other errors. The dated base protocol/schema define `-32021` as `MissingRequiredClientCapability` and `-32022` as `UnsupportedProtocolVersion`; HeaderMismatch `-32020` is also a recognized modern code (its actual header semantics are HTTP-specific).

Observed: `_initialize()` exempts only `-32022`. A synthetic discovery reply with the modern `-32021` code and `data.requiredCapabilities` makes an auto client issue `initialize`, send `notifications/initialized`, and report negotiated version `2024-11-05`. The same fallback happens for `-32020`; `-32022` correctly stays an error with only the probe emitted. The `-32021` case alone establishes the relevant defect; this report does not assert that a HeaderMismatch is a conforming stdio server response.

Reproduce with `python3 independent-review/run_check.py adversarial-probes work /private/tmp/friday-mcp-upgrade/venv/bin/python /private/tmp/friday-mcp-upgrade/independent-review/adversarial_probes.py`, from `/private/tmp/friday-mcp-upgrade`. [Probe source](adversarial_probes.py); [raw observed methods/versions](checks/adversarial-probes/stdout); [command receipt](checks/adversarial-probes/receipt.json).

Risk: modern failures are misclassified as legacy-era detection, initiating the wrong handshake and selecting a different protocol profile. This violates the approved era boundary even though the candidate correctly avoids tool-call replay.

Required mitigation: recognize the applicable modern reserved error family at the wire boundary and surface a fixed safe error without fallback on a recognized modern error. Preserve fallback for varied **non-modern** codes and the probe timeout; do not reinterpret Friday local `MCPToolExecutionError` codes as peer wire meanings.

Required regression evidence: auto probes returning `-32021` and recognized modern error controls issue no `initialize`/initialized notification; `-32022`, non-modern `-32601/-32602/-32000`, timeout, late IDs and safe exception/log privacy remain covered. Keep docs consistent with the implemented recognized-error decision; no new runtime/config/HTTP capability is authorized.

### VAL-UP02A-002 — medium — modern protocol metadata and known schema fields bypass validation

Affected source: `packages/friday-mcp/src/friday_mcp/client/protocol.py:200-237,259-274,324-349,493-525,558-592`.

Requirement: approved `protocol-contract.md:48-50` explicitly requires rejecting malformed metadata; CD-MCP-UP-001 requires JSON boundary validation and malformed/invalid catalogs/results to fail safely. Conformance mapping makes the full dated TypeScript schema authoritative. Frozen base `basic/index.md:336-345` and schema `MetaObject:42-48` require valid metadata prefix/name grammar. Dated `Tool._meta` and `TextContent._meta` are `MetaObject`, `ServerCapabilities.tools.listChanged` is boolean, and text `Annotations.priority` is numeric.

Observed independently:

- Discovery and tool-result `_meta` accept `{"bad prefix/key": ...}`.
- ToolDefinition/CatalogPage accepts `_meta: []` and returns the malformed tool as a successful catalog member.
- ToolResult accepts a text block with `_meta: []` and treats its text as a successful result.
- Discovery accepts `capabilities.tools.listChanged: "not-a-bool"`; ToolResult accepts `annotations.priority: "high"`.

All six counterexamples return a typed parsed model instead of a safe boundary error. Only selected outer `_meta` objects are checked; key grammar and nested protocol structures are not validated. [Independent probe source](adversarial_probes.py); [raw accepted counterexamples](checks/adversarial-probes/stdout); [receipt](checks/adversarial-probes/receipt.json). The existing malformed-envelope tests cover `_meta: []` at one outer location and miss these cases.

Risk: the declared strict modern boundary reports successful catalogs/results for messages that violate the controlling metadata/schema contract. Malformed known fields can cross public catalog APIs into downstream consumers. Opaque treatment and size limits preserve several safety properties but do not supply the required conformance validation.

Required mitigation: perform bounded, context-aware validation of the **named protocol structures** actually handled by the modern profile: result/notification metadata, discovery capability/identity structures, Tool metadata/known optional fields, and supported TextContent metadata/annotations. Validate metadata grammar and reserved typed fields where the schema declares them. Preserve unknown extension metadata as bounded JSON without making trust assumptions. Fail malformed catalogs without publishing a partial list; expose only fixed safe failures and retain the established legacy behavior.

Do **not** recursively treat arbitrary `structuredContent`, tool arguments, `inputSchema` annotations/default/examples or other application JSON keys named `_meta` as protocol metadata. Those are application data and may contain arrays, arbitrary key names or other JSON values. Do not fetch links, references, icons or metadata URLs while validating shapes.

Required regression evidence: modern discovery/result/nested Tool/TextContent `_meta` object/grammar failures and malformed known capability/annotation types; positive valid metadata/known optional fields; safe logs/reprs; a good first page followed by malformed tool metadata returns no successful partial catalog; legacy extraction remains compatible. Add positive application-data cases with `_meta` inside structured content, arguments and schema annotation values to prove the context boundary. Package docs should accurately describe strict modern parsing and any optional shape limits; no arbitrary application-data schema change is authorized.

## Requirement-to-evidence coverage

Statuses below evaluate each mandatory criterion, not merely command success. Remaining failures point to the numbered findings; all other claimed checks cite current source and independent raw evidence.

| Criterion | Evaluation | Independent evidence |
| --- | --- | --- |
| CD-AC-01 typed bounds/profiles/default compatibility | PASS for typed immutable models, validated ceilings and explicit profiles; metadata shape completeness is tracked separately below | `protocol.py:ProtocolLimits/FrozenJSON/Discovery/ToolDefinition/ToolResult`; `base.py` and `stdio.py` keyword-only constructors; focused limits/snapshot/default tests; scoped Mypy/Ruff receipts |
| CD-AC-02 discovery/metadata/capabilities/version | FAIL for recognized modern error fallback and malformed known discovery fields | VAL-UP02A-001/002; otherwise current per-request metadata, honest empty capabilities, exact legacy version and no-intersection tests pass in focused/interop evidence |
| CD-AC-03 envelope/IDs/safe errors/no fallback/cross-settlement | FAIL for required malformed protocol metadata rejection | VAL-UP02A-002; otherwise invalid/bool/null IDs, result/error exclusivity, wrong/late/duplicate IDs and safe peer errors pass; `-32022` never falls back |
| CD-AC-04 complete bounded catalog | FAIL for malformed nested Tool metadata accepted as a catalog success | VAL-UP02A-002; otherwise complete pagination/fresh snapshots, cycles/pages/entry/byte/duplicate-name caps and failed-refresh invalidation pass in focused tests |
| CD-AC-05 result disposition/fidelity/schema/no replay | FAIL for malformed supported TextContent metadata/annotations accepted as success | VAL-UP02A-002; otherwise required tags, unsupported content/input, text/mixed/scalar/array/null preservation, output-schema invalid/unsupported safe errors and no mutation replay pass in focused/real-child tests |
| CD-AC-06 deadlines/caps/cancellation | PASS for required exercised paths | `base.py:_request/connect/list_tools/_cancel_request`; `stdio.py:send/receive`; focused send-stall, total connection/fallback/catalog deadline, allocation/concurrency, cancel-resistant send and outgoing limits; interop issued-call cancel/timeout/oversized-frame tests; raw focused/package outputs |
| CD-AC-07 lifecycle/privacy/provider preservation | PASS for accepted regression and inspected source/diff | Existing lifecycle tests inspect process/tasks, retained failed cleanup, cancellation/EOF and primary exception; interop checks owned process exit; source logs use fixed messages; no telemetry/Core/Runtime/Chat source changes or new global tracing/provider hooks; cross-package/root reruns pass |
| CD-AC-08 wire interoperability/docs/dependencies/gates | Required automated/real-child gates PASS; conformance completion withheld for findings | Official SDK 2.3.0 actual stdio child in modern/auto, deterministic exact 2024-11-05 peer, one-call ambiguous failure counts and task/process cleanup; package README documents profiles/schema limits; approved exact lock/scope hashes; all check receipts below |

[Independent normative clause ledger](normative-clause-ledger.json) covers every line with capitalized MUST/REQUIRED/SHALL in all ten complete frozen sources: 222 source-line records (47 PASS, 8 FAIL, 1 PARTIAL, 166 NOT_APPLICABLE). Multiple mandatory keywords on the same line remain within that row and the adjacent wrapped source context. This is a source-line inventory, not an inflated claim of 222 independent protocol requirements. Applicable typed schema structures without uppercase keywords are separately classified in the same ledger. Findings aggregate the failing rows into two remediation items.

HTTP bindings/OAuth/server obligations, undeclared extension handlers, subscriptions, sampling/elicitation/roots, icon rendering and MRTR retry-conditional obligations are expressly out of this first tools-only stdio client profile. Core input-required recognition, opaque-state handling, no automatic continuation and safe unsupported outcomes are exercised. The approved bounded 2020-12 output-schema feature subset is implemented/documented; this report does not claim support for every JSON Schema keyword or whole-initiative conformance.

## Executed checks and raw results

Exact argv, UTC intervals, allowlisted environment, stdout/stderr SHA-256 and exit codes are in [command-ledger.json](command-ledger.json); each directory below retains unabridged stdout, stderr and receipt. The private interpreter directly invokes the installed locked tools, avoiding `uv` dependency synchronization; this is an explicit equivalent offline execution environment, not a clean installation claim.

| Check | Exit/result | Raw artifact |
| --- | --- | --- |
| Board validate / next / show | 0 / 0 / 0; started, granted, named MCP branch, correct review next gate | `checks/board-validate`, `checks/board-next`, `checks/board-show` |
| Four focused client test files | 0; 123 passed | `checks/focused` |
| Complete MCP package | 0; 159 passed | `checks/package` |
| Runtime/Chat/telemetry | 0; 1211 passed, 5 existing live skips | `checks/cross-package-loopback` |
| Exact nine source/test/fixture Ruff paths | 0; no findings | `checks/scope-ruff` |
| Three touched client source Mypy | 0; 3 files | `checks/scope-mypy` |
| Complete MCP source Mypy | 0; 18 files | `checks/mypy-package` |
| Candidate and baseline raw root Ruff JSON | 1 / 1; exactly 327 matching inherited identities, no new/removed finding | `checks/root-ruff`, `checks/baseline-ruff`; `ruff-comparison.json` |
| Whole candidate workspace pytest, no exclusions | 0; 3226 passed, 14 skipped, 15 warnings | `checks/root-pytest-loopback` |
| Whole original baseline workspace pytest, no exclusions | 0; 3132 passed, 14 identical skips, 15 warnings | `checks/baseline-pytest-loopback`; `skip-comparison.json` |
| Documentation lifecycle | 0 | `checks/docs` |
| Exact candidate diff whitespace check | 0 | `checks/diff-check` |
| Independent adversarial probes | 0 as a diagnostic script; recorded counterexamples/control outcomes are interpreted above, not treated as passing conformance | `checks/adversarial-probes` |

Initial sandbox attempts are preserved in `checks/cross-package`, `checks/root-pytest` and `checks/baseline-pytest`. They failed solely at synthetic literal-loopback listener binds (Operation not permitted), including gRPC and existing HTTP capture fixtures. These are not accepted skips. The approved bounded fixture profile was rerun with `require_escalated`; every affected required gate then passed.

The full-workspace root discovery matches the repository configuration (`packages/*/tests_*`, `experiments/*/tests`). No exclusion flags were added. Pytest importlib mode and the isolated Chat tests directory on PYTHONPATH handle inherited module-name collisions. Top-level `tests/integration` are not part of configured root discovery and no new top-level integration gate was invented.

## Effects, baseline treatment and limitations

All commands use private HOME/temp/cache directories under this review, `PYTHONDONTWRITEBYTECODE=1`, importlib pytest mode, all isolated package src directories and isolated Chat tests on PYTHONPATH, and no ambient credentials or OTEL_* flags. `OTEL_SDK_DISABLED` was not set. Audit guard SHA-256: `38f6a7483d66a066336d63c14980f1acfe307ec38848f0761c6928a66989a7a8`.

Permitted real effects are the two named synthetic stdio Python child fixtures and existing literal `127.0.0.1:0` HTTP/gRPC fixtures (`test_wire_capture.py`, Chat `test_llm_adapter_migration.py`, telemetry `test_otlp_collector.py`), plus isolated synthetic filesystem regression stores. Fixture process/task ownership is asserted by the tests. The native gRPC collector has its own exact-target/channel-option guards; Python audit hooks alone cannot intercept all native-library network I/O. No live model/MCP/exporter service, user runtime state, credentials, npm/npx, dependency install, push/merge/release/acceptance or remediation occurred.

The isolated source snapshots omit 267 protected tracked paths before checkout; the original snapshot receipts were inspected for that omission contract. Private test environments reuse version-matching installed library files copied into private virtualenvs with archived hash manifests and add locked SDK validation dependencies. This is not a fresh network-resolved clean install or a claim to execute 24 platform contexts. The reviewed full lock matches the approved static-context proposal exactly; other existing version sets are independently unchanged. SDK wire interoperability actually ran, not an in-process mock.

Root Ruff is explicitly nonzero inherited debt (327 exact path/code/row/column identities); there is no new waiver or suppression. Root pytest skips exactly reproduce the baseline: disabled explicit live LM Studio tests and unavailable SciPy graph adapter test. Candidate added 94 passing tests; no new aggregate failure or skip. Warnings also remain 15 in both complete runs. No skipped infrastructure failure is counted as success.

## Recommended next gate and freeze interpretation

Keep the initiative `started` and record `changes_requested`. Convert **VAL-UP02A-001** and **VAL-UP02A-002** exactly once each into a bounded remediation directive under the existing twelve product paths and existing authority. Commit a corrected frozen candidate and dispatch a fresh independent full-work-unit review; neither this result nor passing tests authorize completion, acceptance or later units.

No controller closeout changes were made during this review. Adding immutable review evidence/process records after the verdict does not retroactively change the reviewed candidate. The packet README is expressly hashed in the authority manifest: changing that frozen control or refreshing its hash is an authority-input change under the stale-review rule, not something the reviewer can silently grandfather. Preserve the original candidate/manifest/report and declare later process transitions separately; any governed deliverable or controlling-authority change requires a newly frozen candidate and fresh review. A remediation candidate already requires that fresh gate.

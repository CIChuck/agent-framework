CHANGES_REQUESTED

Reader copy: only source hyperlinks are adapted to repository-relative paths. The exact original report is retained in [report-original.md.gz](report-original.md.gz) and the original review archive; original SHA-256 `9b12286237b36d455840be9a188b2a83f4f7230d3ad7993e6f1dc8090b4d18a3`. Verdict, findings and evidence text are unchanged.

Fresh-context independent VAL-003 review of REM-002 execution delta and aggregate TELEM-01, 2026-10-05. Reviewer: `/root/telem01_rem002_validator`, GPT-6 session identity; exact backend model version unavailable. Frozen candidate `faa2dc0c0a25f1db4fa244185de8ddcae4153389`; preparation base `2155a0fc51f5b20dea4e35c6cfc70f1d52002735`; delta base `3a690505c8a82aa2cf8abfb872848e64f084e2b3`. All12 controlling document hashes, authority-manifest hash and fixed network-guard hash match the request before/after. Product paths are unchanged from3a69050; aggregate product delta is limited to the approved Chat/Composite sources, tests and README files. No new aggregate product defect was established by this review. AC-06 still lacks passing or waived mandatory gates.

## Finding VAL-003-F01 — high — unwaived aggregate verification gates remain unresolved

Affected scope: TELEM-01 AC-06 and current A03 verification, including mandatory root Ruff, complete affected-package/root suites and genuine advertised-minimum runtime evidence. [Tactical plan:24](../../tactical-plan.md) maps these gates to AC-06. [Verification profile:31-35,76-85,115-123,127-141](../../verification-profile.md) prohibits treating unchanged baseline failures or narrower successes as waivers. [Independent validation policy, VERIFIED](../../../../../reference/policies/independent-validation-policy.md) requires all mandatory deterministic checks to pass or be covered by an approved waiver.

The current A03 setup successfully collects the whole root suite and the approved3-node Chat rerun passes. These improvements provide additional evidence, while the mandatory broad commands still return1. No waiver exists. The exact dispositions are:

| Gate / classification | Candidate | Preparation base | Reproducible evidence |
| --- | --- | --- | --- |
| Root Ruff — unchanged repository lint debt |337 errors, exit1 |337 errors, exit1 |candidate-root-ruff.log and baseline-root-ruff.log are byte-for-byte identical, SHA256 `eb436074cbed2a5b92ca4f2040f953b45e543106a023f5f26da0314b17c52284`; fresh-outcome-comparison.json |
| Full Chat + telemetry — unchanged failure/permission IDs |724 passed,5 skipped,1 failed,3 errors, exit1 |676 passed,5 skipped,1 failed,3 errors, exit1 |candidate-packages.log:281-285; baseline-packages.log:279-283; fresh-outcome-comparison.json |
| Full root A03 — unchanged failure/permission IDs |2699 passed,1 skipped,16 failed,11 errors, exit1 |2651 passed,1 skipped,16 failed,11 errors, exit1 |candidate-root-execution.log:1119-1146; baseline-root-execution.log final summary; fresh-outcome-comparison.json |
| Genuine3.10 Chat runtime — frozen baseline dependency incompatibility |Observer import fails at unchanged LiteLLM compact.py:17 |Chat runtime import fails at same line |candidate-python310-chat-import.log:1-45; baseline-python310-chat-import.log:1-45; api-review.md |

The package failure is the unchanged provider-free PTY assertion requiring acknowledgement within0.8s, [test_reorganization_terminal.py:104-118](../../../../../../packages/friday-chat/tests_chat/test_reorganization_terminal.py). Root failures additionally comprise seven runtime/native-tool registry expectations (`recall_memory` absent), two optional DOCX/XLSX-reader dependency expectations when readers are installed, and six Web/SSRF expectations under the frozen guard. All16 failure IDs and11 error IDs match baseline exactly. These results establish no introduced telemetry-source failure. They still leave mandatory aggregate gates nonzero.

All11 broad listener errors are `PermissionError: [Errno 1] Operation not permitted` at fixture bind. Only the three approved Chat nodes were rerun with privilege; they passed3/3 at both revisions. The eight LLM wire-capture nodes remain unprivileged and nonzero. No extra privilege or test exclusion was inferred, and the3-node passes do not make broad runs PASS.

The genuine Python3.10.19 environment contains127 distributions, all versions matched to frozen lock, zero installed RECORD hash mismatches, and127 supplied origin URL/hash pairs independently matched to lock artifacts. Genuine public `friday_telemetry` CompositeProvider/DebugTelemetryRecorder import/start/end **passes at both revisions**. Genuine Chat observer import fails through unchanged package initialization -> Memory -> LLM -> LiteLLM1.100.1, whose compact.py:17 directly imports `typing.NotRequired`, unavailable in3.10. This is partial runtime evidence; no Chat observer3.10 lifecycle pass is claimed. Typing-extensions4.15.0 is already installed, but it does not repair that explicit import. No dependency edit, installation, download, import stub or patch was attempted.

Risk: marking VERIFIED would erase nonzero AC-06 gates and imply a genuine3.10 Chat runtime result that is unavailable. Required mitigation is a maintainer-controlled disposition for each remaining gate: bounded cleanup/repair authority or a precise approved baseline exception for root lint and test debt; a bounded decision for the eight unprivileged LLM fixtures; and compatible locked3.10 runtime authority or an explicitly approved minimum-runtime disposition. Current REM-002 authorizes none of those expansions. WVR-001 remains proposed and its all-other-gates-pass condition is unmet. Any implementation/dependency/authority changes require a stable new candidate and fresh review. Required follow-up evidence must rerun the affected frozen commands without additional exclusions, preserve exact baseline differences, and demonstrate genuine Chat observer import/lifecycle if runtime repair is authorized. Documentation must record each decision honestly; no source remediation is prescribed or authorized by this report.

## Required checks and supporting acceptance evidence

All commands, exact argument lists, cwd/revision, nonsecret environment values, exit status, duration and log hashes are in per-command JSON files and evidence.json. These are fresh retrospective checks, not pre-build baselines. Static baseline commands used the original isolated preparation base; before broad execution the controller supplied a fresh checkout with exactly identical complete tracked hashes. Fresh-baseline root collection was repeated before root execution. Operational-addendum.yaml records that relocation and the narrow synthetic ignored-artifact allowance; original request unchanged.

| Check | Candidate | Baseline |
| --- | --- | --- |
| Required focused6-module suite (baseline omits absent telemetry.py test) |135 passed, exit0 |87 passed, exit0 |
| Root collect-only, importlib + exact2 live exclusions |2727 collected, exit0 |2679 collected, exit0; repeated at fresh base |
| Changed-file Ruff, exact10 Python paths (baseline existing subset) |exit0 |exit0 |
| Changed-source mypy Python3.10 /3.13, exact6 paths |both exit0 |both exit0,5 existing paths |
| Changed-source Python3.10 syntax |6 files, exit0 |5 files, exit0 |
| Independently reviewed minimum APIs |3.10 stdlib and Pydantic API evidence passes |Same applicable frozen metadata/API branch; no observer file yet |
| Board validation / documentation lifecycle |both exit0 |both exit1: isolated tracked base lacks docs/planning/active lane |
| git diff --check |exit0 |exit0 |
| Exact3 privileged Chat loopback nodes |3 passed, exit0 |3 passed, exit0 |
| Genuine public Composite3.10 lifecycle |exit0 |exit0 |
| Genuine Chat3.10 runtime |exit1, above |exit1, above |
| Independent contract probes |9 passed, exit0 |Not a substitute for baseline required suites |

The baseline governance failure is the absent untracked/empty lifecycle lane in the exact tracked preparation tree, not an introduced candidate governance regression. Its nonzero logs are retained; candidate governance passes. Full package skips are the5 explicitly gated Chat live-model nodes (`test_live_primary_complete_accepts_supported_controls[disabled/enabled]`, stream, automatic-tool-selection and bounded-turn-processor flow), reason `set FRIDAY_CHAT_LIVE=1 to authorize loopback LM Studio requests`. Root's single skip appears in memory test_graph.py and is `TestElementXGraphStore::test_rank_nodes_pagerank`, which uses importorskip('scipy') at source:250. Skip identities/reasons were established from current source and progress output; default broad reports did not print verbose skip details. No activation flags were provided.

AC-01 through AC-05 have source/test support within their TELEM-01 scope:

- AC-01: strict default-disabled ConfigDict and safe loader errors at config.py:594-602,911-922; compatibility fixtures, local enabled/default/unsupported/malformed/unknown-field tests and independent safe-error probe pass. Langfuse configuration remains independent.
- AC-02: observer constructed before real/fake service assembly at runtime.py:1221-1242, retained at1320-1322, with caller-owned injection even when disabled; CLI invokes the same build path and reports snapshot state at cli.py:111-123. Focused real-stub/injection/CLI tests and independent pre-construction probe pass without vendor traffic.
- AC-03: app.py:405-458 observes completion after existing cleanup at536-550; failed cleanup and cancellation preserve behavior. telemetry.py:93,104-117,166-179 keeps256 immutable events and cumulative counters. Independent cancellation waits for async-client cleanup, then records cancelled/shutdown_failed identically to both providers. Bounded300-event failure probe and frozen-snapshot assertions pass.
- AC-04: telemetry.py:137-164 validates current public MCPEvent or closed lifecycle payloads, rejects reserved/unknown/foreign-session/content fields with categorical counts, copies safe attributes to sinks and never exports exception text. Public accepted MCP schema/redaction and planted sentinel tests were independently read. Focused safe MCP, privacy and rejection tests plus independent probes pass.
- AC-05: composite.py:57-103 maps child/parent IDs and pins membership, reserves all published IDs for instance lifetime, generates IDs with collision checks, rolls back partial starts, copies nested payloads and consumes ownership before best-effort end. Current tests and independent active/completed/generated-ID reuse, stale-end, parent/replacement, empty-composite, nested-mutation, rollback/failure-count and exactly-once probes pass. Lifetime ID-string growth is documented in telemetry README.

Reviewer probe v1 contained a counting error:604 emitted diagnostic records minus256 retained gives348 dropped, not349. The corrected probe passes; v1 source/log retained. The initial guard-check command had a quoting SyntaxError before execution; corrected file-backed parent/subprocess DNS denial passes. Neither reviewer mistake is a candidate defect or a passing gate; both nonzero records remain in evidence.json.

## Isolation, unchanged state and limits

[preflight-review.md](preflight-review.md) records current source/import/helper/subprocess review and controls. Test environment uses frozen network guard, isolated package sources, isolated Chat helper and root, fixed allowed nonsecret values, offline/no-sync operation and reviewer-owned TMPDIR/cache paths. Source-resolution logs confirm isolated package origins. No credentials, vendor/live services, remote exporter/runtime activation, original application state, or source/docs/tests/config/authority/Git mutation occurred.

`final-state-comparison.json` and complete before/after tracked SHA256 manifests prove candidate and fresh base remain identical, HEAD/status/diffs unchanged, with all controlling hashes unchanged. The existing unchanged synthetic OTel console fixture is locally captured; shutdown closed-file exporter warning occurs at both revisions and is retained as fixture behavior, not a claim of remote/exporter readiness. Exactly one permitted ignored synthetic prompt/transcript audit summary was generated per isolated root; its path/hash is in candidate/baseline-synthetic-artifact-after.json and retained in place. Prior baseline artifacts were preserved.

All required checks and adequate independent probes are complete. No additional broad repetition is needed. No waiver, completion, acceptance, later telemetry work, source/dependency repair, publication, merge or delivery follows. Work must remain started with the numbered finding returned for a maintainer disposition.

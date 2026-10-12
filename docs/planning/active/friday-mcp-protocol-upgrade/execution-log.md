# MCP upgrade execution log

## 2026-10-12 — MCP-UP-01 preparation

Maintainer direction: "lets move onto the mcp upgrade" following the proposed
MCP-UP-01 preparation gate. Prepared current baseline, primary-source revision
check, protocol/compatibility contract, SDK/dependency decision, build/tactical
plans and exact twelve-path CD-MCP-UP-001 proposal. No product construction or
implementation approval is inferred from this progression request.

Baseline `46005353046553477417a730f05ff21ead64a00d` includes accepted core
TELEM-01 through04. Checked fifteen accepted telemetry product hashes and the
forty-six acceptance-control hashes. Preserve TelemetryInterface and queue
Langfuse after MCP acceptance. Existing source core remains 2024-11-05; new
revision/profile decisions are proposed, not implemented.

Planning validation: board/dashboard consistency, documentation lifecycle,
proposal control/source hash checks and diff whitespace checks. Existing
client/base.py and client/stdio.py Ruff and Mypy checks pass. SDK/network
interop, dependency resolution, product tests and independent product validation
have not been executed. No source, tests, package metadata, lock or user config
was edited; unrelated dirty/deleted/queued assets were preserved.

Next gate: maintainer review of the build/protocol/tactical contract and
CD-MCP-UP-001; then frozen approval/branch/start preparation and only the first
approved construction slice. HTTP, remote YAML, server and Langfuse work retain
their separately bounded scopes. Proposal remains queued/not_granted.

## 2026-10-12 — approval and normative-source clarification

Chuck Russell explicitly approved the contract and CD-MCP-UP-001, and asked
whether the packet specifically matches the new MCP specification and is pegged
to the appropriate research. Recorded the exact statement and original seventeen
proposal-control hashes/twelve-path product scope in [approval.json](approval.json).
Made official dated specification/schema conformance explicit and added
[research-to-acceptance mapping](conformance-matrix.md). No product-scope or optional-feature expansion.

Official latest still selects 2026-07-28. The TypeScript schema linked by that
specification is normative; SDK 2.3.0 is counterpart evidence and Anthropic
connector documentation is context. Complete normative-byte and SDK artifact
hashes remain required before product edits. Board approval authorizes execution
preparation and only CD-MCP-UP-001; later construction directives remain separate.

Captured complete public normative bytes for nine dated documents and the
TypeScript schema, archived losslessly with URL/size/content/artifact hashes.
Schema upstream commit `271ecc9accafdd9b83a3c869fa67c22953b2af80` was fetched
separately and its full bytes match SHA-256
`742750af0bb8c716e7030c4977c992b55d1adc4407e9e66997db5846baedc2cd`.
These inputs are research authority, not executed product-conformance evidence.


## 2026-10-12 — approved first construction slice started

MCP dedicated branch now derives from telemetry merge1302b5f and approved planning
checkpoint `a3c0cbdc867ca3535f611c2461ff080a991de86c`. Original approved product hashes remain unchanged.
Move packet to active, repair scheduling links, preserve original approval bytes
and original queued-control hashes at that checkpoint, and hash active controls.
Started/granted on feature/friday-mcp-protocol-upgrade for CD-MCP-UP-001 only.
Construct and validate in an isolated sparse snapshot excluding protected state
before checkout. No later-unit or delivery authority is added.


## 2026-10-12 — SDK dependency conflict; A01 prepared for approval

Two isolated sparse checkouts exclude267 protected paths before checkout; both
use committed started/granted authority8f80463 without a dirty-work overlay.
PyPI confirms SDK2.3.0 and exact artifact hashes. Default and minimum-httpx2
resolutions require an existing IDNA update. Original no-churn resolver exits1:
SDK2.3.0 -> httpx2>=2.10.0 -> idna>=3.18 conflicts with idna3.11.
Prepared exact A01 proposal and full lock/metadata/registry/command receipts.
Only IDNA changes among existing version sets; twelve new SDK transitive packages
are individually inventoried. All other contexts still require formal preservation
checks before execution. Restore isolated pyproject/lock to original bytes; no
client/test edits, dependency install, SDK execution or product checks are claimed.
Started/local; execution_phase planning; validation_state blocked. Approval of
this bounded exception and renewed frozen controls is the next gate.


## 2026-10-12 — A01 approved; dependency verification resumed

Chuck Russell explicitly approved A01 and asked about regression risks. Recorded
the exact statement and frozen original proposal/dependency evidence in a separate
receipt; retained original CD-MCP-UP-001 approval bytes. The approved target is
IDNA 3.20, rather than the distinct older 3.2 release. Permit only IDNA 3.11 to
3.20 among existing versions. Resume isolated reproduction and supported-context
comparison before locked installation. No product completion or independent
validation is claimed.


## 2026-10-12 — A01 dependency reproduction and offline comparison

Reproduced exact approved lock hash from baseline, then verified offline lock
consistency. All existing selections and edges across24 supported-context
samples and all other existing artifact records are preserved. Ran352 offline
IDNA operations per version:57 representative HTTP URL checks unchanged;12
other semantic changes include stricter remapping/length rules and a rare
Unicode-to-YARL URL mapping. Full results, raw outputs and script/hash receipts
are retained in execution/idna-regression. Source construction and official
SDK/full regression/independent validation remain pending. Shared IDNA3.11 and
root twelve-path product baseline remain unchanged.


## 2026-10-12 — client-core candidate frozen for independent review

execution_phase: validation; validation_state: in_review. The twelve approved
product paths are implemented. Final product gates and independently reproduced
baseline debt are retained in execution/client-core/. Private installed-library
reuse and pytest import resolution are disclosed in the implementation report.
No live service, credential, shared state or later-unit changes occurred. The
initiative remains started/local. Commit the stable candidate and issue a fresh
read-only review; no self-VERIFIED or acceptance/delivery inference.


## 2026-10-12 — independent findings and bounded remediation

execution_phase: remediation; validation_state: changes_requested.
VAL-UP02A-001 and002 are recorded exactly once in REM-MCP-UP-001. Preserve
4f3574c and its full raw independent evidence. All automated gates pass; modern
fallback/metadata conformance gaps prevent VERIFIED. Separate remediator follows
existing approved criteria and exact paths. No new authority, waiver or delivery
is inferred. Commit a corrected candidate and conduct fresh delta/full review.


## 2026-10-12 — remediation candidate dispatched for fresh review

execution_phase: validation; validation_state: in_review. Stable builder candidate
9283146f10defcb8095270cd7a1b740aa2830112 corrects exactly VAL-UP02A-001/002 within original scope.
Original failed review is retained; fresh delta and full work-unit review required.
Current process-only transitions are separately recorded in current-process-state.json
without revising the frozen index after dispatch. No acceptance/delivery inferred.


## 2026-10-12 — corrected client-core independently VERIFIED

execution_phase: closeout; validation_state: verified. Fresh independent
VAL-UP02A-02 verifies reviewed candidate a36142fb41f59a743b72088d8cce749b71b32202.
VAL-UP02A-001/002 are resolved and the full original unit profile passes. Propose
MCP-UP-02A completion; maintainer acceptance remains pending. Whole initiative
remains started/local because HTTP/runtime/server and aggregate units remain.
Frozen authority/index/directive/product files remain byte-identical; only
review evidence and the separately referenced process-only state/board are updated.


## 2026-10-12 — maintainer accepted client-core; HTTP directive proposed

Chuck Russell's explicit “accepted” closes CD-MCP-UP-001 / MCP-UP-02A only.
acceptance/MCP-UP-02A.json records the reviewed candidate, immutable original
independent report and product/control hashes. Whole initiative stays started/local.
No delivery or later-unit approval is inferred.

Prepared separate CD-MCP-UP-002 / MCP-UP-02B: fourteen exact product paths,
2026-07-28 Streamable HTTP and explicit 2025-11-25 compatibility, bounded
headers/SSE/session/cancellation, no mutating replay, endpoint/connect policy,
synthetic real-wire fixtures, ten criteria and independent handoff. Captured and
hashed additional complete dated sources/schema. Earlier authority/index/source
bytes remain unchanged. Current next-unit state is planning/not_ready; source
construction waits for exact directive/manifest approval. Runtime/YAML/server
and aggregate units remain later gates; Langfuse remains queued after full MCP.


## 2026-10-12 — exact HTTP construction directive approved

Chuck Russell explicitly stated “approved” in response to CD-MCP-UP-002.
Separate approval-UP-02B.json and authority-UP-02B.json pin the immutable draft
and proposal manifest at 9e00288. Work unit MCP-UP-02B enters construction/not_ready
on the existing feature branch. Fourteen exact product paths and fixture-only
effects are authorized; prior frozen evidence and unrelated dirty root changes
remain preserved. No Runtime/YAML/server or delivery authority is inferred.


## 2026-10-12 — Streamable HTTP stable candidate review checkpoint

execution_phase: validation; validation_state: in_review. CD-MCP-UP-002 products
are frozen in execution/http/stable-check-freeze.json. All final deterministic
gates pass; root Ruff has exactly the inherited 327 findings. The new client
supports modern 2026-07-28 and separate explicit 2025-11-25 profiles within the
fourteen approved paths. Builder evidence and full raw receipts are retained in
execution/http/report.md and stored-manifest.json. Fresh independent review is
required; whole initiative remains started/local and later units are unapproved.
No original authority/index/directive/proposal/acceptance bytes are revised.


## 2026-10-12 — HTTP independent review requests four corrections

execution_phase: remediation; validation_state: changes_requested. Fresh full
VAL-UP02B-01 reviewed candidate 2a3cec520f20442515d3d9a5a1a33eb500bd8846. Original report and
raw probes/checks are preserved losslessly in validation/VAL-UP02B-01. All required
checks pass, but four reproduced schema/header/metadata/session-concurrency defects
prevent VERIFIED or unit completion. REM-MCP-UP-002 is a concrete six-path,
four-finding proposal; source remediation awaits maintainer authorization.
Original candidate, controls, approval/proposals and raw builder evidence remain
unchanged. Whole initiative remains started/local; no acceptance/publication.


## 2026-10-12 — bounded HTTP remediation approved

Chuck Russell explicitly stated “approved” in response to REM-MCP-UP-002.
Separate approval-REM-MCP-UP-002.json and authority-REM-MCP-UP-002.json pin the
immutable six-path directive/proposal. execution_phase: remediation;
validation_state: changes_requested until a new candidate reaches fresh review.
A separate remediator is authorized to correct exactly VAL-UP02B-001..004 and
run original CD2 gates in the same private guarded fixture profile. All prior
controls/evidence and unrelated root work remain preserved. No acceptance or
publication is inferred.

# MEMQ-001 — round3 findings returned to the maintainer

Branch: `feature/command-retirement`
Execution phase: validation (directive/design only)
Validation state: changes_requested; formal council incomplete because Sol is BLOCKED

Reviewed technical candidate: `818b42eeca4495cf34292e934dbdac34e31ca4db`.
[Round3 reconciliation](validation/memory-queries/directive-review/round3/report.md)
records Astra VERIFIED9.5, Sol BLOCKED9.4 and Claude CHANGES_REQUESTED8.9.
Technical corrections CR-01..05 are resolved. CR-06 still has the unqualified
post-SESSION instruction at reviewed README line215 (CLAUDE-001, Low).
Sol wrote a locator outside its own fresh scratch, so that receipt cannot be
counted as VERIFIED despite unchanged candidate/supplied inputs. No cleanup or
retrospective waiver was performed.

**Next gate:** Await Chuck Russell direction on MEMQ-DIR-R3-CLAUDE-001 and Sol isolation-blocked receipt after two correction cycles. No further automatic correction, product D0/D1, acceptance or delivery.

Two correction cycles are consumed. The council skill and independent-validation
policy require returning remaining mandatory findings rather than another
automatic loop. [Exact proposed sentence patch](validation/memory-queries/directive-review/round3/proposed-readme-fix.patch)
is prepared but not applied. The controller has changed only current status and
review evidence after the freeze; approved contract/directive/verifier/format
inputs retain their reviewed hashes. No new technical candidate result is claimed.

Existing [cycle2 authority](approval/memory-queries-directive-correction2.md)
and option R scope remain recorded; readiness is not cleared. Product D0/D1
has not started. The umbrella remains started/local, baseline debt stays
failed/unwaived, and original product/dirty/ignored state remains preserved.
No acceptance, UAT, later-family or delivery authority follows.

### Preserved DIAG acceptance checkpoint

## DIAG-001 — accepted; next-unit preparation checkpoint

Branch: `feature/command-retirement`
Execution phase: planning (next unit); DIAG-001 closeout complete
Validation state: verified (accepted DIAG-001); broader initiative remains started/local

Chuck Russell reported successful manual UAT and [accepted DIAG-001](approval/diagnostics-acceptance.md)
(“the uat was successful - all approved, proceed to next steps”) after Sol/Astra/Claude independently VERIFIED candidate
`be72a1e8` at 9.7 each with no mandatory findings. Product/test/probe and
artifact source `28c544fa` is unchanged. The [UAT register](uat/friday-chat-user-acceptance-roadmap.md)
records maintainer-reported results without inferred per-case detail.

**Next gate:** Prepare proposed MEMQ-001 contract and directive (planning only) after accepted DIAG-001; construction requires their exact approval. No delivery follows automatically.

The [proposed unit order](validation/step3/unit-map.json) places MEMQ-001
(`/memory`, `/insights`, `/summaries`, `/meta`, `/entities`, `/list-ingested`)
after DIAG-001. Preparation may add proposed documents, current status and
guarded characterization only; no product/test/config/dependency/lock change.
PILOT, SESSION and DIAG are accepted internal units. Remaining families, P0/P1,
TUI and full-refactor acceptance stay open; delivery stays local. Root Ruff 534,
the test_display collection conflict and registry format remain failed/unwaived.
Both dirty example files and ignored exports stay untouched.

### Preserved DIAG verified-completion checkpoint

## DIAG-001 — verified completion and human acceptance checkpoint

Branch: `feature/command-retirement`
Execution phase: closeout
Validation state: verified (bounded DIAG D1–D3 and complete aggregate)

[Final verification](validation/diagnostics/implementation/d3/verified-report.md)
reconciles all three fresh round-3 results: VERIFIED9.7 each, no mandatory findings.
Reviewed candidate `be72a1e8b5904436ec3b9eb844a5db4f71ed95c9`; corrected source/probe/artifacts `28c544fa67e934f03c212aed39ba20802b500b13`.
The runtime order finding and both documentation findings are independently
closed. Current1,991-suite/build/install receipts retain exact provenance; all
review inputs and protected local state were rechecked before closeout metadata.

**Next gate:** Chuck Russell's bounded DIAG-001 acceptance decision; manual UAT remains unrun. No next unit or delivery follows automatically.

Read the [acceptance handoff](validation/diagnostics/implementation/d3/acceptance-handoff.md)
and [17-case UAT roadmap](uat/friday-chat-user-acceptance-roadmap.md). The latter
remains NOT RUN; the handoff contains the exact installed launch command and
records fake versus real runtime limits. No acceptance is inferred from reviews
or previous amendment approval. Stop for the bounded maintainer decision.

The command-refactor umbrella remains started/local, with its active packet.
Later families, P0/P1, full-refactor/TUI and all delivery need separate authority.
Root Ruff534, the6,929-test collection conflict and registry format remain failed/
unwaived. Keep both dirty example files and ignored exports untouched. No new
product/test/probe/approved contract/build change or review loop is introduced by
this closeout record.

### Preserved round-3 validation checkpoint

# DIAG-001 — documentation correction validation checkpoint

Branch: `feature/command-retirement`
Execution phase: validation
Validation state: in_review (documentation cycle 2 / council round 3)

[Round-2 reconciliation](validation/diagnostics/implementation/d3/council-round2-reconciliation.md):
all three independently closed DIAG-D3-ASTRA-001. Sol 9.6 and Claude 9.4 requested
only current-status corrections; Astra returned VERIFIED 9.6. The amendment is
approved and the runtime correction is complete. Current product/test/probe
source remains `28c544fa67e934f03c212aed39ba20802b500b13`.

[REM-CMD-DIAG-D3-002](remediation/REM-CMD-DIAG-D3-002-status-reconciliation.md)
corrects the README next gate and PAR header/six DIAG cells, with associated
lifecycle/evidence updates only. No product/test/probe/configuration/lock or
approved authority bytes change. Existing actual 1,991-suite/build/install
receipts must be hash-verified against unchanged runtime; new runtime execution
is not required solely for prose. Every current aggregate criterion still needs
independent evidence and a fresh conformance decision.

Next: reconcile fresh Sol/Astra/Claude docs-delta then complete bounded aggregate
review, and only then propose bounded human DIAG acceptance. UAT remains unrun;
root Ruff 534, test_display collection conflict and registry format remain
failed/unwaived. Dirty examples and ignored exports stay preserved. Later
families, P0/P1, full-refactor/TUI and delivery remain separate gates.

### Preserved correction-cycle1 checkpoint

# DIAG-001 — D3 context evaluation correction validation checkpoint

Branch: `feature/command-retirement`
Execution phase: validation
Validation state: in_review (D3 correction cycle1; fresh council pending)

Chuck Russell approved [REM-CMD-DIAG-D3-001](remediation/REM-CMD-DIAG-D3-001-context-evaluation-order.md)
(SHA-256 `3078bb19…a865`) in the [exact approval record](approval/diagnostics-context-evaluation.md).
Corrected product/test/probe source is `28c544fa67e934f03c212aed39ba20802b500b13`:
one typed `context_debug_snapshot()` capability is used only for exact `--debug`;
Chat formats the selected text once, then measures the original value, and shared
code never re-measures. [Correction evidence](validation/diagnostics/implementation/d3/correction-evidence.json)
binds 12/12 legacy-equal characterization rows (9 diverged before the fix), the
unfixed-candidate call-assertion failures, nine rejected mutants with an
unchanged 539 control, 1,991 source tests (1,971 + 20 new DG-T04 cases), DIAG
68+4/SESSION 25/pilot 196 captures, two identical 154-artifact closed builds,
eight installed probes, 50+4+10 refusals, 2 source refusals, 8 restored copies
and round-1 artifacts rejected by the new installed assertions.

Next: fresh Sol/Astra/Claude remediation-delta review, then complete bounded
D3/DIAG aggregate review. The Claude seat must be a fresh context: the session
that implemented this correction also served as the Claude D2 round-2 reviewer.
Reconcile all mandatory findings before human DIAG acceptance. Root Ruff 534,
test_display collection conflict and registry format remain failed/unwaived.
UAT, acceptance, later families, P0/P1, full-refactor/TUI and delivery remain
pending or separately governed. Dirty examples and ignored exports are preserved.

### Preserved round-1 decision checkpoint (superseded by the approval above)

Branch: `feature/command-retirement`
Execution phase: remediation
Validation state: changes_requested (D3 and complete bounded aggregate, round 1)

[Council reconciliation](validation/diagnostics/implementation/d3/council-round1-reconciliation.md)
records Sol/Claude VERIFIED 9.7 and Astra CHANGES_REQUESTED 8.7. The reproduced
mandatory finding DIAG-D3-ASTRA-001 prevents aggregate verification. Stateful
accepted strings expose changed count, exception and export behavior.

Read the [proposed amendment](remediation/REM-CMD-DIAG-D3-001-context-evaluation-order.md).
It adds one typed host debug snapshot capability to preserve legacy format-then-
length evaluation while shared code retains flags/export ownership. It changes
an exact approved port/algorithm, so maintainer approval of these exact proposed
bytes is required. No implementation under the proposal is started.

Prior product/probe/build inputs and evidence remain unchanged. After approval,
a bounded remediator must correct only this finding, refresh tests and actual
installed normal/optimized proof, rebuild/replay corrected committed source and
obtain fresh Sol/Astra/Claude delta then complete bounded aggregate review.
Preserve dirty examples and ignored exports; no cleanup. Root Ruff 534,
test_display collection conflict and registry format remain failed/unwaived.
UAT, human acceptance, later families, P0/P1, full-refactor/TUI and delivery remain
pending or separately governed. No further council is launched pending decision.

### Preserved prior planning checkpoint

The following describes the preapproval preparation and is superseded by the
exact subsequent approval above.

# Command refactor — next-phase checkpoint

Branch: `feature/command-retirement`
Status: DIAG-001 proposed contract/directive prepared; exact approval pending
Execution phase: planning
Validation state: not_ready (DIAG-001); SESSION-001 remains accepted/verified

## Current checkpoint and next gate

Chuck Russell's “proceed” after the proposed next-step handoff authorizes
DIAG-001 preparation only. Read the [contract](diagnostics-command-contract.md),
then [CD-CMD-DIAG-001](directives/CD-CMD-DIAG-001-context-diagnostics.md).
Approve both exact documents before product/test implementation; approving
them together is sufficient. They explicitly propose seven new closed outcome
variants, fourteen additive exports, the narrow old export assertion update,
and two declared-type decisions. No DIAG implementation is started.

[Preparation evidence](validation/diagnostics/preparation.json) binds clean
accepted source `9dbcec54`, six metadata records and 72 repeated synthetic cases,
including scratch file effects/access/await/failure behavior. Guard/source/
comparator controls pass; related Chat244 and Commands/cohort278 pass.
The future D1–D3 proof and councils are obligations, not completed validation.
The [current council roster](approval/council-roster.md) is Sol/Astra/Claude.

Chuck Russell [accepted SESSION-001](approval/session-acceptance.md) after Sol9.7,
Astra9.7 and Claude9.6 VERIFIED the bounded aggregate; its 1730 scoped passes,
artifacts and installed proof remain accepted historical evidence. PILOT,
RET and foundation acceptance remain closed. Root debt stays failed/unwaived.
The initiative remains started/local; remaining families, P0/P1, full-refactor,
TUI and external delivery stay separate gates.


## Historical checkpoints

The [board](../../board.yaml) owns initiative state. The entire refactor remains
started; this bounded retirement unit is implemented, verified and accepted locally.
Chuck Russell directly accepted it on 2026-11-07; the
[acceptance record](approval/command-retirement.md) preserves that decision.

### Accepted RET-001 result — historical checkpoint

The [fresh independent report](validation/retirement/verified-report.md) VERIFIED
candidate `f896ef536efcc45d569f4231edfc39baab09bbc8` against merged source base
`6f291ca5755a616d9185c86dff104b660a1fba8c`, with no mandatory findings.
All nine default slash names are removed; Chat now has exactly 41 canonical
commands and three aliases. Former effects are unreachable through these names.
Retained metadata, handlers, parser and runtime behavior are preserved. Generic
custom registries remain extensible. Current guides match the supported surface.

The independent review reproduced 1,038 Chat, 145 foundation/cohort and 155 CLI
tests; source/assertion preservation, focused lint/types, metadata/lock/docs and
clean installed-package proof pass. It independently verified all 519 original
functions/2,260 assertions, 390 wheel members/668 sdist files, exact 129-package
profile and additional context-tripwire probes. Root Ruff, root collection and
older formatting failures remain explicitly failing baseline debt; no broad
success or implicit waiver is claimed.

[Exact approval](approval/command-retirement.md),
[builder report](validation/retirement/README.md),
[assertion ledger](validation/retirement/assertion-disposition.json),
[frozen request](validation/retirement/request.json) and
[independent receipts](validation/retirement/independent-evidence.json) retain
candidate-specific evidence. The controller rechecked all frozen hashes before
recording evidence/status-only closeout. No product, test, dependency, lock,
API or directive change follows the reviewed candidate.

### Historical pre-approval sequence

1. Read and approve the [PILOT-001 contract](pilot-command-contract.md): three
   shared definitions/handlers, catalog ownership, Chat routing/rendering,
   lifecycle effects, custom-registry compatibility and required dependency.
2. Read and approve [CD-CMD-PILOT-001](directives/CD-CMD-PILOT-001-help-exit-clear.md):
   exact paths, baseline capture, assertion preservation, regression cases,
   installed artifacts, independent review and stop conditions. Explicitly
   approving both exact documents together is sufficient. Neither is approved
   yet; the instruction to prepare this packet grants no construction authority.
3. After both approvals, record their hashes and execute only that pilot. Stop
   after fresh independent verification for bounded maintainer acceptance.
4. Proceed through the remaining family/P0/P1 gates and bounded directives;
   final integration/aggregate review precedes full refactor acceptance and TUI
   resumption.

No push, PR, merge, pilot/family/TUI construction or release is authorized for
this unit. The prior foundation checkpoint was delivered in PR #13; its delivery
authority is consumed. Both original uncommitted example configurations remain
byte-identical and excluded. Historical directive draft/pending labels describe
pre-approval/review states; current approval/report/board/checkpoint govern this
handoff. RET-001 acceptance is recorded separately from independent verification; it does
not accept the entire refactor or supply future construction/delivery approval.

The planning-only preparation was authorized by Chuck Russell's 2026-11-07
“proceed”. Its scope is the two proposed documents and current board/packet
navigation/authority/log records; no product, test, configuration, dependency,
lock or frozen evidence byte changes. This is the documentation-only lightweight
exemption under repository policy, not an exemption for the future pilot.
Controller validation comprises source/protected-file hashes, proposal pins,
embedded-code syntax, board/dashboard, documentation links and whitespace.
No implementation tests or independent product review are claimed for this draft.

The 2026-11-07 harness amendment now supplies runnable diagnostic scripts,
an initial frozen baseline with 193 observations and explicit G0–G5 incremental gates.
[Harness receipts](validation/pilot/harness-evidence.json) record fresh/offline
startup, seven guard refusals, comparator controls, clean-Git reproduction and
source-tamper rejection; the revised runner passes 1,038 Chat, 145 foundation/
cohort and 155 CLI baseline tests. No pilot API/adapter is implemented. Council
review and bounded feedback are authorized separately; scores do not grant
construction approval. Historical documentation-only limits above describe the
initial draft; the later exact diagnostic exemption is in current authority.

Round-one council reconciliation: OpenAI VERIFIED 9.4/10, Gemini VERIFIED 9.5/10,
Claude CHANGES_REQUESTED 8.3/10. The combined disposition is CHANGES_REQUESTED;
no majority vote overrides reproducible mandatory findings. Authorized bounded
corrections now cover closed-wheelhouse artifact commands, SQLite audit guards,
exact test ownership and complete gate commands, local G2 commits, all export
source/data and loaded-module origins, explicit shared type rules/catalogs,
receipt collisions, capture-identity controls and evidence revision history.
The regenerated baseline comes from the same unchanged Git revision, preserving
all original observations and adding three legacy falsy-focus cases (196 total).
Fresh full three-provider review is required for the corrected candidate.

Current corrected G0 evidence is [round-two harness receipts](validation/pilot/harness-evidence-round2.json):
12 refusal controls, 10 comparison controls, cold artifact build/install and all
1,338 scoped baseline tests pass with the final scratch-isolated runner.
[Correction map](validation/pilot/council-remediation.json) binds every council
finding and the explicit baseline regeneration. The older receipt paragraph
above describes round one. No product construction approval is granted.

Round two: OpenAI CHANGES_REQUESTED 8.8/10, Claude CHANGES_REQUESTED 8.5/10,
Gemini VERIFIED 9.8/10. The combined readiness decision remains CHANGES_REQUESTED.
[Current corrections](validation/pilot/council-remediation-round2.json) and
[round-three evidence](validation/pilot/harness-evidence-round3.json) now include
an executable artifact-bundle recipe: 13 workspace builds, 125 hash-verified
locked third-party artifacts, PyPika source-to-wheel lineage, exact Python
3.13.10 profile compilation and both isolated installs, repeated offline.
All 1,338 scoped baseline tests, 18 guard and 11 comparator refusals pass.
All 196 observations remain identical. The current locked baseline profile has
137 distributions; the report enumerates its differences from the separately
assembled historical 129-member profile. No product/dependency/lock change is
inferred. Actual pilot implementation and its G5 behavior proof remain pending.
Fresh full round-three council review is required for this corrected candidate.


Round three: OpenAI CHANGES_REQUESTED 8.8/10, Claude CHANGES_REQUESTED 9.1/10,
Gemini VERIFIED 9.8/10. The combined result remains CHANGES_REQUESTED,
regardless of scores. [Reports](validation/pilot/council-round3.json) retain all
findings; the controller corrects one raw report's mistaken retirement wording:
`/clear` is retained, while `/cls` is the pilot clear-screen command.

Chuck Russell explicitly authorized one further correction pass and council
after the two-cycle escalation. [Corrections](validation/pilot/council-remediation-round3.json)
now require exact whole-export inventory/types/modes and a private verified Git
archive, case-folded/short-option receipt protection, explicit uv/Python inputs
and complete installed namespace origins. [Round-four evidence](validation/pilot/harness-evidence-round4.json)
records ten source, six receipt and two origin controls; two offline artifact
trials produce identical hashes, including a poisoned-ambient replay. All 196
observations and 1,338 scoped baseline tests pass. Fresh full round-four council
is next. Product design/construction approval and delivery remain not granted.


Round-four council is complete: OpenAI 9.0/10, Claude 9.0/10 and Gemini 9.5/10;
all three return CHANGES_REQUESTED. [Consolidated report](validation/pilot/council-round4.json)
and [bounded proposed correction plan](validation/pilot/round4-reconciliation.md)
record two open defects: an embedded-equals attached-path receipt bypass and
the directive's stale contract hash. Source provenance is verified closed.
The explicit extra pass is consumed; await maintainer disposition before any
further correction/review cycle. No contract/directive/harness correction was
applied after review. Pilot construction and delivery remain not granted.

Maintainer continuation authorizes the proposed two-fix closeout and focused
independent delta plus aggregate readiness verification. The contract remains
unchanged at e625123b; proposal revision 5 updates only the directive binding
and existing receipt prose. Long equals-option parsing no longer truncates
attached short-option paths. No new full council round is being opened. After
verification, read/approve the pilot contract first and CD-CMD-PILOT-001 second
(or approve both exact documents together); then execute only the bounded
help/exit/cls pilot through G0-G5. No construction approval is inferred yet.

Final bounded correction and aggregate readiness verification are **VERIFIED**
at `dcb982cf9190306c2156c3a8050ac4d5469792be`; see the
[final independent report](validation/pilot/final-readiness-validation.md).
The four-round council history is retained: the fourth three-provider council
met all score targets, and the later focused independent check closes the two
remaining findings without reopening the council.

The next approvals, in order, are:

1. [Pilot contract](pilot-command-contract.md), including its additive shared API
   and ownership boundary; SHA-256 `e625123b8222262fb02b32aeadb2cae5c91d18ff573f04763b0af7ea3f22eb8c`.
2. [CD-CMD-PILOT-001](directives/CD-CMD-PILOT-001-help-exit-clear.md); SHA-256
   `b85be3a04035e1f8318cc6566f7767aad00355b61c49e2650c6327981fd2a982`.

One explicit approval of both exact documents is sufficient. After approval is
recorded, execute only the help/exit/cls pilot through G0-G5, then independent
implementation verification and maintainer acceptance. Construction remains
unapproved until that instruction; initiative and delivery remain started/local.

Current maintainer approval: both exact documents are approved together in
[approval/pilot.md](approval/pilot.md). Pilot construction is started on the
existing feature branch. G0 baseline precedes D1 neutral handlers/tests; a
three-provider council follows each D1/D2/D3 deliverable before advancement.
Earlier not-approved labels retain historical provenance. Final pilot
acceptance and external delivery remain separate gates.

Current deliverable checkpoint: D1 neutral API/handlers and standalone tests
(G1) are implemented; [builder evidence](validation/pilot/implementation/d1/evidence.json)
records 217 passing Commands/cohort tests and exact source/assertion preservation.
The next gate is a fresh three-provider D1 council. D2 Chat integration/lifecycle
starts only after D1 council reconciliation; D3 full regression/installed proof
and final maintainer acceptance remain outstanding.

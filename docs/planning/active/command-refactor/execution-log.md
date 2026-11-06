# Shared command refactor — execution log

2026-10-25: The maintainer resolved the
[server-neutral MCP schema proposal](proposals/mcp-schema-compatibility.md): a
bounded extensible keyword profile; faithful provider export or explicit
rejection; local pre-call argument validation; startup and inspectable
registration diagnostics; and charging the shared model-schema budget only
for admitted tools. A read-only shape probe of the three rejected Zapier
schemas found only local pointers but productive structural recursion in
each. The maintainer revised the first-release reference policy to allow
bounded local recursion while rejecting pure alias loops and external
references. No MCP tool was invoked, no credential/schema content was
recorded, and no product code or user config changed. Provider compatibility
and an exact construction directive remain open.

2026-10-25: The maintainer resolved all six policy questions in the
[MCP turn-continuity proposal](proposals/mcp-tool-turn-continuity.md): a
user-request-grounded pending task and narrow registered tool set; expiry on
completion, cancellation, task switch, session end, five follow-up turns or
30 minutes; priority over unrelated optional tools with a clear action failure
if unavailable; no override of manual or required selections; catalog
identity/schema revalidation; and Friday Chat automatic selection as the first
implementation scope. The proposal now distinguishes settled behavior from
remaining engineering design. It remains planning only and is separate from
the server-neutral schema proposal and command P0–P5 gates.

2026-10-25: At the maintainer's request, two MCP follow-ups were written up
before any further code change: [tool continuity across Chat turns](proposals/mcp-tool-turn-continuity.md)
and [server-neutral input-schema compatibility](proposals/mcp-schema-compatibility.md).
A synthetic, offline two-turn selection probe demonstrated that a Gmail
write-action candidate can be selected for an initial request and displaced by
a feedback tool on a short `Yes, send it` follow-up. The schema proposal
records the separate registration rejection of three Zapier tools. Both
documents identify open contract decisions and deterministic proof required
before construction directives; they do not advance command P0–P5 or grant
product-code authority. The maintainer's two existing Chat config edits were
left untouched.

2026-10-24: The maintainer accepted the separate project scope, requested
activation, and directed all command-refactor planning documents to the
`docs/planning/active/command-refactor/` packet. The dedicated
`feature/command-refactor` branch was initially created from `e591f720`. The packet,
five Markdown source documents and JSON command inventory were relocated;
links and board references are being reconciled as one planning transition.

2026-10-24: The maintainer directed independent branches, command execution
first, and a TUI development hold until the command refactor is completed,
tested, and accepted. The command branch was rebuilt directly from `master`
`c3426986`. Its former stacked tip is retained at
`backup/command-refactor-stacked-20261024`; the TUI branch and its uncommitted
work were not rewritten. See the [branch isolation record](branch-isolation.md).

2026-10-24: Documentation review established a [scope decision register](scope-decisions.md)
and [phase plan](phase-plan.md), clarified the planning chain in the packet
index, marked the older seven-name recommendation as superseded and separated
the six retirement cases from retained-command parity obligations in the JSON
inventory. Technical contract, retired-name response and scored outliers remain
open; this documentation pass does not advance a construction gate.

2026-10-24: The maintainer clarified that `command_refactor.md`,
`command-inventory.md` and `command-matrix.md` are the canonical intent sources
for this feature branch and ultimate build plan. The packet index, build plan,
scope register, phase plan and tactical-plan derivation were aligned to that
source order. Candidate recommendations remain distinct from accepted
decisions.

2026-10-24: After reviewing phase-plan sufficiency, the maintainer authorized
a revision to measurable gates. P0 now requires a PAR evidence ledger; P1
must fix contract choices, unit ownership, retirement order, interaction
scenarios and supported environments; P2–P3 require cumulative unit evidence;
P4 covers cross-family installed integration; P5 requires an aggregate report,
independent review, acceptance and a TUI handoff manifest. This revision does
not close P0/P1 or authorize product source edits.

2026-10-24: The maintainer requested a concrete architectural surface for the
shared command owner. The [architecture proposal](shared-command-architecture.md)
now maps proposed package ownership, Chat-owned service seams, the separate
`friday-framework-cli` registry and installed-client reuse proof. Package/API
and service-ownership choices remain P1 decisions; no product code changed.

2026-10-24: The maintainer asked to synchronize the build plan, phase plan and
shared-command architecture. The plans now preserve the 50-command source
matrix while defining a separate target, identify the proposed command package
as a P1 choice, map Chat-owned service seams and the generic CLI role into P1,
and align P0–P5 work units, installed-client proof and TUI handoff. The CLI
decision register and regression gate were reconciled; no product code changed.

2026-10-24: The maintainer flagged the tactical plan as stale. Review found
that it presumed generic-CLI reuse, omitted the new P0/P1 service and package
decisions, treated the first pilot as predetermined and requested a candidate
commit before implementation. The revised tactical plan now lists current
P0/P1 outputs, later P2–P5 receipts and the before/after directive boundary.
It also flags the scored `/security-test` retirement against the approved
six-name scope for explicit P1 reconciliation. The PAR ledger and technical
contract remain to be produced; no product code changed.

2026-10-25: The maintainer approved considering a bounded MCP compatibility
exception on this branch, then agreed to include ordinary query-bearing HTTP
MCP endpoint URLs alongside the 2025 Draft-07 input-schema fix. The
[proposed directive](directives/CD-CMD-MCP-001-compatibility-exception.md)
records both fixes, unchanged security boundaries and regression gates for
exact-scope review. Product code has not changed; command P0/P1 remains open.

2026-10-25: The maintainer approved the exact
[MCP compatibility directive](directives/CD-CMD-MCP-001-compatibility-exception.md)
for implementation on the command-refactor branch. This authorizes only that
bounded MCP unit; the command refactor's P0/P1 gate is unchanged.

2026-10-25: The MCP compatibility working tree passed the focused pre-edit
baseline (260 tests), then 1,639 MCP client, runtime-config and Friday Chat
integration tests after the first implementation pass. Focused Ruff and mypy
passed. Read-only live discovery returned five OpenAI Docs tools from both
`https://developers.openai.com/mcp` and the `?xyz` query variant. Diff review
found that the shared catalog parser needs a version flag to keep 2024 schema
behavior unchanged; [amendment 001](directives/AMEND-CMD-MCP-001-001-2025-dialect-isolation.md)
is proposed before changing `base.py`. No candidate is frozen or independently
validated yet.

2026-10-25: The maintainer approved
[amendment 001](directives/AMEND-CMD-MCP-001-001-2025-dialect-isolation.md),
allowing the selected 2025 version to be passed through `base.py` into catalog
schema validation. The 2024 behavior obligation remains in force.

2026-10-25: The amended MCP unit now passes 402 focused protocol, HTTP and
runtime-config tests, followed by 1,640 MCP client, runtime-config and Friday
Chat MCP integration tests. Focused Ruff and mypy passed for the changed
source. Documentation lifecycle passed for 658 Markdown files; board
validation passed for 36 tasks; `git diff --check` passed. Read-only live
discovery after the amendment returned five tools from both the plain OpenAI
Docs endpoint and its `?xyz` query variant. The exception is ready for a
candidate commit and independent review; no command P0/P1 result is claimed.

2026-10-25: MCP compatibility candidate `28c1741ef66f000f68ccb286ac99f8165828dded`
was frozen from base `c5683fd28a40bf92cf32ae9b790897a9a34ce5f4` with
only the approved source, tests, guide and planning records. A fresh-context,
read-only reviewer returned **VERIFIED** after reproducing the 1,640-test gate,
focused Ruff and mypy, board and documentation checks. See
[VAL-CMD-MCP-001](validation/VAL-CMD-MCP-001-report.md). The two pre-existing
Friday Chat config edits remain outside the candidate. This closes the MCP
exception's validation gate only; the command initiative remains started in
P0/P1 planning and awaits its own contract and construction directive.

2026-10-25: A live Friday report showed only Zapier's `send_feedback` tool and
no OpenAI Docs tools. Authenticated, read-only reproduction through the
configured MCP runtime discovered five Docs and 17 Zapier definitions. The
default shared 4,000 schema budget prepared all five Docs and one Zapier tool;
registration then rejected all five Docs for their Draft-07 declaration. A
40,000-budget in-memory probe prepared all 22, registered 14 Zapier tools and
identified three further Zapier definitions outside the schema subset. See
[FIND-CMD-MCP-002](validation/FIND-CMD-MCP-002-registration-gap.md) and the
[proposed bounded Draft-07 remediation](remediation/REM-CMD-MCP-002-2025-draft7-registration.md).
No product source or user config changed in this review.

2026-10-25: The maintainer approved the exact
[Draft-07 registration remediation directive](remediation/REM-CMD-MCP-002-2025-draft7-registration.md).
The user's Chat YAML now sets the shared MCP schema budget to 40,000; it
remains outside this work unit. The approved fix is limited to 2025 Draft-07
runtime registration and its publication regression.

2026-10-25: The bounded runtime registration fix admits the exact Draft-07
root declaration only for HTTP peers configured with `2025-11-25`, then
applies the existing inline subset and strips the root dialect annotation.
The 122-test focused pre-edit baseline passed. The final MCP client, runtime
and Chat regression selection passed **2,003 tests**; focused Ruff and source
mypy passed. Board validation and documentation lifecycle passed (36 tasks and
661 Markdown files), as did `git diff --check`. An optional Ruff format check
still finds only pre-existing formatting in `test_mcp_registration.py`; the
new hunks and other changed Python files are formatted. A read-only live
OpenAI Docs probe connected, discovered five, prepared five and registered
five tools with no tool calls. With both configured servers, a discovery-only
probe connected to both, discovered 22, prepared 22 and registered 19 (five
Docs plus 14 Zapier); the same three Zapier definitions remain rejected for
unsupported schema keywords. The user's Chat YAML and models config remain
outside this candidate. Freeze the candidate and obtain independent review.

2026-10-25: Candidate `ddd73e0ac3e0e446113a25b68643f9a71afad2c3`
was frozen from `c7c29b9c04e8aeadd69ffc7067cfe48bec3ae4db` with only
the approved seven-file remediation diff. A fresh-context, read-only reviewer
returned **VERIFIED** after independently reproducing 2,003 tests, focused
Ruff and mypy, board and documentation checks, and an anonymous live
five-tool OpenAI Docs registration probe. See
[VAL-CMD-MCP-002](validation/VAL-CMD-MCP-002-report.md). The working Chat
YAML now sets the schema budget to 50,000, outside the candidate. The command
initiative remains started; this verdict does not grant maintainer acceptance.

`execution_phase: planning`; `validation_state: not_ready`.

2026-10-25: The maintainer accepted the MCP schema policy decisions, including
bounded productive local recursion after a read-only Zapier schema-shape probe,
and requested code generation after the document revision. The
[proposed server-neutral schema directive](directives/CD-CMD-MCP-003-server-neutral-schema.md)
now specifies source boundaries, provider-export and local-validation gates,
diagnostics, budget accounting and tests. The exact directive has not yet been
approved; product source remains unchanged. The separate tool-turn continuity
proposal remains a later construction unit.

2026-10-25: Chuck Russell approved the exact
[server-neutral schema construction directive](directives/CD-CMD-MCP-003-server-neutral-schema.md)
and directed code generation. Implementation may proceed within that bounded
unit. The two pre-existing Chat example config edits remain outside the work.

2026-10-25: CD-CMD-MCP-003 implementation now admits bounded local `$ref`,
`$defs` and `propertyNames` schemas, validates canonical arguments in a
deadline-bound isolated worker before RPC, defers shared schema charging until
registration, and exposes safe startup/inspection counts and reasons. The
[engineering matrix](mcp-schema-engineering-matrix.md) was recorded before
source edits. The final selected MCP client, runtime and Chat regression suite
passed **1,844 tests**; focused Ruff, mypy, format, board and documentation
checks passed. A read-only Zapier initialize/list/registration probe discovered and
registered **17 of 17** tools, including the three previously rejected action
tools, without invoking tools or a paid model. The configured model provider's
ability to carry recursive schema constraints is still unverified, so these
tools remain `provider_export` withheld from model turns. This is a safe
partial outcome under the directive, not end-to-end Zapier action acceptance.

Next MCP gate: freeze this bounded candidate and obtain fresh-context,
read-only validation. Provider compatibility needs a separate, explicitly
permitted model-path proof before the recursive tools can be offered. The
command refactor's separate P0/P1 next step remains characterization of Chat
and `friday-framework-cli`, followed by the shared command contract and its
first construction directive.

2026-10-25: Candidate `3a99de8f971807ade560f8f03d9a0b2ba3a0bf25` was
frozen from `936fb835ad0685c59ea93d8979f63a0618a99982`. Fresh-context,
read-only validation returned **CHANGES_REQUESTED**: the full argument tree
was serialized before the node/depth caps and before the worker deadline.
The bounded remediation now preflights exact JSON types, container size,
node/depth and estimated encoded size before serialization, and starts the
deadline before preflight/worker startup. New tests prove large structures
reject before serialization, size/depth/node failures make no RPC, and a zero
deadline fails safely. The refreshed selected suite passed **1,847 tests**.
The candidate must be refrozen and independently reviewed again; the first
review is not a `VERIFIED` result.

2026-10-25: Refrozen candidate `1473b933c82667cba345a78254eb055df4544ffa`
received a second fresh-context, read-only **CHANGES_REQUESTED** verdict. The
reviewer reproduced a catalog-generation race: a definition discovered in one
generation could be validated locally while its wrapper called the same tool
name in a later generation. The runtime now carries the exact discovery
generation into registration, rejects a stale generation before publishing a
wrapper, and binds the wrapper to the discovered generation for later calls.
A synthetic refresh-before/after-registration test asserts zero tool calls on
both stale paths. The broader MCP client, runtime and Chat selection passed
**2,037 tests**; focused Ruff lint/format and mypy passed, as did board
validation (36 tasks), documentation lifecycle (666 Markdown files) and
`git diff --check`. This remediation requires a new frozen candidate and
fresh-context review; neither earlier candidate is `VERIFIED`.

2026-10-25: Candidate `c0d5518aa132b5e416d9806e65132476f34840ea`
received a third fresh-context, read-only **CHANGES_REQUESTED** verdict. The
reviewer verified the earlier two remediations but reproduced one stale RPC
when a catalog refresh occurs after the initial call-generation check and
before transport dispatch. See
[VAL-CMD-MCP-003](validation/VAL-CMD-MCP-003-interim-review.md). The necessary
client-source edit is outside the approved directive's source boundary;
[Amendment 001](directives/AMEND-CMD-MCP-003-001-send-boundary.md) is proposed
for maintainer review. The other finding, one new Ruff formatting difference
in `friday_chat/tools/mcp.py`, was corrected mechanically within the existing
boundary. No existing MCP client source was edited under the proposed
amendment. Work-unit validation remains pending.

2026-10-25: Chuck Russell approved the exact
[send-boundary amendment](directives/AMEND-CMD-MCP-003-001-send-boundary.md).
The additional `friday-mcp` client-source boundary is authorized only for the
two generation guards and deterministic regressions described there.
Work-unit validation remains pending.

2026-10-25: A separate remediator added the approved generation guard at the
stdio `transport.send` and HTTP pool-dispatch seams. The guard reads the
call-local generation and current catalog immediately before dispatch;
generation-free raw calls remain unchanged. Deterministic stdio, 2025 HTTP
and 2026 HTTP fixtures now invalidate the catalog after initial call admission
but before dispatch, assert `catalog_unavailable`, and observe **zero** tool
requests. The old HTTP test expecting a pre-dispatch stale call was corrected;
existing issued-call output-schema/header tests still pass. The full selected
MCP client, runtime and Chat regression command passed **2,040 tests**:

```sh
uv run pytest -q packages/friday-mcp/tests_mcp/client packages/friday-runtime/tests_runtime/test_mcp_registration.py packages/friday-runtime/tests_runtime/test_mcp_runtime_config.py packages/friday-runtime/tests_runtime/test_mcp_http_integration.py packages/friday-runtime/tests_runtime/test_mcp_loading.py packages/friday-chat/tests_chat/test_mcp_chat_bridge.py packages/friday-chat/tests_chat/test_mcp_http_integration.py packages/friday-chat/tests_chat/test_mcp_turn_budget.py packages/friday-chat/tests_chat/test_mcp_execution_security.py packages/friday-chat/tests_chat/test_mcp_execution_transcript.py packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/test_mcp_memory.py packages/friday-chat/tests_chat/test_tool_selection_budget.py
```

Focused Ruff lint and format checks passed for the amended client files,
refresh test and corrected Chat line; focused mypy passed for `base.py` and
`http.py`. Board validation passed (36 tasks), documentation lifecycle passed
(668 Markdown files), and `git diff --check` passed. Freeze the bounded
candidate and obtain a new fresh-context, read-only aggregate review.

```sh
uv run ruff check packages/friday-mcp/src/friday_mcp/client/base.py packages/friday-mcp/src/friday_mcp/client/http.py packages/friday-mcp/tests_mcp/client/test_result_refresh.py packages/friday-chat/src/friday_chat/tools/mcp.py
uv run ruff format --check packages/friday-mcp/src/friday_mcp/client/base.py packages/friday-mcp/src/friday_mcp/client/http.py packages/friday-mcp/tests_mcp/client/test_result_refresh.py packages/friday-chat/src/friday_chat/tools/mcp.py
uv run mypy packages/friday-mcp/src/friday_mcp/client/base.py packages/friday-mcp/src/friday_mcp/client/http.py
uv run python scripts/friday-dev-board.py validate
uv run python scripts/check-documentation-lifecycle.py
git diff --check
```

2026-10-25: Frozen candidate `e898e211d2c666aef3190682cd8cfb4556e3c934`
was independently **VERIFIED** against CD-CMD-MCP-003 and its approved
send-boundary amendment. The reviewer reproduced 2,040 selected tests,
focused Ruff lint/format and mypy, board validation (36 tasks), documentation
lifecycle (668 Markdown files), and `git diff --check`. See
[VAL-CMD-MCP-003](validation/VAL-CMD-MCP-003-report.md). The review used
local tests only. Provider model-path export for recursive tools remains
unproven, so those tools are still withheld from model turns. Maintainer
acceptance and the wider command-refactor phases remain separate.

2026-11-04: Chuck Russell resolved O-01 through O-05 individually in the
planning discussion. All nine selected names are removed completely without
legacy compatibility; `/tools` stays. Shared UI-neutral `friday-commands`
ownership is confirmed. Preserve separate generic CLI behavior, reusing
primitives only with demonstrated compatibility. Preserve retained-command
quirks; handle fixes through separate bounded decisions and resolve security
or contract violations before affected migration. Reconciled the decision
register, three canonical intent sources and derived plans. The 50/3 source
snapshot is unchanged; the planned target is 41/3. No source/test changes,
construction authority, phase completion, acceptance or TUI resumption is
implied. Exact contract, P0 evidence and first directive remain next gates.

2026-11-04: Began the bounded P0 characterization checkpoint. Captured the
[50-case source ledger](validation/par-coverage-ledger.md), reproducible source
inspection and stateless contract probes, and [baseline receipts](validation/p0-baseline.md).
Live metadata matches the frozen 50-name/three-alias snapshot with no drift.
Generic CLI: 155 passed. Chat (explicit live-provider lane excluded):
823 passed, three failed; baseline is red. The combined suite invocation first
failed collection due to duplicate test module basenames, so owning suites were
run separately. Pre-existing dirty configuration/model examples and backlog
were preserved and hashed; no clean-HEAD or isolated-wheel baseline is claimed.
Observed parser differences and the generic CLI's missing entry-point `app`
need explicit contract treatment. Case-level fixture/assertion coverage,
transitive effects, failure disposition and installed proof remain open.
No product source/test edits, automatic remediation, phase completion or
acceptance occurred. Continue the per-case audit before affected construction.

2026-11-04: Continued P0 without product source/test changes.
[Controlled failure isolation](validation/p0-failure-disposition.md) uses committed
example blobs in temporary files and a temporary collection plugin; original
dirty examples remain untouched. The three failing nodes pass with xterm; the
full Chat control passed 826 tests (one existing deprecation warning, explicit
live lane excluded). Dumb TERM reproduces both clear-byte failures after the
committed config removes the native-vs-MCP adapter mismatch. Captured all 50
default invocations on fresh no-runtime contexts with zero unhandled exceptions
and audited selected existing behavior assertions. Exact node references are
validated against source. Production-adapter/complete per-command effect mapping
and isolated-wheel proof remain open; no P0/P1 completion or construction grant.

2026-11-04: Audited production-adapter, persisted-transcript, memory-diagnostic
and maintenance assertions and source effect ordering. The 54 passing cases
in those four modules have unchanged test hashes against the initial receipt.
[Audit](validation/production-effects-audit.md) distinguishes observed assertions
from unprobed clear/reset late-failure behavior. Drafted the
[foundation API](shared-command-api.md), with typed data/outcome invariants,
Chat-compatible parsing and separate generic CLI preservation; family port
schemas remain pending. Prepared [CMD-FND-001](directives/CD-CMD-FND-001-neutral-foundation.md)
as a draft exact boundary for neutral types/registry only, no default handlers
or client wiring. Construction remains unauthorized pending required review,
applicable P0/P1 disposition and maintainer approval. No product code changed.

2026-11-04: Under the maintainer's instruction to proceed until an artifact
requires approval, froze review candidate 0124d14bb8e91091d35eb73c09f6640e6f558289
and dispatched a fresh-context read-only architecture reviewer. The reviewer
returned VERIFIED for AP-01–AP-06 design approval readiness; no mandatory findings,
one optional multi-slash fixture clarification. Stored the returned report as
[VAL-CMD-ARCH-001](validation/VAL-CMD-ARCH-001-report.md); reviewer verified all
19 authority pins, 84 source/test hashes, unchanged HEAD and dirty inputs, board
and documentation checks. The controller prepared [CMD-DESIGN-001](approval/foundation-design.md)
for limited design/verification approval. Reviewed API/directive bytes and
manifest authorities remain unchanged. Stop at the maintainer design decision;
no approval, P0/P1 closure, implementation authority or external delivery inferred.

2026-11-05: Chuck Russell authorized resolving the three council findings.
Applied bounded documentation remediation under REM-CMD-DESIGN-001: explicit
runtime validation and exception classes, rebuilt canonical-spec storage with
single-pass normalization, negative parser/constructor fixtures and active
nine-retirement wording. Historical scoring rows, baseline snapshots, old reports
and manifests remain unchanged. Updated the approval artifact to fresh-review
pending; the correction authorization is not design/construction approval.
No product source/test/config/metadata changes or automatic council run.
Validation for the corrected packet: board validation passed (36 tasks),
documentation lifecycle passed (685 Markdown files), whitespace checks passed,
and all 84 inventoried source/test hashes plus three pre-existing dirty input
hashes remained unchanged. Frozen parser observations confirm //HELP -> help,
///HELP -> /help, and N(' /HELP ') -> /help; the implementation does not yet exist,
so no new constructor/registry tests are claimed.

2026-11-05: Round 2 completed on c9c15922: GPT-6.1 Sol CHANGES_REQUESTED 8.8/10;
GPT-6 Sol VERIFIED 9/10; GPT-5.6 Sol VERIFIED 9.5/10. All substantive constructor/
canonicalization findings resolved. One residual current-six-name instruction
in command-pruning-review.md remained. Under the existing authorization to
resolve SOL3-ARCH-003, corrected that wording and historical section labels after
all reviews completed. API/directive/approval bytes unchanged; no new delegation,
product code, construction or design approval. Prior verdicts remain historical.

2026-11-05: Maintainer clarified the TUI checkout is the warehouse for the whole
effort, with command refactoring first, and authorized document-only reconciliation.
Imported the complete command packet and exact source snapshot; updated current
location authority/board/navigation to feature/friday-tui. Historical evidence
and branch decisions remain provenance, not local verification. Existing TUI
drafts and source-checkout dirty edits are preserved. No product source merge,
phase closure, design approval or construction grant. See reconciliation/README.md.

2026-11-06: Resumed command-first planning in Agent Framework under the
maintainer's continuation request. Corrected active directive/evidence indexes
that still named the old TUI working home. Wrote a separate
[local continuation receipt](validation/local-2026-11-06/README.md): all 84
inventoried source/test hashes match; generic CLI passed 155 tests; controlled
Chat passed 826 tests with one existing warning, committed examples and xterm.
Historical evidence and unrelated dirty work are preserved. This is a
documentation-only continuation; `execution_phase: planning` and
`validation_state: not_ready` remain. Fresh scoped design-readiness review and
the maintainer's design/directive decisions remain gates before construction.

2026-11-06: Chuck Russell directly approved CMD-DESIGN-001 and instructed a pause
before Step 3 for review. Recorded the exact limited foundation input hash in
[the approval record](approval/foundation-design.md), aligned authority/board
and the packet index, and reconciled the [next-phase](next-phase.md) and
[tactical](tactical-plan.md) checklists to distinguish existing partial outputs
from open obligations. Step 3 is the approval-sequence prerequisite/readiness
work, not tactical task 3 or phase P3. No fresh independent design verdict is
claimed or requirement waived. CD-CMD-FND-001 remains draft/unapproved;
P0/P1 remain incomplete. No prerequisite engineering, source inspection/probe,
new baseline run, contract drafting or product change was started. Pause here
until explicit maintainer resumption. Execution remains planning and validation
state not_ready. This documentation-only administrative continuation was
explicitly authorized by the maintainer; it changes no runtime behavior.

2026-11-06: Chuck Russell explicitly resumed Step 3 and requested Claude Opus,
OpenAI Sol and Google Gemini evaluation of the readiness review. Resumption
revokes the prior pause for readiness preparation only. Wrote the single
[readiness summary](readiness-review.md) and supporting step3 evidence: 17
existing wheels built offline; the default Chat/CLI environment installed and
passed dependency checks but Chat import failed on missing friday_finance.
The finance+sandbox diagnostic profile passed stateless isolated registry and
Chat help probes, with unchanged 50/3 metadata; the generic friday app remains
absent. The full-cohort offline install hit an optimization dependency-cache
limit. No repair, healthy-default-install or complete PAR/P0/P1 claim is made.
Assigned all 50 cases and three aliases to proposed units, recorded service
ownership constraints, eight scenario obligations and environment limits, and
prepared a source-backed separate-CLI reuse assessment. Updated only the draft
foundation directive for an explicit proposed RD-01/RD-02 readiness amendment
and package-under-test overlay command; the approved API bytes are unchanged.
Those dispositions and Step 4 construction approval remain ungranted.
This is authorized planning/evidence work, including read-only source inspection,
disposable local builds/installs and a capture script; it changes no product
source, tests, configuration or runtime behavior. Freeze this candidate for one
read-only three-provider council pass; no automatic remediation loop or product
construction follows. Execution phase planning; validation state pending.

2026-11-06: The requested single readiness council pass completed against
candidate `95fdeadc0a0e4b9720cdb553e5b26756a438ab70`, base `bbbd90e0`.
Claude Opus 5.5, GPT-6.1 Sol and Gemini 4 Argon High each returned
CHANGES_REQUESTED. Saved the original reports and
[consolidated result](validation/step3/council-round1.md), with five open
findings: package-cohort integration scope/checks, default-install evidence
and probe provenance, ingest admission ordering, lock/registry procedure,
and the SC-08 installed-entry-point boundary. The earlier Step 3 paragraph's
Chat import attribution and sandbox implication are disputed; use the council
result before relying on the original readiness assessment. No correction to
the reviewed directive, unit map or raw evidence was performed. API consistency
is supported, but overall readiness and Step 4 remain unapproved. Recorded
review outcome/navigation only, with product and protected dirty bytes
preserved. Next: maintainer disposition of the proposed bounded correction
plan and cohort membership, then corrected frozen evidence/fresh validation
before Step 4. No automatic remediation, further council pass, product code or
external delivery. Execution phase planning; validation state changes_requested.

2026-11-06: Chuck Russell accepted the controller recommendation and authorized
[REM-CMD-STEP3-001](remediation/REM-CMD-STEP3-001.md): bounded planning/evidence
correction followed by fresh independent validation. The draft now selects
existing-cohort integration for the future foundation, an explicit controlled
lock/registry procedure, FILE-001 after MAINT-001 with shared ingest admission,
and source-level CLI proof separate from later installed-entry-point acceptance.
No product metadata/tests/lock/source were changed. A separate remediator
handled the draft package-boundary/verification amendment under repository
policy; the controller handled mechanical map/evidence/process corrections.

Correction to the original Step 3 entry: default Chat/registry/CLI imports and
Chat help pass. Explicit friday_tools import fails on missing friday_finance;
friday_tools.sandbox is a local stdlib module, not optional friday_sandbox.
The original default probe log was from an earlier unpinned script. It remains
unchanged, as do the augmented script/output and original council records.
A fresh 127-distribution default install passes dependency checks and reproduces
the narrow tools/finance and generic CLI missing-app defects with a pinned
[new probe/receipt](validation/step3/default-profile/receipt.json). Versions
match the historical default installation; metadata remains 50 names/three
aliases. The current run blocks one create_connection attempt; augmented and
original-default runs retain their own separate network/provenance limits.
No runtime/store construction, configured tool execution or client repair was
performed by the isolated default-profile probe. Separate root-collection
diagnostics and their weaker containment are disclosed in the correction
receipt; they are not frozen validation evidence. Execution phase planning;
validation state in_review. Freeze corrected
inputs for one fresh read-only independent readiness pass over the five fixes
and all R-01–R-08 criteria. Full feature-branch aggregate implementation review,
Step 4 construction approval, RD-01/RD-02 disposition and delivery remain open.

2026-11-06: Fresh independent validator returned VERIFIED for corrected readiness
candidate `fcea84b879995735308e5be18cfed6cbb82a0b17`, correction base `e0eb3e9c`.
[The report](validation/step3/correction-report.md) records closure of all five
CMD-RDY findings and independent PASS on R-01–R-08/AP-01–AP-06 for the limited
planning packet. All request/authority/deliverable/protected hashes matched at
start/end. The controller independently confirmed the same freeze before
collecting the result. Evidence/status closeout only: preserve the reviewed
API, directive, readiness summary, map, receipts and planning authorization
JSON unchanged; board scope/approval decisions are unchanged. Their pending labels retain frozen pre-review provenance; the
report, board and main handoff record the subsequent outcome. No product
package exists or is claimed implemented/verified. Execution phase planning;
validation state verified for readiness only. Work state remains started/local.
Next: explicit Step 4 decision on exact directive/base, RD-01/RD-02 and
architecture-readiness disposition. No construction, full P0/P1 closure,
feature acceptance, aggregate implementation approval or external delivery.

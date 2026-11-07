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

2026-11-06: Chuck Russell identified the framework CLI's friday launcher
registration as a legacy error and explicitly instructed its removal from TOML.
Recorded [CD-CMD-CLI-001](directives/CD-CMD-CLI-001-retire-legacy-launcher.md)
for that exact metadata deletion and related disposition. Removed only the
project.scripts table from packages/friday-cli/pyproject.toml; no Python source,
API, dependency, lock, finance loading or replacement app changed. Rebuilt CLI
wheel/sdist offline; isolated no-dependencies install advertises no console
script and creates no friday executable. Historical probes/reviews still
describe their old wheels. Updated current readiness/draft/SC-08 text so the
retired launcher is not a missing feature to restore. Its retirement does not
close the separate tools/finance defect. Prior fcea84b8 readiness remains
historical; freeze this metadata/readiness delta for fresh independent review.
Execution phase validation; validation state in_review. Foundation Step 4,
RD-01/RD-02, implementation acceptance and external delivery remain unapproved.

2026-11-06: Fresh independent review VERIFIED CD-CMD-CLI-001 candidate
06285ae446f609f0546866b951dff611cbb447bf: exact launcher metadata deletion,
no replacement, 158 guarded CLI/cohort tests and package/artifact/lock checks.
[Result](validation/legacy-cli-removal/report.md) is preserved for that candidate.
The maintainer then requested finance mandatory in tools metadata. Recorded
[CD-CMD-DEP-001](directives/CD-CMD-DEP-001-required-finance.md) for a separate
remediator to add only the required dependency, preserve the finance extra for
compatibility and retain every resolved version. Finance/provider Python code
and foundation API/implementation stay unchanged. Full offline lock generation
hit the existing litellm==1.100.1 cache gap. Controller disposition permits only
the two exact already-authorized lock edge/metadata additions, semantic equality
proof, offline consistency check and clean default wheel resolution; it is not
claimed as successful full regeneration. No network or upgrade is authorized.
Execution phase validation; validation state in_review for this new unit.
Foundation Step 4 and delivery remain unapproved.

2026-11-06: Independent CD-CMD-DEP-001 review VERIFIED d003c4db31cc9b1e3d143fd8c0d8b930db50ab30;
all DEP criteria pass, 12 focused tests and 129-distribution default replay,
84 source/test hashes and all 16,876 protected hashes preserved. Recorded
[report](validation/required-finance/report.md); full offline regeneration
remains accurately disclosed as cache-limited, with exact lock delta validated.
Chuck Russell then explicitly approved RD-01 and CD-CMD-FND-001. Recorded
[foundation approval](approval/foundation-readiness.md), exact directive/API
hashes and reviewed execution source base d003c4db. Only administrative evidence/
authorization/status records follow that base before construction; verify product
and approved-input equality and record actual builder starting HEAD. Execute
CMD-FND-001 only, with fresh independent implementation validation required.
No later migration, removal, client wiring or delivery authority is inferred.
Execution phase implementation; validation state not_ready.

2026-11-06: CMD-FND-001 builder implementation/checks complete under exact
approved directive hash cf61cab1bc18af071b4b2b9a98f335cf1685592ee647d3c80f60493a80598806
and unchanged API hash e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74.
Approved source baseline d003c4db; administrative builder start 1b4756b7,
with product/input equality verified before editing. Created only the neutral
stdlib models/registry and exact new-package/cohort/root/artifact integration.
Controlled registry resolution adds only new member and root all references;
old resolutions unchanged. Tests: 145 new/cohort, 19 selected Chat and 155 CLI;
focused static checks, 18-project metadata, current wheel/sdist and isolated
no-deps smoke pass. Malformed artifacts missing typing, adding a requirement
or entry point are refused. Guarded current Chat metadata remains 50/3 with
zero JSON-value drift; all 84 inventoried source/test hashes remain unchanged.
Broad Ruff reports 534 findings in 13 unchanged files, root pytest stops at
existing CLI/Chat test_display collision, and docs retain exactly four TUI
broken links. No baseline is presented as a green broad gate. Protected inputs
remain unchanged. [Unit report](validation/CMD-FND-001-report.md) binds actual
commands, tool/environment versions, artifact hashes, limits and raw receipts.
Freeze this candidate for fresh read-only implementation validation before
acceptance; no handlers/client wiring/removals or later unit authorized.
Execution phase validation; validation state in_review.

2026-11-06: Fresh-context read-only validator
`/root/foundation_implementation_validation` independently VERIFIED frozen
CMD-FND-001 candidate `b4fc199eeef3c63a5cf9a8b960cf61c0116170ad`, implementation
base `1b4756b7` and approved source base `d003c4db`. All API-01–API-06 and
FND-01–FND-04 criteria pass with no mandatory findings. Independent checks
reproduced 145 foundation/cohort, 19 selected Chat and 155 CLI tests, focused
typing/lint/format, 18-project metadata, exact lock equality, fresh offline
wheel/sdist/install, three artifact refusals and 24 extra adversarial assertions.
All request, authority, deliverable, external and 16,876 protected hashes match
at start/end; 84 inventory files and current 50/3 metadata remain unchanged.
The controller repeated the final freeze check before recording the result.
[Independent report](validation/VAL-CMD-FND-001-report.md) and
[durable machine receipts](validation/CMD-FND-001-evidence.json) preserve the
full evidence and limits. Root Ruff's 534 findings/13 unchanged files, the
existing root pytest collection collision and four unrelated TUI links remain
unsuccessful broad baselines, with no implicit waiver. Full Chat/runtime/live/
platform acceptance remains excluded. Only evidence/status closeout follows:
reviewed code/tests/root metadata/lock, approved API/directive and builder report
remain frozen. Initiative stays started/local because later command work is
incomplete; foundation unit is ready for maintainer acceptance. No later
directive, wiring/migration/removal, aggregate approval or delivery is inferred.
Execution phase closeout; validation state verified for CMD-FND-001 only.

2026-11-06: Chuck Russell accepted the independently VERIFIED CMD-FND-001
foundation by direct instruction “approved, proceed what's next steps?”
Acceptance applies to candidate b4fc199eeef3c63a5cf9a8b960cf61c0116170ad and its
foundation-only validation, not the entire command refactor or later units.
Recorded the acceptance and prepared
[CD-CMD-RET-001](directives/CD-CMD-RET-001-nine-command-retirement.md) for the
next separate decision, with proposed product source base
08b1900defda3150f30027bec30998360515b72d and directive SHA-256
5be2c7af2384a1bc15a3f385dbca16807ec29d504e2c08e184f23cac4d8c1a66.
The draft binds nine assigned PAR cases, ordinary unknown/no-effect treatment,
41/3 retained metadata, orphan-state/metric decisions, exact affected paths,
underlying runtime/tool preservation, controlled test/installed evidence and
fresh independent review. Its RET-GATE-01–03 dispositions are requested, not
inferred from foundation approval: RD-01 does not authorize retirement before
full family/P1 closure. No product code, tests, lock, dependency or approved
API/directive changed. Preserve historical review/authority labels as frozen
provenance; the main checkpoint and board own the current handoff.
Initiative remains started/local. Execution phase planning; validation state
not_ready for RET-001; foundation result remains VERIFIED and accepted.

2026-11-06: Chuck Russell agreed to the proposed checkpoint delivery sequence
and directed “i agree with your recommendations. proceed”. This explicitly
supplies checkpoint commit/push/PR/merge authority, followed by confirmed old-
branch deletion and a fresh retirement branch. It does not approve RET-001 or
TUI source. [Checkpoint scope](validation/checkpoint/README.md) includes all
existing branch work and the earlier authorized planning transfers. Exclude
and preserve the two unrelated Chat example configurations. Repaired ten
historical source links in four imported TUI reports, with old/new hashes and
exact verified source commits in the relocation receipt; no source copied.
Board validation passes 36 tasks and documentation lifecycle passes 851 files
before adding this checkpoint record. Aggregate inspection must cover all
branch changes against master, including MCP fixes and historical archives,
not just the accepted foundation. Freeze a stable candidate and obtain fresh
read-only aggregate VERIFIED before delivery. Execution phase validation;
validation state pending. Initiative stays started/local until actual delivery.

2026-11-06: Fresh aggregate validator returned CHANGES_REQUESTED for
candidate dea496075de55060ad477820e04b71c78239cca0 against master c3426986.
[Report](validation/checkpoint/aggregate-report.md) records two mandatory findings:
AGG-001, inherited post-adoption archival board script/test changes lack exact
construction authority; AGG-002, five formatting regressions. All 3,116 tests
pass, including controlled full Chat 826, and focused lint/type, artifacts,
default 129-distribution installation, archive/transfer integrity and input
preservation pass. Broad baseline debt and optional-cohort cache limits remain
separate unsuccessful gates. All reviewed inputs and two excluded config files
were preserved throughout. Recorded independent evidence and prepared exact
CD-CMD-CHK-001 (SHA cf8ed0b8c088d7aba6067f518a3f6b46ccd56b672d454d6bff7461f794f1469a)
for a current explicit historical-authority exception plus five-file mechanical
formatting; no code changed and no retrospective approval inferred. Maintainer
publication/merge authority remains valid subject to these gates. Execution
phase validation; validation state changes_requested. No push/PR/merge yet.

2026-11-06: Changed only the review patch presentation to zero context so its
blank context markers do not trigger whitespace checks when stored as a file.
The exact base/candidate/two-file semantic delta is unchanged. Patch SHA-256 is
now 1001e73202db0670f9e1f267876dfea3fc68650b91780bbe2f7bc46af0a3fe22; proposed CD-CMD-CHK-001 SHA-256 is
d0cc21779452767862b52ca025db1fa11417e8481418d119aa8a0a875ef2823d. This supersedes the earlier proposal digest for
approval purposes; no product source or authority exception has been approved.

2026-11-06: Chuck Russell explicitly responded “Approve CD-CMD-CHK-001”
to the presented historical-exception/five-file-formatting/fresh-review scope.
Recorded [exact approval](approval/checkpoint-reconciliation.md) at directive
SHA d0cc21779452767862b52ca025db1fa11417e8481418d119aa8a0a875ef2823d, source base dea496075de55060ad477820e04b71c78239cca0,
with administrative starting HEAD c8192fb34d302674454de799a0f0555aae6f2ef5. Verified approved source equality
and both protected configurations before correction. This is a current,
one-time archival-construction exception; original chronology is preserved.
Execute only five-file formatter output with identical ASTs, freeze a new
candidate and obtain fresh aggregate verification before already-authorized
delivery. Execution phase remediation; validation state not_ready.

2026-11-06: Approved CD-CMD-CHK-001 correction complete. Recorded current
explicit AGG-001 historical exception without backdating or changing board-test
behavior. Applied only five named Ruff-format outputs for AGG-002; all five
AST fingerprints match their pre-correction values. 325 focused tests, 34-file
Ruff, five-file format and 18-source mypy pass. Board/docs/lock/whitespace pass;
configs and all outside-scope product bytes preserved. [Correction report](validation/checkpoint/correction-report.md)
and machine receipts record actual argv/results/AST hashes. Freeze a stable
candidate for fresh independent full aggregate review, including explicit
current-input equivalence for prior receipts. Prior CHANGES_REQUESTED remains
historical until a new verdict. Execution phase validation; validation state
in_review. Existing delivery authority remains conditional on verified readiness.

2026-11-06: Fresh aggregate validator VERIFIED 51334a5b3f92ca7922976f1c0f3aa15443ae61e6
against master c3426986, independently closing AGG-001/002 under the exact current
exception/formatting approval. All AGG-01–08 pass; 3,116 tests, current fresh
artifacts/default129 installation, source/installed equivalence, archive/transfer
integrity and protected inputs pass. Broad baseline and optional-cohort limits
remain accurately disclosed. [Fresh report](validation/checkpoint/verified-report.md)
and [durable receipts](validation/checkpoint/verified-evidence.json) retain the
full evidence. Controller independently verified all input/manifest/protected
hashes before evidence-only closeout. No code/tests/API/metadata/lock/directive
or approved scope change follows. Proceed with already-authorized checkpoint
push/PR/actual-requirements check/merge/new branch; no new development approved.
Execution phase closeout; validation state verified. Initiative remains started.

2026-11-06: Authorized checkpoint delivery completed. Published head
7b344b010e347a74e730d2aff9f4670f24d6e1c3; [PR #13](https://github.com/CIChuck/agent-framework/pull/13)
merged into master at 6f291ca5755a616d9185c86dff104b660a1fba8c. Immediately before merge, refetched base
c3426986 was unchanged, actual PR base/head matched, mergeability clean, no
check runs/statuses/reviews/threads/rulesets or branch protection applied. No CI
success was invented. Merge tree equals published checkpoint tree; reviewed
51334a5b differs only by evidence/status closeout. Confirmed history and protected
working config hashes, fast-forwarded local master, created feature/command-retirement, then
normally deleted merged old branch locally/remotely. [Delivery receipt](validation/checkpoint/delivery.json)
records exact remote identities and gates. Refreshed current board/authority/
headers and draft RET source identity only: source base 6f291ca5755a616d9185c86dff104b660a1fba8c, directive SHA
a8646a4bbd2c0275bca74d5430a9169b053f45490c34621aa144f224b0f79e28. Earlier approvals/requests/reports remain unchanged. Both excluded
working examples remain byte-identical; no runtime/test/dependency/lock change.
This documentation-only branch handoff is within explicit delivery authorization;
its lightweight exemption is date 2026-11-06, owner Chuck Russell, scope current
branch/source references and delivery records, with board/docs/hash/whitespace
validation. Initiative remains started; remaining unit local, checkpoint merged.
Execution phase planning; validation state not_ready for RET-001. Exact retirement
directive approval is the next gate; no command removal or TUI construction began.

2026-11-06: Chuck Russell directed “Strengthened the document i approve your
recommendations.” Applied the five proposed drift controls in CD-CMD-RET-001:
exact removal/retention symbols and four orphan fields with caller evidence;
pinned 50-to-41 metadata/alias and parser/no-effect oracles; fixed assertion
preservation map; pinned reviewed harness plus DNS/bind containment and exact
check recipes; candidate-Git-only artifact inputs, frozen129 profile and
installed equality; current docs baseline and explicit disposable loopback
permissions. Updated draft SHA-256 b760a9a8f8b94e120e5d26914d9bdf45f037a6a3f7f9552cd3d4054d829da9df; source base remains merged6f291ca5.
Validated shell/embedded-Python/guard syntax, source helper names, oracle/profile/
harness pins and 41/3 set derivation without running the recipes. This is a
maintainer-authorized documentation-only lightweight revision: owner Chuck
Russell, date2026-11-06, scope directive/handoff/current hash/status only, no
runtime/test/dependency/lock change. Validate board/docs/whitespace and protected
config/source equality before handoff. Exact RET construction approval remains
not_granted; no code generated or retirement begun. Execution phase planning;
validation state not_ready for RET-001.

2026-11-07T02:06:07+00:00: Chuck Russell approved exact strengthened CD-CMD-RET-001 by
“i approve the document proceed.” [Approval](approval/command-retirement.md)
binds hash b760a9a8f8b94e120e5d26914d9bdf45f037a6a3f7f9552cd3d4054d829da9df and source base 6f291ca5755a616d9185c86dff104b660a1fba8c.
Verified source equality and preserved dirty hashes/assertion inventory before
code edits. Execute this unit only, including RET-GATE-01–03; capture current
before results and immutable evidence. No future construction or delivery.
Execution phase implementation; validation state not_ready.

RET-001 implementation: before suites826/145/155 pass, approved guard self-tests
and exact original metadata-fields/Git-source proof pass. Removed exact allowed
source symbols/catalog entries/four fields; no parser/registry blacklist or
retained-handler change. Updated23 mapped test nodes, kept496 original node ASTs
identical, added216 no-effect cases and exact catalog/field/custom-registry checks;
updated seven allowed guides. Working Chat1038 passes. New schema-projection and
test-fixture errors were corrected/disclosed in unit evidence; no product fix
beyond approved removals. Final frozen after checks and clean Git packaging
remain required. Execution phase implementation; validation state not_ready.

RET-001 builder verification complete:1038 Chat/145 foundation-cohort/155 CLI
pass; focused lint/types, metadata/board/docs/lock and exact negative/metadata
proof pass. Format37->36 with no new file failures; root534 lint and one root
collection collision remain baseline. Clean candidate-Git Chat artifacts and
offline129 installed profile pass41/3,216 no-effect cases,390 installed/Git/wheel
source members, aliases/help/finance and retired launcher absence. All retained
source ASTs and496 original test node ASTs preserved;23 mapped nodes accounted
for. [Report](validation/retirement/README.md) discloses controller harness/
fixture corrections and exact evidence; no product scope drift. Freeze current
candidate for fresh independent validation. Execution phase validation;
validation state in_review. No pilot/delivery/acceptance inferred.

Fresh read-only independent review VERIFIED RET-001 candidate
f896ef536efcc45d569f4231edfc39baab09bbc8, source base6f291ca5. All RET-01–09
criteria pass with no mandatory findings; 1038 Chat/145 foundation-cohort/155 CLI
passes reproduced. Independent source AST,519-function/2260-assertion, exact
41/3 metadata,216 negatives plus80 strict-context probes, clean Git artifacts,
129-profile/default imports and390 wheel/668 sdist source matches pass. All
17069 current-input hashes/authority/request/external/protected pins held. The
controller independently repeated the complete end freeze before closeout.
[Independent report](validation/retirement/verified-report.md) and retained raw
receipts document actual commands/limits. Nine PAR removal rows are VERIFIED;
remaining family/P1/TUI/feature gates stay open. Only evidence/status closeout
follows; no source/tests/metadata/lock/API/directive change. Initiative stays
started/local. RET-001 ready for maintainer acceptance, not self-accepted.
Execution phase closeout; validation state verified. No publication or next-unit
construction authority inferred.

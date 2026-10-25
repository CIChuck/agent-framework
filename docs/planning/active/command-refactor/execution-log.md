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

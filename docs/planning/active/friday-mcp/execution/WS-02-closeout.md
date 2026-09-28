# MCP-WS-02 Work-Unit Closeout

Date: 2026-09-28
Status: Independently verified; awaiting explicit maintainer acceptance
Work unit: Runtime-owned stdio startup, bounded discovery and shutdown only
Candidate: `a257f041d1d68f8aea2f5b9773df1b88acd82379`
Accepted predecessor / full work-unit base: `a64e423cffca6162c43b8cfa193792508cf87fd6`
Validation: Fresh independent REM-004 delta and complete WS-02 aggregate
`VERIFIED`, no findings, in [VAL-007](../validation/VAL-007-report.md)
Acceptance: Not recorded; no maintainer acceptance decision yet
Delivery: Local; no push, merge or release

WS-02 makes runtime startup own an explicit MCP provider/manager, connect
validated enabled stdio peers, discover within configured deadlines,
concurrency and caps, and preserve typed redacted diagnostics. Optional peer
failures are skipped, required failures abort and clean up, and binding
validation follows discovery. Native registration and public runtime startup
signatures remain compatible. Discovery is a bounded explicitly untrusted
handoff, not executable MCP registration or prompt-visible schemas.

VAL-005 found failed-start retry could replace retained owners. Separately
approved REM-003 corrected provider/DI retry ownership. VAL-006 verified that
delta but found a separate noisy-child post-kill pipe/wait hang. Separately
approved REM-004 confines correction to stdio teardown, local regressions and
two reports. It incrementally discards output, bounds process/task cleanup,
preserves the five-second graceful wait, and retains ownership with a static
error if cleanup cannot finish. Fresh VAL-007 independently verified both
correction and the entire current WS-02 unit, including prior owner recovery.

Independent checks: 333 Core/MCP/runtime aggregate tests, 39 focused lifecycle
tests, 32 runtime-loading tests and 46 Chat compatibility tests passed (these
suites overlap; do not add their counts). Broad integration had 44 passing
tests and only the declared 22-versus-23-board-count baseline failure. Ruff
and prescribed Python 3.13 mypy passed (42 files); default mypy reproduced
only the declared installed NumPy syntax baseline. Board/dashboard, docs,
all exact diff checks and frozen-product comparisons passed. Controller also
reran the focused suite: 39 passed. Full command/evidence details are in VAL-007.

Independent production probes additionally confirmed direct/public-kernel
noisy-child forced cleanup, cancellation/public retry, optional/required noisy
partial startup, released processes/pipes/tasks and redaction. Independent
incomplete-cleanup doubles retained owned resources and later publicly
recovered. An intentionally failing scratch assertion confirmed fixture
cleanup even when a regression assertion fails; it was not a product failure.

Limits remain explicit: the eleven-second asynchronous attempt budget assumes
cooperative scheduling, not hard real time. OS reaping failure, descendants
holding pipes or cancellation-resistant I/O can require a later retry after
the obstruction clears. No process-tree control or broader lifecycle redesign
is claimed. Cwd confinement is not an executable sandbox. Evidence uses only
local synthetic peers/doubles, not live MCP/provider/SSE or complete app UAT.

Next gate is explicit maintainer acceptance of this WS-02 work unit. The wider
`friday-mcp` initiative remains `started` and local. WS-03 and later remain
draft/unapproved; executable registry naming/filtering/sanitization is not
implemented by WS-02. Acceptance does not itself authorize those workstreams
or push, merge, release, deployment, credentials or paid/live external effects.

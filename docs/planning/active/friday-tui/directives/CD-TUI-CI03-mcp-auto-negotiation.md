# CD-TUI-CI03: Bounded MCP auto-negotiation recovery

**Status:** Proposed for maintainer review. This document grants no source,
test, workflow or push authority. TUI-CI02 stopped at its approved
framework-source boundary; CI01 and CI02 remain `changes_requested` on Linux.

**Initiative/unit:** `friday-tui` / TUI-CI03, a separate shared-framework
remediation required by the TUI Linux verification gate.

## Evidence and proposed behavior

[Ubuntu run 39181571549](../validation/TUI-CI02-ubuntu-run-39181571549.md)
on `49adbcb50d8e6b238172845fe32ef1ddfe279f4a` passed all Chat, unchanged
`friday-cli` and wheel gates, but Runtime `auto`/modern startup failed in its
full suite and all three focused repetitions. Runtime recorded
`connection_failed` after about 1.7 seconds. All three direct MCP `auto`
connections sent legacy `initialize` to the modern SDK peer and received
unsupported-protocol error `-32022`. The existing source gives `auto`'s modern
`server/discover` probe half of the original connection budget, then falls
back to legacy on probe timeout. The locked SDK's `mcp.client._probe`
implementation documents the case where a timed-out probe succeeds
server-side and a later legacy `initialize` receives `-32022`. A local
delayed modern SDK peer reproduced the same error;
explicit `modern` connected within the three-second budget. The probe-timeout
mechanism is a strong inference, not yet a directly captured Ubuntu event.

**Proposed contract:** Preserve `legacy` and explicit `modern` behavior and
the configured total connection deadline. For `auto`, retain legacy fallback
when a peer ignores or rejects modern discovery. If modern discovery timed
out and the legacy `initialize` reply returns unsupported-protocol code
`-32022`, allow at most one modern discovery retry on the
same owned connection within the *remaining original deadline*. Never replay
`tools/call`, extend the timeout, silently retry ambiguous transport errors,
or leave child processes/tasks unowned. If the original budget is exhausted,
fail within the existing public exception contract and clean up. This is a
negotiation recovery for a read-only handshake, not a change to Friday Chat,
`friday-cli`, or TUI commands.

The exact retry design is subject to CI03-A characterization: capture the
first modern-probe outcome and prove that the subsequent `-32022` follows that
timeout. If that sequence is not confirmed, stop and revise this directive
before source changes. Do not approve a speculative generic retry.

## Testable subunits and proposed exact edit scope

1. **CI03-A, characterize before source edit:** Add a deterministic synthetic
   test for a modern peer whose discovery reply arrives after `auto`'s first
   probe budget but before the total connection deadline. Establish the
   modern-probe timeout, explicit `-32022` on legacy fallback, child cleanup
   and no tool call. Also exercise a legacy peer that ignores modern discovery
   and a genuinely unavailable modern peer. Keep the Linux job red at this
   point. If the observed sequence differs, stop for a revised directive.
2. **CI03-B, bounded source correction:** Implement only the proposed
   one-time modern discovery retry after that exact timeout/version-mismatch
   sequence. Preserve the original deadline, all explicit profiles, legacy
   fallback, no mutation replay, cancellation and owned-child cleanup.
3. **CI03-C, verify integration:** Run focused deterministic and real SDK
   direct MCP tests repeatedly, the full MCP and Runtime suites, full Chat,
   unchanged `friday-cli`, lock and static checks locally. On Ubuntu rerun
   the exact direct `auto` test repeatedly, full Runtime and Chat/CLI suites,
   wheel metadata/isolation checks and installed dependency checks. Require a
   green exact-candidate run and fresh-context independent review. Hands-on
   Linux terminal UAT remains a later TUI release gate.

After approval, exact allowed edits would be:

- `packages/friday-mcp/src/friday_mcp/client/base.py` — only `auto`
  negotiation and deadline handling for the confirmed failure sequence.
- `packages/friday-mcp/tests_mcp/client/test_stdio_interop.py` — focused
  synthetic regression and cleanup coverage.
- `.github/workflows/friday-tui-linux.yml` — add a direct explicit-modern
  control check if needed while retaining all existing gates and red status.
- This TUI packet's directive, authority, index, execution log and validation
  evidence; the TUI board entry and generated dashboard.

No `friday-cli` source/tests, Chat source, Runtime source, TUI package,
metadata, dependency lock, production timeout/default, release, PR or merge
edit is proposed. A needed additional path or changed contract requires a
revised directive and maintainer approval before editing it. Avoid logging
credentials or peer-supplied text; use synthetic fixtures and fixed reason
codes. The maintainer must separately authorize any future branch push.

## Approval and stop gate

The maintainer can approve or revise this exact CI03 scope and behavior.
Approval would authorize only the listed local source/test/workflow work after
the board and authority manifest record it. It would not accept CI01/CI02,
approve a PR or release, or waive Linux terminal UAT. Stop if CI03-A does not
confirm the sequence, if source correction changes the `friday-cli` contract,
or if tests reveal an unrelated transport or SDK problem.

# REM-009 — Correct WS-08 Optional-Server And Selection Guidance

- Date: 2026-09-29
- Status: Bounded documentation correction authorized within the maintainer's "continue with ws-08" and the approved exact WS-08 documentation directive
- Work unit: `MCP-WS-08`
- Branch: `feature/friday-mcp-ws08-docs`
- Reviewed candidate: `f8970313655e6e18b39d14dc1f151b5a7b5aaa33`
- Original base: `d9eb81d`
- Independent finding authority: [VAL-017](../validation/VAL-017-report.md), CHANGES_REQUESTED
- Cycle: first WS-08 remediation

The two findings are bounded, non-destructive corrections of prose/examples
inside the maintainer-approved WS-08 documentation manifest. The maintainer's
WS-08 instruction authorized accurate documentation, and no new product,
configuration schema, package or external-effects scope is introduced. The
reviewed candidate and VAL-017 report/evidence remain immutable historical
inputs. The controller may perform this mechanical wording/example correction;
a **new** fresh-context read-only validator must review the delta and complete
original WS-08 aggregate before any closeout proposal.

## Exact correction paths

- `docs/guides/17-mcp-client.md`
- `docs/guides/10-configuration.md`
- `docs/guides/13-troubleshooting.md`
- `packages/friday-runtime/README.md`

A remediation implementation report and new validation request/report/evidence,
packet/board/dashboard process updates are separate artifacts. Do not change
runtime source, tests, templates, other guides/READMEs, dependencies, lock,
original WS-08 directive, pinned VAL-017 authority/report/evidence or any of
the five unrelated dirty paths.

## VAL-017-F01 — High: Optional server with explicit include

The principal guide config has `required: false` but pins
`include_tools: [mcp_demo_probe]`. If the peer fails, discovery records an
optional connection failure and registration then fails with `missing_include`.
The current guide/config summary incorrectly promises nonfatal startup.

Required correction: state that an explicit missing include is a separate
startup requirement even when its server is optional. Show a selected-mode
configuration that really continues after optional peer failure without a
strict tool-name include, and warn that `include_categories: [mcp]` admits
all valid discovered MCP tools if the peer is available. Align the main guide,
configuration summary, troubleshooting table and Runtime README. Do not alter
the accepted runtime semantics or claim an absent explicitly selected tool is
silently skipped.

Verification: parse the primary and optional guide snippets through Runtime
and Chat models; start and register a good local peer for each intended
selection mode; with a missing command, assert the principal explicit-include
case raises `missing_include` after `connection_failed`, while the category
based optional case completes with no registered MCP tool. Recheck required
failure. Document the result without exposing raw command/exception values.

## VAL-017-F02 — Low: Category selection omitted

The configuration summary says selected mode needs explicit canonical
`include_tools`, but accepted registration also supports
`include_categories: [mcp]`. Qualify this sentence to name both rules and
retain canonical-name guidance for strict `include_tools` entries. This is a
wording correction in `docs/guides/10-configuration.md` only. Verify the
category-only config parses in Runtime and Chat and registers the local probe
tool without a tool-name include.

## Exit and stop conditions

Run the affected local probes, documentation link/lifecycle and board checks,
`git diff --check`, and the focused Runtime/Chat MCP configuration tests.
The prior package/integration and nonzero broad Chat results remain recorded;
repeat broader checks if changed behavior or an unresolved concern warrants
them. Commit a new stable exact-path candidate, mark VAL-017 superseded for
decisions on that new candidate while preserving it historically, then request
a fresh delta plus complete original-aggregate review. Stop if any correction
requires product code, schema, template or outside-manifest changes.

# MCP-WS-08 Work-Unit Closeout Proposal

- Date: 2026-09-29
- Status: Independently VERIFIED and explicitly accepted
- Initiative: `friday-mcp`
- Work unit: `MCP-WS-08`
- Branch: `feature/friday-mcp-ws08-docs`
- Original base: `d9eb81d6e67bafc71346e142c1d1fd0c61ced6df`
- Corrected candidate: `08141407f7a7c3ca37174c8950bf552180df47c8`
- Delivery: Local
- Accepted by: repository maintainer
- Accepted at: 2026-09-29
- Acceptance evidence: explicit "accepted ws-08, continue" after the complete VAL-018 report and independently audited closeout proposal were presented

Fresh `/root/mcp_ws08_val018`, dispatched with `fork_turns: none`, returned
**VERIFIED** with no findings for the exact REM-009 documentation correction
and complete original WS-08 aggregate. The [complete independent report](../validation/VAL-018-report.md)
and [byte-checked evidence](../validation/VAL-018-evidence.yaml) are preserved.
The report is byte-exact from the reviewer's scratch output (SHA256
`153e7f5b43ffc15225f4bf6c2dce1db0dbf9a4d8d5486edc37fbef2d61ad5fce`);
all 14 scratch archive members match their manifest hashes. All 18 authority
hashes, 11 corrected deliverable hashes, exact four-path remediation product
delta, exact 11-path original WS-08 product aggregate and five unrelated local
fingerprints matched at review start and close. No governed repository change
was made by the reviewer.

WS-08 publishes the accepted local stdio MCP configuration in a new client
guide, four updated guides, three package READMEs and matching default-disabled
Friday Chat config examples. REM-009 corrects the important distinction that
an optional server's connection failure can still make startup fail when
`include_tools` pins a missing tool; a category-only selection permits
optional absence and admits every valid discovered MCP tool when available.
The old [VAL-017](../validation/VAL-017-report.md) CHANGES_REQUESTED finding
remains historical for `f897031`; the corrected candidate resolves both
findings without changing runtime source, tests, schema, package metadata or
other product scope.

Independent Runtime, MCP, focused Runtime/Chat and MCP integration suites
passed 195, 65, 92 and 56 tests respectively. The guide snippets, templates,
README Python example, local stdio success/failure cases, CLI, links, board,
documentation lifecycle and diff checks passed. Broad Chat remains **nonzero**:
620 passed, 5 skipped, one PTY timing failure and three localhost bind
PermissionErrors, matching the prior independently recorded baseline class.
The first documentation lifecycle invocation attempted an unavailable nested
network download; its `UV_NO_SYNC=true` rerun passed 375 Markdown files. No
live provider, external network UAT, paid endpoint, credential, merge, push
or release was exercised.

The maintainer explicitly accepted this verified WS-08 candidate and complete
VAL-018 result with "accepted ws-08, continue" on 2026-09-29 after the
independently audited closeout proposal was presented. WS-00 through WS-08
are independently verified and explicitly accepted work units. The wider
initiative remains `started`/`granted`/`normal` with local delivery. The next
gate is a fresh aggregate review of the complete feature-branch diff;
optional WS-09 and any delivery action require separate authority.

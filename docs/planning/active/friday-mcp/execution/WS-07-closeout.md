# MCP-WS-07 Work-Unit Closeout

- Date: 2026-09-29
- Status: Independently VERIFIED and explicitly accepted
- Initiative: `friday-mcp`
- Work unit: `MCP-WS-07`
- Branch: `feature/friday-mcp-ws07-telemetry`
- Base: `c05882e45d78dc83ad48ee17b156aa9efff6fff0`
- Candidate: `2e36613eae6060a99c1255cce04fcb7a27bc7374`
- Delivery: Local
- Accepted by: repository maintainer
- Accepted at: 2026-09-29
- Acceptance evidence: explicit "accepted" after the complete VAL-016 report and closeout proposal were presented

Fresh `/root/mcp_ws07_val016`, dispatched with `fork_turns: none`, performed a
read-only complete WS-07 aggregate review of the frozen 16-path candidate. The
[complete independent report](../validation/VAL-016-report.md) returns
**VERIFIED** with no numbered findings. All 11 pinned authority hashes, all 16
product hashes, the exact aggregate path manifest and five unrelated local
fingerprints matched at review start and close. The reviewer made no governed
repository edits. The original report is copied byte-exact (SHA256
`1aaea6980372e36618641055476874c7ce9a642b44e107484cba3ff06f66f242`);
its scratch checks, probes, logs, wheel artifacts and freeze audits are in
[byte-checked evidence](../validation/VAL-016-evidence.yaml). All 755 selected
archive members match their manifest hashes. The large reproducible frozen-base
extraction is omitted from that archive and can be recreated from the pinned
base commit.

The approved first pass adds closed, redacted MCP telemetry and public
operational diagnostics across Runtime, MCP tool calls and Chat decisions. It
retains both typed collision contenders locally, aggregates catalog-cap skips,
records checked output and budget outcomes, and distinguishes pending from
published ingestion. The reviewer exercised retry, cleanup, cancellation,
large-catalog redaction, collision, native dispatch, budget rejection and
receipt reuse with local peers and scratch storage. The approved new Chat
health-command deferral remains in force; no command, configuration,
dependency, lock, schema, backend or outside-manifest product path changed.

Focused tests passed 294; Telemetry 56, Runtime 195, MCP 65 and four MCP
integration modules 56. Ruff, affected Python-3.13 mypy, offline lock, board,
docs and diff checks passed. All 16 framework wheels built offline, and an
isolated Python process loaded checked Friday modules from extracted wheels.
The broad Chat and top-level integration commands remain nonzero for one PTY
timing failure, three localhost bind permissions, and a stale 22-versus-23
board expectation. The reviewer independently reproduced each class against
byte-checked frozen-base source; these results are disclosed as nonzero,
inherited test/environment debt. The distribution proof is not a clean offline
resolver install or live-provider UAT.

## Acceptance And Remaining Gates

The maintainer explicitly accepted this verified WS-07 candidate and complete
VAL-016 result with "accepted" on 2026-09-29, after the independent report and
closeout proposal were presented. WS-00 through WS-07 are now independently
verified and explicitly accepted work units. This decision applies to candidate
`2e36613eae6060a99c1255cce04fcb7a27bc7374` and its full WS-07 aggregate
review; it grants no WS-08 implementation or external-effects authority.

Next gate: reconcile the draft WS-08 documentation directive against accepted
source, guides and distributed configuration, then request separate bounded
approval. The wider initiative remains `started`/`granted`/`normal` with local
delivery on its named branch. Initiative-level aggregate review and
merge/push/release remain separate decisions.

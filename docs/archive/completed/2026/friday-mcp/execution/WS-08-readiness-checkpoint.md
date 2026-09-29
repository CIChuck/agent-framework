# MCP-WS-08 Readiness And Scope Checkpoint

- Date: 2026-09-29
- Accepted predecessor: WS-07 candidate `2e36613eae6060a99c1255cce04fcb7a27bc7374`, fresh VAL-016 VERIFIED and explicitly accepted
- Branch base: `93d3684` (`Record maintainer acceptance of WS-07`)
- Branch: `feature/friday-mcp-ws08-docs`
- Authority: maintainer's "continue with ws-08" after being told WS-08 is the remaining required documentation workstream
- Phase/state: implementation / not_ready

The old draft directive had directory-wide edit permission and a nonexistent
`docs/planning/queued/friday-mcp/build-plan.md` path. The reconciled
[directive](../directives/ws-08-documentation-guide-closeout.md) narrows the
deliverable to six guide files, three package READMEs, and the two actual
Friday Chat runtime-config example copies. No implementation source, test,
package metadata, other template or historical validation file is in scope.

Current implementation facts to document:

| Boundary | Checked behavior |
| --- | --- |
| `friday_runtime.config.MCPToolProviderConfig` | Canonical `tools.providers.mcp` is default-disabled, mode `selected`; selected mode requires explicit canonical `include_tools`. `config_file` is rejected. |
| `MCPRuntimeServerConfig` and `MCPClientSecurityPolicy` | Integrated runtime accepts local stdio with an explicit command and workspace-confined `cwd`; required and disabled cannot coexist. Programmatic protocol-local SSE/server APIs are separate. |
| `MCPClientLimits` and Chat `ToolBudgetSnapshot` | Discovery caps differ from Chat per-turn schema/count/result reservations and the minimum memory retrieval floor. |
| `MCPIngestionPolicy` and accepted WS-06 receipts | Direct long-term MCP ingestion is disabled by default; explicit server/tool opt-in and sanitization are required. Checked transcript records can exist without memory ingestion. |
| `RuntimeMCPProvider.operational_diagnostics` and WS-07 telemetry | Local typed diagnostics retain lifecycle/registration decisions; optional telemetry exports closed categorical events with opaque identifiers. No Chat health command or telemetry endpoint exists. |
| Current docs/templates | The distributed Chat config examples omit MCP, and the old troubleshooting FAQ shows an unsupported HTTP `MCPClient`/registry example. Correct those claims without broad guide rewrites. |

The guide will use a repo-local synthetic stdio peer for an executable example
and an installed local server path as the production substitution. New snippets
must parse through the actual Runtime and Chat config models. Required-server
failure and local fake-peer behavior will be exercised without a paid or remote
service. All five unrelated local fingerprints remain outside this scope.

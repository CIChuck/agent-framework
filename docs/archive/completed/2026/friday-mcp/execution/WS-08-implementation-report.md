# MCP-WS-08 Implementation Report

- Date: 2026-09-29
- Status: Stable builder candidate; independent review pending
- Branch: `feature/friday-mcp-ws08-docs`
- Base: `d9eb81d`
- Candidate: `f897031`
- Authority: [approved reconciled WS-08 directive](../directives/ws-08-documentation-guide-closeout.md)
- Scope: [exact 11-path product manifest](WS-08-product-manifest.json)

The new [MCP client guide](../../../../../guides/17-mcp-client.md) provides a
checkout-local stdio example and the disabled default, selected-mode naming,
optional/required server behavior, workspace paths, environment interpolation,
discovery and per-turn budgets, output/provenance, default-disabled ingestion,
diagnostics and deferred capabilities. Four existing guides point to or
summarize those behaviors; the troubleshooting FAQ's unsupported HTTP
`MCPClient`/`register_mcp_tools` example was replaced. The three package
READMEs distinguish the lower-level protocol APIs from integrated local-stdio
runtime/Chat use. Both distributed Friday Chat runtime templates now show the
same disabled MCP stanza, leaving other template settings intact.

No runtime implementation source, tests, package metadata, CLI command,
external include, remote integrated transport, backend or memory schema
changed. The five unrelated dirty paths were fingerprinted against the
predecessor freeze and remained unchanged. The doc changes are committed at
the candidate hash above; process artifacts follow separately.

## Builder verification

| Check | Result |
| --- | --- |
| Three guide YAML snippets through `MCPToolProviderConfig`, `FridayChatConfig` and `RuntimeConfig` | Pass; enabled, disabled and env-value shapes round-trip |
| Two distributed Chat templates against the disabled guide stanza | Pass; identical MCP stanza, existing distinct template settings retained |
| Friday Chat `${EXAMPLE_API_KEY}` interpolation and rejected `config_file` | Pass with a synthetic local value and reserved-key error |
| Repo-local stdio peer through `RuntimeMCPProvider` | Pass; `mcp_demo_probe` discovered and registered, owned provider stopped |
| Missing command, optional versus required | Pass; optional startup continued with diagnostics, required startup failed |
| `friday-mcp` README Python example | Pass; runnable fenced code printed `['mcp_demo_probe']` |
| `friday-chat --help` | Pass; `--config` and `--runtime` syntax/real choice confirmed |
| Focused Runtime/Chat config, turn-budget and ingestion tests | 92 passed |
| Runtime package | 195 passed |
| MCP package | 65 passed |
| Four MCP integration modules | 56 passed |
| Chat package | **Nonzero:** 620 passed, 5 skipped, 1 PTY timing failure, 3 localhost bind PermissionErrors; same independently reproduced WS-07 baseline class in [VAL-016](../validation/VAL-016-report.md) |
| Documentation lifecycle/local links | 371 Markdown files checked, pass |
| Board validate/next/show/render and `git diff --check` | Pass |

The snippet and peer checks ran from `/private/tmp/ws08_validate.py` with
scratch-only state. They are builder evidence, not an independent verdict.
The fake peer is a repository test fixture; installed users must substitute
their own trusted local stdio server. No live/paid provider, credential,
external network request, clean isolated install, deployment or delivery is
claimed. WS-09 and initiative-level aggregate review remain separate.

# VAL-018 independent review — MCP-WS-08 documentation correction

**Verdict: VERIFIED**

I reviewed candidate `08141407f7a7c3ca37174c8950bf552180df47c8` against REM-009 and the complete original WS-08 aggregate. The two VAL-017 findings are resolved, and all five original WS-08 acceptance criteria are met. There are **no numbered findings**. This is an independent validation result; maintainer acceptance and delivery remain separate.

| Criterion | Assessment |
| --- | --- |
| REM009-F01 / WS08-AC01 | The guide now distinguishes optional server connection failure from a strict `include_tools` registration requirement. An independent local probe registered `mcp_demo_probe` under both strict-name and category-only selection. With a missing optional command, strict selection failed with `missing_include` after `connection_failed`; category-only selection completed with no MCP tools. A missing required peer failed startup. The guide warns that `include_categories: [mcp]` admits every valid discovered MCP tool when the peer is available. |
| REM009-F02 | The configuration summary names both supported selected-mode rules: canonical `include_tools` and `include_categories: [mcp]`. The category-only snippet parsed through Runtime and Chat and registered the local peer without a tool-name include. This matches `packages/friday-runtime/src/friday_runtime/mcp_registration.py:440-451,568-576`. |
| WS08-AC02 | The guides distinguish discovery and registration caps from Chat’s per-turn tool count, schema and result reservation, and memory floor. The behavior matches `packages/friday-core/src/friday_core/mcp.py:46-61,98-122` and `packages/friday-chat/src/friday_chat/tools/selection.py:555-664`. They describe checked transcript provenance and default-disabled, explicitly opted-in long-term MCP ingestion, including the distinction between a pending and published memory. |
| WS08-AC03 | The troubleshooting guide removes the unsupported HTTP `MCPClient`/`register_mcp_tools` example. The guide and READMEs match the public `RuntimeKernel.mcp_provider`, `MCPChatRegistry.provider`, and typed `operational_diagnostics` surfaces. They identify `config_file` as rejected and integrated remote transport, refresh, resources/prompts, server exposure, and a Chat health command as deferred. The separate programmatic stdio/SSE client and server APIs exist in `friday-mcp`. |
| WS08-AC04 / AC05 | The original diff contains exactly the 11 approved product paths plus process artifacts; the remediation changes exactly four approved product paths. There are no runtime source, test, package metadata, other-template, or historical-validation changes. All four guide YAML snippets and both distributed template copies parsed through Runtime and Chat MCP configuration. Chat environment interpolation succeeded with a synthetic value and rejected its absence; both parsers rejected `config_file` at either attempted level. The fenced `friday-mcp` README Python example printed `['mcp_demo_probe']`. All 35 local links scanned in the touched Markdown resolved. |

At review start and close, all **11 corrected product hashes** matched `REM-009-product-manifest.json`, and all **18 authority hashes** listed in `VAL-018-request.yaml` matched the current files. The candidate’s 11 product files are unchanged at current HEAD `5a8ce9d44c8bd31ca40e6c77dedb1630dad801eb`. The original range `d9eb81d6e67bafc71346e142c1d1fd0c61ced6df..08141407f7a7c3ca37174c8950bf552180df47c8` contains exactly those 11 product paths; `f8970313655e6e18b39d14dc1f151b5a7b5aaa33..08141407f7a7c3ca37174c8950bf552180df47c8` changes only `docs/guides/10-configuration.md`, `docs/guides/13-troubleshooting.md`, `docs/guides/17-mcp-client.md`, and `packages/friday-runtime/README.md` as products. The VAL-017 report and evidence are unchanged from their recording commit `e999152` through the corrected candidate and current HEAD. All five unrelated dirty-path states and per-file byte hashes matched the prior VAL-017 snapshot and this review’s start/close snapshots. I made no governed repository or Git changes.

Checks used `UV_CACHE_DIR=/private/tmp/friday-uv-cache` and `LITELLM_LOCAL_MODEL_COST_MAP=true`:

| Check | Result |
| --- | --- |
| Runtime package tests | **195 passed** |
| MCP package tests | **65 passed** |
| Four focused Runtime/Chat MCP config, budget and memory modules | **92 passed** |
| Four MCP integration modules | **56 passed** |
| Broad Chat package tests | **Nonzero:** 620 passed, 5 skipped, one provider-free PTY 0.8-second timing assertion failure, and three localhost fixture-bind `PermissionError`s |
| `friday-chat --help` | Passed; `--config` and `--runtime` present, fake runtime is default, no MCP health command |
| Documentation lifecycle command as requested | Nonzero because a nested `uv` invocation attempted an unavailable network download; with `UV_NO_SYNC=true`, **375 Markdown files passed** |
| Board `validate`, `next`, `show friday-mcp`, `render --check` | Passed; 23 tasks, initiative `started`/`granted`, local delivery, VAL-018 next gate |
| Both `git diff --check` ranges | Passed |
| Independent snippet, template, README, stdio lifecycle, environment, rejection, and link probe | Passed after correcting my scratch-only probe to parse the Chat templates’ MCP stanzas as Runtime input |

The broad Chat failure names and counts match the pinned VAL-017 result. Relevant test and source paths are byte-unchanged across this documentation candidate, apart from the approved packaged YAML template; the Chat suite remains nonzero and is not claimed as passing. No live provider, paid endpoint, real credential, external network UAT, merge, push, or release was used. Owned local stdio peers were stopped.

Scratch evidence: `/private/tmp/val018_start.json`, `/private/tmp/val018_close.json`, `/private/tmp/val018_audit.py`, `/private/tmp/val018_probe.py`, `/private/tmp/val018_tests.py`, and `/private/tmp/val018_{runtime,mcp,focused,integration,chat,cli,docs,board,render}.log`.

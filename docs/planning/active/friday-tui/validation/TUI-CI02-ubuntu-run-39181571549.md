# TUI-CI02 Ubuntu diagnosis: run 39181571549

**Result:** Failed. [GitHub Actions run 39181571549](https://github.com/CIChuck/agent-framework/actions/runs/39181571549)
tested source and checkout
`49adbcb50d8e6b238172845fe32ef1ddfe279f4a` on Ubuntu 24.04.5,
Python 3.13.12, uv 0.11.3 and the locked mcp 2.3.0 dependency. This was the
[independently verified pre-push candidate](VAL-TUI-CI02-preflight-49adbcb5.md).
The branch push was authorized, but CI02 and CI01 are not Linux-verified.

| Gate | Ubuntu result |
| --- | --- |
| Neutral loader and Chat facade | 21 passed |
| Full Runtime | 333 passed, 1 failed: `test_real_public_kernel_stdio_profiles_and_child_cleanup[auto-True]` |
| Focused Runtime auto/modern case, repeated | Failed 3/3, each after 1.726–1.749 seconds |
| Direct MCP official SDK `auto` stdio case, repeated | Failed 3/3 at `client.connect()` with peer error `-32022` during legacy `initialize` |
| Plain and colored Chat help capture | Passed |
| Full Chat | 827 passed, 23 skipped, 1 warning |
| Unchanged `friday-cli` | 155 passed |
| 13 wheels, Runtime metadata, installed Runtime/Chat isolation and `uv pip check` | Passed |

The Runtime diagnostic exposed `mcp_provider.lifecycle` outcome
`connection_failed`, not `connection_timeout`. Its synthetic child had no
retained client, no available child return code and zero tool records after
cleanup. The direct MCP traceback shows an `auto` client sent legacy
`initialize` with protocol version `2024-11-05` to the modern SDK peer and
received error `-32022`. This is an unsupported-protocol error, rather than
a connection timeout. The full Runtime modern-profile case
passed while the auto/modern case failed.

**Read-only hypothesis check on macOS:** With unchanged production source and
the same SDK fixture delayed 1.6 seconds before startup, a direct `modern`
client connected in 1.919 seconds; a direct `auto` client failed in 1.926
seconds with the same `-32022` error. This reproduces the observed pattern
and supports the inference that `auto`'s half-budget modern probe expires
before a slower peer is ready, then tries legacy initialization on a modern
peer. The Ubuntu log does not directly expose the first probe's result, so
the precise trigger still needs a focused framework test before correction.

**CI02-C decision:** Its required evidence gate is not met. The Runtime
lifecycle is `connection_failed` and repeated direct MCP interoperability
fails. Do not raise the synthetic or production timeout under CI02. The
approved directive stops before `friday-mcp` source edits; the proposed
[CI03 framework directive](../directives/CD-TUI-CI03-mcp-auto-negotiation.md)
defines the next approval decision. The successful Chat, CLI and wheel gates
do not close the red Runtime/MCP gate or final Linux terminal UAT.

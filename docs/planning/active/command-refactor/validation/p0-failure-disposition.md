# P0 baseline failure controls and disposition

Date: 2026-11-04
Starting HEAD: `a8d9bf3f` (product source unchanged from `fc028f3b`)
Status: Controlled local Chat baseline green; P0 case-level/packaging proof incomplete

## Method

Reproduce with:

```sh
uv run python docs/planning/active/command-refactor/validation/p0/isolate_failures.py
uv run python docs/planning/active/command-refactor/validation/p0/isolate_failures.py --full
uv run python docs/planning/active/command-refactor/validation/p0/probe_no_runtime.py
```

The control script extracts the two committed Chat example files using `git show
HEAD:<path>` into a temporary directory. A temporary pytest collection plugin
redirects only the `EXAMPLE_CONFIG` / `EXAMPLE_MODEL_LIBRARY` constants in
`test_config_compatibility.py` and `test_command_disposable_uat.py`. It does not
rewrite the tracked files, alter test assertions, or change production code.
The two lanes retain `TERM=dumb` or explicitly set `TERM=xterm-256color`.
The full lane uses committed examples and xterm. This is a controlled workspace
baseline, not an isolated install or complete clean-checkout run.

## Results and explanations

| Control | Result | Evidence |
| --- | --- | --- |
| Committed examples; original `TERM=dumb`; three failing nodes | 1 passed, 2 failed | [log](p0/head-examples-original-term.log), [manifest](p0/failure-controls.json) |
| Committed examples; `TERM=xterm-256color`; same three nodes | 3 passed | [log](p0/head-examples-xterm.log) |
| Full Chat suite; committed examples; xterm; live LM Studio file excluded | 826 passed, 1 deprecation warning; 46.74s | [log](p0/head-examples-xterm-full-chat.log), [manifest](p0/full-control.json) |
| Fresh no-runtime context; default invocation of all 50 names | 50 captured, zero unhandled exceptions | [audit](default-behavior-audit.md), [full state/output receipt](p0/no-runtime.json) |

The earlier unmodified-worktree run remains 823 passed / three failed; retain
that receipt as evidence of the actual dirty-worktree environment.

1. **Example model alignment:** Passes when using the committed repository
   examples. The working-copy model-library edits differ from packaged examples.
   Preserve those edits as separate work, rather than changing packaged examples
   or compatibility expectations during extraction.
2. **Tool-adapter UAT check:** The dirty config enables integrated MCP, so
   `build_runtime()` wraps native tools in `MCPChatRegistry`; the UAT fixture
   requires `FrameworkToolRegistryAdapter`. The committed config disables MCP
   and reaches the terminal sequence without that type failure. Under dumb TERM
   it then fails the terminal-clear-byte assertion; with xterm the entire
   provider-free UAT passes. This is a config-sensitive fixture boundary, not
   evidence that MCP itself is broken. MCP-enabled UAT is a separate obligation.
3. **Clear-screen PTY:** Both terminal-clear assertions fail under dumb TERM and
   pass under xterm, with the same source/assertions. Use xterm for this terminal
   evidence lane; do not amend `/cls` behavior based on the dumb-terminal result.

These controls explain the observed failures without source/test fixes. They do
not authorize removal of a test, waiver of actual terminal requirements, or
acceptance of the pre-existing config edits.

## Contract consequences and remaining gates

- Retain xterm and committed example identity in reproducible baseline receipts.
  Do not silently replace the original dirty-worktree result with a green claim.
- Preserve UI-neutral clear intent; test terminal clearing in the frontend lane.
- Tool inventory must operate through a neutral capability, not a concrete
  native-registry type assumption. `/tools` must support the admitted aggregate
  inventory while preserving categories and MCP diagnostic meaning.
- Separate CLI's missing `friday_cli.main:app` remains an observed pre-existing
  entry-point limitation. No repair is bundled with extraction; characterize the
  isolated wheel and decide its treatment before applicable delivery gates.
- Complete per-command assertion and transitive effect/error-order mapping,
  production-adapter coverage and build/isolated-install baselines. Review the
  exact API and bounded directive before constructing the shared package.

The [selected assertion audit](behavior-assertion-audit.md) documents inspected
checks and remaining limits. No complete P0/P1 signoff, independent validation,
maintainer acceptance, live-provider proof or TUI construction is claimed.

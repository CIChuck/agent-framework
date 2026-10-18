# TUI-CI01 first Ubuntu Actions run

**Outcome:** Failed; this run does not establish Linux verification.

**Run:** [Friday TUI Linux verification, #39172562601](https://github.com/CIChuck/agent-framework/actions/runs/39172562601), push event on `feature/friday-tui`, 2026-10-18 22:30:57–22:31:50 UTC. Job [#117808499173](https://github.com/CIChuck/agent-framework/actions/runs/39172562601/job/117808499173) concluded `failure`.

**Source and checkout SHA:** both
`e3e2e974b22d193794dc5420cbad29a36b40e3e8`.

**Environment:** GitHub-hosted `ubuntu-24.04` image, Ubuntu 24.04.5 LTS,
Python 3.13.12, uv 0.11.3. The job had `contents: read` permission and no
provider credentials.

Checkout, uv setup, locked root `dev` sync, version logging and the focused
neutral-loader/Chat-facade tests succeeded. The focused suite reported
**21 passed**. Full Runtime test collection then failed before running its
tests:

```text
packages/friday-runtime/tests_runtime/test_mcp_http_integration.py:19
    from cryptography import x509
E   ModuleNotFoundError: No module named 'cryptography'
1 error in 6.00s
```

The full Chat and unchanged `friday-cli` suites, local-wheel build, Runtime
metadata inspection and installed-import checks were skipped. No wheel hashes
or installed-import results exist for this run.

**Diagnosis and bounded correction:** The workflow synced only the root
project's `dev` extra. The test file requires `cryptography`; the existing
`uv.lock` includes it through `mcp==2.3.0`, selected by
`friday-framework-mcp[dev]`. `RD-TUI-CI01-02` in the
[approved construction directive](../directives/CD-TUI-CI01-linux-actions.md)
selects the root and MCP package `dev` extras together while preserving the
lock and all protected package/test paths. A new successful Ubuntu run for
the corrected commit is required.

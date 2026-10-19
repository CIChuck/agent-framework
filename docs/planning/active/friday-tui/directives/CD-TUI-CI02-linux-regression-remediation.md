# CD-TUI-CI02: Diagnose and correct Linux CI regressions

**Status:** Proposed for maintainer review; not approved and not implementation
authority. No source, test or workflow edit under this directive may begin
until the maintainer approves its exact scope and the packet/board record that
approval. TUI-CI01 remains `started` and `changes_requested`.

**Initiative/unit:** `friday-tui` / TUI-CI02

**Planning baseline:** `feature/friday-tui` at
`927dacc81d21a6e119a0c06bb8a2443d069157f5`. The approved TUI-CI01
workflow and all existing package behavior are the starting point.

## Authority and decision to approve

The controlling requirements are `AGENTS.md`, repository engineering and
independent validation policies, Friday TUI decisions D-01/D-02/D-05/D-08/
D-10/D-11, and the CI01 [independent findings](../validation/VAL-TUI-CI01-final-a7519db2.md)
CI01-07 through CI01-10. The read-only
[before-code diagnosis](../validation/TUI-CI02-before-code-diagnosis.md)
distinguishes confirmed behavior from the unresolved MCP cause. CI01's
workflow-only authority does not permit these
test changes. Approval of this directive would grant only the bounded paths
and behavior below; it would not accept CI01, authorize TUI product code,
approve a PR/merge/release, or waive Linux terminal UAT.

**Proposed Linux maintenance decision for approval:** Keep the current
`friday-chat` behavior: `/reorganize` safely refuses on Linux because durable
lease semantics are verified only on Darwin. Make tests assert that refusal
and absence of mutation on Linux while retaining meaningful macOS command
checks. Full Linux maintenance support, if desired later, needs its own
cross-platform durability design and directive. This interpretation preserves
the existing Chat and `friday-cli` feature sets and behavior. The maintainer's
reply "approved continue" to the recommended next steps is treated as
authorization to prepare this proposal, not as approval of unseen file edits.

## Objective and testable subunits

1. **CI02-A, diagnosis before correction:** On a GitHub-hosted Ubuntu 24.04
   runner with locked Python 3.13 dependencies, capture the synthetic MCP
   test's `mcp_provider.lifecycle` outcome and relevant synthetic child
   diagnostics when `auto`/modern startup fails. Run
   `test_official_sdk_230_real_stdio_catalog_text_structured_and_reaping[auto]`
   from `packages/friday-mcp/tests_mcp/client/test_stdio_interop.py`
   separately to distinguish client/fixture startup from Runtime composition.
   Preserve the failing assertion and job
   conclusion. Capture complete `friday-chat --help` test output with and
   without ANSI color, without logging secrets or unrelated environment
   values. Record source SHA, commands, outputs and inference limits.
2. **CI02-B, Chat test portability:** Correct only the Chat tests listed
   below. Normalize ANSI styling before asserting visible help option text;
   still assert all declared help options and that `--version` invocation
   returns the package version. The current test's literal assertion fails
   when `GITHUB_ACTIONS=true` or `FORCE_COLOR=1` because Rich inserts ANSI
   codes within `--version`; the option is present after stripping ANSI.
   For `/reorganize`, verify Linux's existing safe refusal, no maintenance
   mutation and preserved command syntax/error handling. Preserve the
   existing meaningful macOS dry-run/execute expectations; do not blanket
   skip or xfail the four failing cases.
3. **CI02-C, bounded MCP test correction only if justified:** If CI02-A
   shows a timeout in the synthetic `auto`/modern startup path, and repeated
   direct MCP interoperability checks pass, adjust only that integration
   fixture's connection timeout to a documented bounded value supported by
   measured Ubuntu startup time. Do not change production MCP timeout,
   retry, fallback or cleanup behavior. Rerun the exact case repeatedly and
   the full Runtime suite. If the outcome is not a fixture-budget timeout,
   or the correction does not produce repeatable success, stop and draft a
   separate framework-source directive from the captured evidence.

## Exact allowed edits after approval

- `packages/friday-chat/tests_chat/test_cli.py` — ANSI-independent visible
  help assertions and focused color-mode coverage only.
- `packages/friday-chat/tests_chat/test_maintenance_commands.py` — portable
  assertions for existing Linux refusal and macOS command behavior only.
- `packages/friday-runtime/tests_runtime/test_mcp_http_integration.py` —
  synthetic-case diagnostic on failure and, only under CI02-C's evidence gate,
  its synthetic timeout value.
- `.github/workflows/friday-tui-linux.yml` — focused direct MCP interop and
  diagnostic invocations while retaining every existing full-suite, wheel,
  isolation and failure gate.
- This TUI packet's directive, authority, index, execution log and validation
  evidence; the TUI board entry and generated dashboard.

No product source, `friday-cli` source/tests, package metadata, lockfile,
configuration schema, release tooling or TUI package edit is authorized.
If diagnosis requires any other path, stop and request a new exact directive.
Do not print provider keys, credentials or real runtime configuration values;
use only existing synthetic fixtures.

## Required verification

- Before edits, retain the current failure baseline: [run
  39175828523](https://github.com/CIChuck/agent-framework/actions/runs/39175828523)
  on `927dacc8`: focused 21 passed, Runtime 333 passed/one failed,
  Chat 816 passed/five failed/23 skipped, unchanged `friday-cli` 155 passed,
  and wheel/installed-isolation checks passed.
- On macOS, reproduce the help assertion under `GITHUB_ACTIONS=true`, then
  prove the corrected test passes with both color enabled and disabled.
  Run the focused Chat CLI and maintenance tests, full Chat suite, full
  Runtime suite and unchanged `friday-cli` suite after edits.
- On Ubuntu, run the direct MCP stdio case, repeated focused Runtime
  `auto`/modern case, full Runtime and Chat suites, and unchanged
  `friday-cli` suite. Retain the existing wheel metadata, isolated installed
  Runtime/Chat checks and `uv pip check`. A skip/xfail or a green job on a
  different source commit does not satisfy CI02 or CI01.
- Run focused Ruff/static checks for changed test code, workflow YAML and
  embedded Bash/Python syntax, `uv lock --check`, board validation,
  dashboard check and `git diff --check`. Inspect the exact allowed-path
  diff. Commit a stable candidate, obtain fresh-context read-only
  independent review, and record all findings. A separate maintainer
  delivery authorization is required before a push to run Actions.

## Stop and closeout gates

Stop if the MCP lifecycle outcome points to product code, the timeout
correction would mask a functional defect, Linux maintenance should execute
in the first release, any protected Chat/CLI behavior changes, a new
dependency is needed, or any edit outside the exact allowed paths is
required. Do not hide red checks with `continue-on-error`, conditional skips,
or expected failures. Record a new directive or maintainer decision before
resuming. CI02 completion requires a green exact-candidate Ubuntu run and
fresh independent `VERIFIED` review; that evidence can then support CI01's
deferred Linux gate. It is not TUI release UAT or maintainer acceptance.

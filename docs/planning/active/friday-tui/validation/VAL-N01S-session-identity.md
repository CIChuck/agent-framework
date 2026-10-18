# VAL-N01S: neutral session-identity work-unit review

**Outcome:** VERIFIED

**Reviewer:** `/root/n01s_independent_validation`, separate fresh-context
Codex GPT-6-family agent (exact model version unavailable)

**Date/mode:** 2026-10-18; full, read-only work-unit review

**Initiative/unit:** `friday-tui` / TUI-N01S. This result is neither
maintainer acceptance of the initiative nor delivery authorization.

## Frozen inputs

- Branch: `feature/friday-tui`.
- Base: `793aa084266043b8c58beb7732d4c58b0f156c0c`.
- Candidate: `073134f9b13ddfbb07e884c7e1c05c872e0783f7`.
- Exact diff: `git diff 793aa084266043b8c58beb7732d4c58b0f156c0c..073134f9b13ddfbb07e884c7e1c05c872e0783f7`.
- `docs/planning/active/friday-tui/authority.json` SHA256:
  `50ffbf578f16ae8518f4096c7e94acd1d8c407009c42c5c1f0afb61a41349830`.
- `docs/planning/active/friday-tui/directives/CD-TUI-N01S-session-identity.md`
  SHA256: `2d444dc3c49e736b565e090e2edbdb630b1e5b4604bfd8ee7a646aed8e2c10c6`.
- `docs/planning/active/friday-tui/replacement-plan.md` SHA256:
  `12a81e70d37abc7235f56ef8e6981037e749ec2a11db51c7da7a5d105a7f9125`.
- `docs/planning/active/friday-tui/neutral-capability-map.md` SHA256:
  `ed777dfe4666f5ca70fcb7e7437b9b7790210d0be04b8d45f7543953009dbc0d`.
- `docs/planning/board.yaml` SHA256:
  `fece38f0af9adedc49fbcd379ce6d20c7ad816a16de707f29cad4a62cce91408`.

These are the frozen candidate-commit bytes. Later process-only updates to the
current board and authority manifest record this verdict and close code
authority for future units; they do not alter the reviewed source or directive.

The reviewer independently checked these hashes, read `AGENTS.md` and the
engineering, lifecycle and independent-validation policies, and inspected the
committed candidate. The dispatch supplied the candidate and authority paths,
not builder reasoning. A separate worktree was not used; the shared checkout
was clean at the start and end of the read-only review. No files were edited
by the reviewer.

## Criteria and evidence

The work-unit acceptance criteria are the exact behavior and negative cases in
CD-TUI-N01S, the TUI-N01S row in `replacement-plan.md`, and the slice-relevant
parts of packet AC-08, AC-09 and AC-13. The complete TUI AC-01 through AC-34
remain future initiative gates.

- The diff changes only the three source/test paths allowed by the directive,
  plus scoped planning-state documents. `packages/friday-runtime/src/friday_runtime/session_identity.py:9-48`
  retains the exception, frozen value object, validation text, UUID-shaped
  generation, resolver signature, typed-object reuse and mismatch message.
- `packages/friday-chat/src/friday_chat/session.py:7-46` imports and re-exports
  the same three objects; `FridaySession` keeps its fields and identity check.
  New contract cases at
  `packages/friday-runtime/tests_runtime/test_session_identity.py:19-100`
  cover generation, invalid input, injection, mismatch, Chat object identity,
  legacy pickle global lookup and neutral import closure. Existing Chat tests
  cover propagation through runtime, app, commands, replay, adapters and
  persisted transcript.
- Required focused Chat/Runtime tests: **117 passed**. All unchanged
  `packages/friday-cli/tests_cli` tests: **155 passed**. Broader Runtime suite:
  **324 passed**. Broader Chat suite: **828 passed, 5 skipped**; one existing
  deprecation warning. The full suites required local loopback sockets and
  made no live-provider request.
- Changed-file Ruff and Mypy pass; `git diff --check` passes. Board validation
  passes for 34 tasks. Both affected wheels built offline. An outside-checkout
  temporary installation contains the neutral module; installed Runtime
  import loaded neither Chat nor CLI, and installed Chat re-exported the same
  class, exception and resolver objects.
- `friday-chat --version` remains `0.1.0a4` and `--help` exits zero. The
  existing `friday --help` failure still exits one because the console script
  imports nonexistent `friday_cli.main.app`; this matches the before-code
  baseline and is not an N01S regression.

Reproduce the core checks from the candidate commit with:

```text
uv run pytest -q packages/friday-runtime/tests_runtime/test_session_identity.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_command_registry.py packages/friday-chat/tests_chat/test_cli.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_runtime.py packages/friday-runtime/tests_runtime/test_config.py packages/friday-runtime/tests_runtime/test_model_library.py
uv run pytest -q packages/friday-cli/tests_cli
uv run pytest -q packages/friday-runtime/tests_runtime
uv run pytest -q packages/friday-chat/tests_chat
uv run ruff check packages/friday-runtime/src/friday_runtime/session_identity.py packages/friday-chat/src/friday_chat/session.py packages/friday-runtime/tests_runtime/test_session_identity.py
uv run mypy packages/friday-runtime/src/friday_runtime/session_identity.py packages/friday-chat/src/friday_chat/session.py packages/friday-runtime/tests_runtime/test_session_identity.py
uv run python scripts/friday-dev-board.py validate
git diff --check 793aa084266043b8c58beb7732d4c58b0f156c0c..073134f9b13ddfbb07e884c7e1c05c872e0783f7
```

## Findings and limits

No findings. Repository-wide Ruff reports 534 existing errors outside the
changed files. The documentation lifecycle checker reports six broken absolute
links in the unchanged telemetry VAL-001 review report. Changed-file checks
and the TUI board/dashboard pass. The installed-package smoke used existing
workspace dependencies for transitive imports, so it does not prove a fresh
dependency resolution. The intended `SessionIdentity.__module__` change is
documented in the directive; the old Chat import and pickle global lookup
passed. This identity-only unit changed no configuration or package metadata
and requires no user-facing TUI UAT. No credential, live-provider, paid-service,
push, merge, release or deployment action was in scope.

# CD-TUI-N01S: neutral session identity

**Status:** Approved for construction on 2026-10-18 by Chuck Russell

**Initiative/unit:** `friday-tui` / TUI-N01S

**Branch/source baseline:** `feature/friday-tui` /
`c34269867be50f71923c93c95a63236a35505812`

**Current authority:** `granted` for TUI-N01S only. Chuck Russell approved this
exact directive in the current session by answering "approved, proceed" to the
explicit CD-TUI-N01S scope-and-authority question. The board and authority
manifest record the same bounded grant. Later TUI units remain design-only.

## Purpose and observable result

Give the future independent TUI a UI-neutral session identity type without
importing Chat or CLI code. Preserve existing Chat identity generation,
injection, mismatch errors and propagation into its runtime and persisted
transcript. This slice alone does not make Chat runtime assembly, commands or
configuration available to the TUI.

The source-backed [N00 review](../n00-integration-review.md),
[replacement plan](../replacement-plan.md) and
[capability map](../neutral-capability-map.md) govern this slice. The complete
Chat/`friday-cli` feature set and behavior remain the protected baseline.

## Exact change boundary

Permitted source edits:

1. Add `packages/friday-runtime/src/friday_runtime/session_identity.py` with
   `SessionIdentity`, `SessionIdentityMismatchError` and
   `resolve_session_identity()` preserving their existing value validation,
   `generate()` shape, resolver signature, object reuse and mismatch message.
2. Edit `packages/friday-chat/src/friday_chat/session.py` only to import and
   re-export those same three objects. Keep `FridaySession`, its fields,
   initialization and mismatch behavior in Chat. Existing import paths must
   resolve to the **same** neutral class, exception and function objects.
3. Add `packages/friday-runtime/tests_runtime/test_session_identity.py` with
   focused value, generation, injection, mismatch, re-export identity and
   import-closure tests. Existing Chat tests are comparison fixtures, not
   wholesale rewrite targets.

No edits to `packages/friday-cli`, Chat command handlers, runtime assembly,
configuration models, transcript schemas, package versions/metadata, or TUI
code. No new dependency, global configuration, provider call or file write is
required for the identity primitive. If a required change falls outside these
paths, stop and revise the directive before editing it.

## Required behavior and negative cases

- A generated identity remains immutable, unique per call and formatted
  `session_<uuid4 hex>`; an injected typed identity is returned by object
  identity, not copied. A matching `session_id` with a typed identity returns
  that object. A string-only injection constructs the same validated type.
- Empty or untrimmed values raise `ValueError` with the current text. A typed
  versus string mismatch raises the same exception class and message as the
  before-code Chat baseline. `FridaySession` still rejects its own mismatched
  session ID without changing other session fields.
- `friday_chat.session.SessionIdentity is
  friday_runtime.session_identity.SessionIdentity`, likewise for the error
  and resolver. Existing Chat runtime, app, replay, command context and
  transcript adapters keep one identity value through a session; no duplicate
  or changed persisted session ID appears.
- Importing the new neutral module or `friday_runtime` must not import
  `friday_chat` or `friday_cli`. Importing the Chat facade must continue to
  work. Do not infer parity merely from import success: execute the existing
  identity and transcript tests.
- The class's `__module__` changes with ownership. Check that old
  `friday_chat.session` imports and any documented serialization path still
  resolve; do not claim byte-for-byte module-introspection parity. If a
  supported persisted format depends on the old module path, stop and add a
  compatibility fixture before proceeding.

## Verification and stop conditions

Before edits, retain the N00 results: 108 focused Chat/Runtime tests, 155
`friday-cli` tests, live 50-command/three-alias metadata match, Chat launcher
smokes and the existing `friday --help` import failure. After edits:

1. Run the new Runtime identity tests and unchanged
   `packages/friday-chat/tests_chat/test_session_identity.py`,
   `test_transcript_production_commands.py`, `test_command_registry.py`,
   `test_cli.py`, `compat/test_config_compatibility.py`, `test_runtime.py`,
   plus Runtime `test_config.py` and `test_model_library.py`. Compare identity,
   exception and persisted-session behavior against the before-code fixtures.
2. Run all `packages/friday-cli/tests_cli` tests unchanged. Recheck Chat
   `--version`/`--help` and the CLI `friday --help` outcome; report its known
   baseline import failure rather than changing CLI code in this slice.
3. Run Ruff, Mypy and `git diff --check` on affected source/tests; inspect
   the exact diff for only the allowed paths. Verify the neutral import
   closure and the wheel's inclusion of the new public module. Build/install
   candidate packages outside the checkout where available before calling
   the installed-package check complete.
4. Commit a stable candidate only after local checks pass, then hand its
   exact directive, authority, commit, diff and test evidence to a fresh,
   read-only independent validator under repository policy. A changed
   candidate needs a fresh validation. `VERIFIED` is not maintainer
   acceptance or delivery authorization.

Stop if identity propagation changes, an existing Chat or `friday-cli`
behavior regresses, the neutral import loads frontend code, a persisted format
breaks, or the change needs another source path or dependency. Do not start
TUI-N01A, TUI-N01B or TUI package implementation under this directive.

**Approval fields:** Maintainer Chuck Russell; approved 2026-10-18; scope
TUI-N01S and the three exact source/test paths above. Independent product
validation and UAT have not yet run.

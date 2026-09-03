# Friday Chat 0.1.0a1 Release Evidence

- Evidence date: 2026-08-28
- Branch: `feature/friday-chat-typed-llm-config`
- Implementation commit: `51a112c`
- Distribution: `friday-chat==0.1.0a1`
- Status: published and post-publication verified in the final cohort
- Publication: [production PyPI 0.1.0a1](https://pypi.org/project/friday-chat/0.1.0a1/)
- Live provider lane: implemented but not authorized or executed

## Superseding Cohort Decision

On 2026-08-28 the maintainer approved a full lock-step `0.1.0a1` cohort for
every current Friday distribution and internal exact pin. The blocker and
rejected hashes below remain historical evidence; they are not the final release
state. The final clean artifacts, Python 3.10-3.13 wheel installs, root `all`
extra, source-only install, and hashes are recorded in the
[cohort release evidence](../../friday-package-cohort-0.1.0a1-release-evidence.md).
That cohort was subsequently published and revalidated from production PyPI.

## Scope And Worktree

The implementation commit contains Friday Chat source, tests, package metadata,
templates, planning/reference documents, lock state, and package-generic release
helper changes. It does not contain the pre-existing repository-example edits to
extraction temperature, tool count, or trailing whitespace. Unrelated local
reference documents also remain untracked.

The artifact candidate was built from a detached clean worktree at `51a112c`,
not from the dirty development checkout.

## Implementation Evidence

The primary `llm:` path now supports strict canonical generation, explicit
transport/model identity, bounded provider options, typed complete/stream calls,
and one documented legacy compatibility window. Deterministic loopback coverage
proved final wire emission for `temperature`, `top_p`, `top_k`, `min_p`, presence
and frequency penalties, repetition penalty, max tokens, and reasoning controls.
Provider-option mismatches fail before the loopback request count changes.

Non-primary extraction, maintenance, compaction, passage-routing, smart-file,
and reorganization consumers remain on isolated legacy services and are recorded
in the deferred-consumer handoff.

## Deterministic Validation

Environment:

- Python `3.13.10`
- uv `0.11.3`

Focused results:

- migration config/adapter/live-module collection: `36 passed, 5 skipped`;
- full Friday Chat suite: `418 passed, 5 skipped, 2 failed`;
- focused Ruff: passed;
- focused mypy: passed for 93 source/test files.

The two Friday Chat failures are the same baseline PTY clear-screen failures:

- `test_real_app_cli_pty_command_uat_is_contained_and_provider_free`;
- `test_production_clear_emits_control_sequence_through_pty`.

Both expect Rich clear-screen control bytes that are absent in the current PTY
environment. They do not overlap LLM configuration or adapter behavior.

Repository-wide results:

- default pytest collection stopped on the pre-existing duplicate
  `test_display` module name;
- pytest with `--import-mode=importlib`: `2154 passed, 14 skipped, 15 failed`;
- repository Ruff: 12 unrelated existing findings;
- repository mypy stopped on the same duplicate `test_display` module name.

The 15 broad pytest failures comprise nine legacy Copilot mock/model validation
failures, the two baseline Friday Chat PTY failures, two runtime built-in-tool
registration failures, and two optional document-reader expectation failures.
No new migration test failed.

## Artifact Checks

Clean-worktree artifacts:

- `friday_chat-0.1.0a1-py3-none-any.whl`, 175683 bytes;
- `friday_chat-0.1.0a1.tar.gz`, 258942 bytes.

The mixed-version source metadata validator passed. The custom wheel/sdist
validator passed, including dependency metadata, expanded `full` extra,
entry point, resources, license, and sensitive-content scans. Twine passed both
files.

These hashes identify only the rejected diagnostic candidate and are not frozen
release hashes:

- wheel SHA-256:
  `3c729f5baadb9a34ac1d7ca2fb0aea763490c81478ea1fc11b20ba3e5126aed3`;
- sdist SHA-256:
  `b1c61bff30b9efedd697a5f43be6987db3afc88705e0b893cdd0154d89268db4`.

Do not upload these files.

## Clean-Install Release Blocker

The first Python 3.13 clean installation failed before smoke execution with pip
`ResolutionImpossible`. The candidate requires
`friday-framework-llm==0.1.0a1`, while the published `0.1.0a0` wheels for Friday
Memory, Runtime, and CLI each require `friday-framework-llm==0.1.0a0`.

Read-only PyPI queries on 2026-08-28 found only `0.1.0a0` for Friday LLM,
Memory, Runtime, CLI, and Chat. Consequently:

- Friday LLM `0.1.0a1` is not yet registry-installable;
- the accepted Chat mixed-version matrix is unsatisfiable;
- Python 3.10-3.13 artifact smoke cannot proceed honestly;
- the live provider lane remains downstream of an unresolved release gate;
- TestPyPI/PyPI upload, tagging, and pushing remain prohibited.

The tactical plan records the recommended compatible `a1` cohort and the
required scope amendment. After that cohort is implemented and published in
dependency order, Friday Chat must be rebuilt from a clean commit and all
artifact, clean-install, Python-matrix, and opt-in live gates repeated.

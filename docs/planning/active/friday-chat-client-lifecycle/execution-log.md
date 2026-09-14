# Friday Chat Client Lifecycle Execution Log

## 2026-09-14 — Diagnosis And Authorization

- A live long-running session reported a 300-second background extraction
  timeout, one literal unclosed aiohttp session, and repeated prompt-toolkit
  `Exception None` dialogs.
- Traced the dialog to prompt-toolkit's temporary asyncio exception handler,
  which prints only a missing `exception` field and ignores aiohttp's meaningful
  `message` field.
- Confirmed installed LiteLLM 1.94.1 uses a one-hour async-client cache that
  dereferences expired clients without closing them.
- Confirmed stable upstream LiteLLM 1.100.1 contains owned-client eviction and
  finalizer lifecycle repairs for unclosed aiohttp sessions.
- Separated the background extraction timeout from the client-session
  lifecycle defect and from Friday's tool loop.
- The maintainer directed the agent to proceed with remediation.
- Created and approved CD-001. No push, merge, release, publication, or paid
  live-provider authority was granted.

## 2026-09-14 — Branch Preparation

- Preserved `feature/kanban-governance-portability` at `29a6b2a`.
- Created `feature/friday-chat-client-lifecycle` from verified governance
  baseline `fe15552`.
- Preserved unrelated `.DS_Store`, `family-tree.md`, configuration-backup, and
  sandbox-audit worktree state without modification.

## 2026-09-14 — Board Start

- Recorded the maintainer's current approval on the canonical development
  board.
- Moved the packet to `docs/planning/active/friday-chat-client-lifecycle/` and
  transitioned the initiative to `started` on
  `feature/friday-chat-client-lifecycle`.
- Began implementation under CD-001; the next gate is deterministic validation
  and a stable candidate commit.

## 2026-09-14 — CD-001 Implementation And Deterministic Validation

- Upgraded the exact LiteLLM dependency from 1.94.1 to 1.100.1 and refreshed
  the workspace lock without changing Friday package versions.
- Added the public Friday LLM process-client cleanup boundary and regression
  coverage for delegation, error propagation, and actual owned aiohttp-session
  eviction through LiteLLM's cache lifecycle.
- Added typed real and fake async-client lifecycle services to Friday Chat
  runtime composition.
- Added application shutdown cleanup after background cancellation and all
  LLM-dependent maintenance, using the existing bounded diagnostic and
  snapshot-failure accounting path.
- Configured prompt-toolkit input to preserve the application's event-loop
  exception handler, preventing message-only aiohttp diagnostics from becoming
  blocking `Exception None` dialogs.
- Focused lifecycle, input, app, and runtime tests: `49 passed`.
- Friday LLM package suite with deterministic localhost wire capture:
  `186 passed, 8 skipped`.
- Friday Chat package suite: `428 passed, 5 skipped`, with three existing PTY
  failures. A temporary LiteLLM 1.94.1 baseline reproduced the representative
  screen-clear and early-acknowledgement failures, demonstrating that they are
  not introduced by CD-001. No PTY source or test was changed.
- Focused Ruff passed for every changed Python file.
- Focused mypy with skipped dependency traversal passed for the four changed
  lifecycle/runtime/input/app source modules. Broader mypy remains blocked by
  the repository's Python 3.10 target parsing Python 3.12-only syntax in current
  NumPy stubs; the changed adapter also exposes one pre-existing unrelated
  `no-any-return` error outside the modified lines.
- The repository's default pytest command stops during collection because two
  package test trees both expose an unnamespaced `test_display` module. The
  non-destructive importlib-mode fallback completed with `2205 passed, 14
  skipped, 7 failed`; three failures are the already-baselined Friday Chat PTY
  cases and four are unrelated Friday Runtime/tool optional-registration and
  optional-reader expectations outside CD-001.
- No credential, provider call, external runtime state, package version, push,
  merge, tag, release, or publication action was performed.

## 2026-09-14 — Candidate Freeze

- Froze the CD-001 implementation, deterministic evidence, and validation-state
  metadata in one stable candidate commit. Its exact identifier and diff range
  are pinned in the VAL-001 request.
- Prepared VAL-001 as a fresh-context, full, read-only review. No governed file
  will change after dispatch without making the review stale.

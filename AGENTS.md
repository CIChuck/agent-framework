# Repository Guidelines

## Repository Policy
- The canonical engineering policy for this repository is [docs/reference/policies/repository-engineering-policy.md](docs/reference/policies/repository-engineering-policy.md).
- Development work state and authorization are tracked by [docs/planning/board.yaml](docs/planning/board.yaml) under [docs/reference/policies/development-task-lifecycle.md](docs/reference/policies/development-task-lifecycle.md).
- Independent post-generation review is governed by [docs/reference/policies/independent-validation-policy.md](docs/reference/policies/independent-validation-policy.md).
- All code changes must comply with that policy.

Priority operational rules for agents:
- Do not add `# mypy: ignore-errors` to source files under `packages/*/src` without an explicit waiver.
- Do not rely on `assert` as the sole enforcement mechanism for essential runtime invariants; use explicit exceptions.
- Prefer interface or contract fixes over repeated `cast(...)`.
- Cross-package contracts should use typed models or declared interfaces, not incidental implementation details.
- If a requested change conflicts with repository policy, stop and explain the conflict.
- Preserve unrelated local changes and generated state. Do not clean caches, `.friday/`, Chroma/transcript state, or dirty worktree files unless explicitly asked.
- Do not implement a queued task or infer approval or acceptance from a branch, push, merge, release, or stale plan label.
- Do not let an implementation agent approve its own work or treat a validator's `VERIFIED` result as maintainer acceptance.

## Development Planning & Code-Generation Authority

This `AGENTS.md` is the canonical operational entry point for repository code
generation. It delegates engineering constraints to the repository engineering
policy and delegates current task state, priority, and implementation authority
to the development board. It does not override either policy.

Before generating or modifying product code, an agent must:

1. Run `uv run python scripts/friday-dev-board.py validate`.
2. Run `uv run python scripts/friday-dev-board.py next` and inspect the selected
   task with `show <initiative>`.
3. Confirm the task is `started`, has `implementation_authority: granted`, and
   names the current feature branch. `approved` permits branch and execution
   preparation, but code generation begins only after the `started` transition.
4. Read the initiative packet. Its build plan defines authorized scope and
   acceptance criteria; its tactical plan defines implementation ordering and
   validation; and its execution log records progress and stop points.
5. Confirm every code-generating work unit has an approved construction
   directive that binds its exact scope, non-goals, tests, verification, and
   stop conditions. Only a maintainer-recorded lightweight-change exemption may
   replace the directive.
6. Stop and reconcile the board, packet, branch, source, and tests when they
   disagree. Directory placement or an old status label never supplies missing
   authority.

After generating code, the builder must commit a stable candidate and hand it to
a fresh-context, read-only validation subagent. The validator receives the
exact authority manifest, construction directive, candidate commit and diff,
acceptance criteria, and required checks, but not the builder's private
reasoning or conclusions. The validator returns exactly `VERIFIED`,
`CHANGES_REQUESTED`, or `BLOCKED` with reproducible evidence.

Applicable work remains `started` through independent validation and any
bounded remediation. A changed candidate or controlling authority invalidates
the prior result and requires a fresh review. The controller may propose
`completed` only after `VERIFIED`; only the maintainer may record `accepted`.
Validation does not authorize source edits by the reviewer, automatic
remediation beyond preauthorized low-risk scope, or any push, merge, release,
deployment, credential disclosure, or external side effect.

The planning architecture is:

- `docs/planning/board.yaml`: canonical current task registry;
- `docs/planning/README.md`: generated human-readable Kanban view;
- `docs/planning/queued/`: proposed or approved work not yet executing;
- `docs/planning/active/`: started work with implementation authority;
- `docs/planning/review/`: completed work awaiting maintainer acceptance;
- `docs/planning/blocked/`, `deferred/`, and `backlog/`: work carrying those
  non-authorizing conditions; and
- `docs/archive/completed/`: accepted historical packets and closeout evidence.

Work progresses through `queued -> approved -> started -> completed -> accepted`.
Only the maintainer may approve or accept work. Agents may record a start after
authorization and may propose completion with validation evidence. Delivery
state (`local`, `pushed`, `merged`, or `released`) is recorded separately and
never substitutes for approval or acceptance. The complete transition contract
is [docs/reference/policies/development-task-lifecycle.md](docs/reference/policies/development-task-lifecycle.md).

## Project Structure & Module Organization
- `packages/` contains the workspace libraries. The current package set includes `friday-core`, `friday-telemetry`, `friday-llm`, `friday-transcript`, `friday-memory`, `friday-agent`, `friday-runtime`, `friday-cli`, `friday-tools`, `friday-sandbox`, `friday-mcp`, `friday-speech`, `friday-finance`, `friday-moltbook`, and `friday-optimization`.
- `friday-runtime` is the current headless assembly layer. Prefer `RuntimeKernel` and `RuntimeConfig` for full-stack composition work.
- `friday-cli` contains terminal display/input/session components, compatibility container code, REPL/server hooks, and FastAPI-related modules. The declared console entry point is not a reliable complete CLI surface in this checkout.
- `friday-memory` is the central memory package: controller, adapters, context assembly, lifecycle, retrieval, ingestion, maintenance, and multi-agent memory.
- `friday-agent` owns agent abstractions, interactive/Copilot agents, routing/orchestration, registries, built-in agent tools, and workflows.
- `friday-tools` contains both general tools and several integration tools; be careful about cross-package coupling when adding new tools.
- `tests/` holds top-level integration and legacy/lab-style suites. Package tests live under package-local directories such as `packages/friday-memory/tests_memory` and `packages/friday-cli/tests_cli`.
- `experiments/` contains exploratory work and is included in root pytest discovery when it has `*/tests`.
- `docs/` contains guides, specs, design notes, build plans, and repository policy. Some older docs describe target or legacy architecture; verify against current package metadata before relying on them.
- `main.py` is only a minimal smoke entry point.

## FridayV2 Implementation Boundary
- FridayV2 planning and implementation are tracked under `docs/planning/` and the new `packages/friday-chat` app package.
- During the FridayV2 parity implementation pass, do not modify existing framework package source or tests under `packages/friday-*`, except for `packages/friday-chat`.
- Allowed FridayV2 implementation targets are `packages/friday-chat/`, `packages/friday-chat/tests_chat/`, minimal workspace metadata needed to register/run `friday-chat`, and FridayV2 planning docs.
- If FridayV2 work reveals a needed framework package fix or API improvement, record it in [docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md](docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md) instead of patching the frozen framework package during the parity pass.

## Build, Test, and Development Commands
- `uv sync --all-extras`: install all workspace dependencies, including optional extras.
- `uv sync`: install the default workspace dependency set.
- `uv run python main.py`: run the minimal repository smoke check.
- `uv run python -c "from friday_runtime import RuntimeKernel; from friday_agent import InteractiveAgent; print('Friday imports OK')"`: quick import sanity check.
- `uv run pytest`: run tests discovered by the root config (`packages/*/tests_*` and `experiments/*/tests`).
- `uv run pytest packages/friday-memory/tests_memory`: target the memory package tests.
- `uv run pytest packages/friday-agent/tests_agent`: target the agent package tests.
- `uv run pytest packages/friday-runtime/tests_runtime`: target the runtime package tests.
- `uv run pytest tests/integration`: run top-level integration tests only.
- `uv run ruff check .`: lint with configured rules (`E`, `F`, `I`, `UP`, `B`, `SIM`).
- `uv run mypy packages tests main.py`: desired repo-wide type-check gate. This command may expose legacy debt; do not hide failures with broad suppressions.

When a repo-wide validation command fails because of unrelated legacy debt, report the failure and also run the narrowest meaningful validation for the files you changed.

## Coding Style & Naming Conventions
- Python 3.10+, 4-space indentation, snake_case for modules/functions, PascalCase for classes/dataclasses.
- Prefer explicit type hints, small functions, and side-effect-aware APIs.
- Use `friday-core` structured logging utilities when instrumenting runtime code.
- For runtime/config work, prefer Pydantic models for validated external input and dataclasses for simple internal structures. Current full-stack runtime configuration lives in `friday_runtime.config.RuntimeConfig`; `friday_cli.container.FridayConfig` is compatibility-oriented.
- Keep package boundaries explicit. Cross-package behavior should go through public modules, typed models, protocols, or runtime composition, not incidental implementation details.

## Testing Guidelines
- Framework: `pytest` with `pytest-asyncio`.
- Async tests must use `@pytest.mark.asyncio`.
- Name tests `test_*.py` and test functions `test_*`.
- Put package tests under `packages/<pkg>/tests_<pkg>` unless working in an existing test tree with a different local convention.
- Put cross-package integration coverage under `tests/integration` when it is genuinely integration-level.
- Add regression coverage for new behavior and edge cases, especially missing API keys, telemetry toggles, persistence paths, tool safety, memory lifecycle behavior, and cross-package contracts.
- Prefer focused tests first. Broaden to package-level or repo-level validation when the change affects shared interfaces, runtime boot, agent execution, memory storage, or tool registration.

## Commit & Pull Request Guidelines
- Use short, descriptive sentence-style commit messages.
- PRs should include: what changed, why, how to validate, package-boundary implications, and any config/env implications.
- Link relevant issues/specs and attach screenshots for UX-affecting changes.
- Call out known validation debt separately from new failures introduced by the change.

## Security & Configuration Tips
- Never commit secrets or local state: `.env`, `.friday/*`, `chroma_db/`, Chroma collections, transcript databases, provider keys, or local runtime data.
- Copy `.env.example` to `.env` for local development and set provider keys such as `OPENAI_API_KEY` only in local environment files or shell state.
- Common runtime knobs include `FRIDAY_LLM_MODEL`, `FRIDAY_CHROMA_PATH`, `FRIDAY_CHROMA_COLLECTION`, and `FRIDAY_TELEMETRY_ENABLED`.
- Telemetry is opt-in via `FRIDAY_TELEMETRY_ENABLED=true`; ensure endpoints are reachable before enabling telemetry in shared environments.
- Treat tool outputs and external content as untrusted. Preserve sanitization, provenance wrapping, quarantine behavior, and memory-storage safety when touching tool execution or ingestion paths.

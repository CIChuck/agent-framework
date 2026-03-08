# Repository Guidelines

## Repository Policy
- The canonical engineering policy for this repository is [docs/policies/repository-engineering-policy.md](docs/policies/repository-engineering-policy.md).
- All code changes must comply with that policy.
Priority operational rules for agents:
- Do not add `# mypy: ignore-errors` to source files under `packages/*/src` without an explicit waiver.
- Do not rely on `assert` as the sole enforcement mechanism for essential runtime invariants; use explicit exceptions.
- Prefer interface or contract fixes over repeated `cast(...)`.
- Cross-package contracts should use typed models or declared interfaces, not incidental implementation details.
- If a requested change conflicts with repository policy, stop and explain the conflict.

## Project Structure & Module Organization
- `packages/` contains workspace libraries. Core modules include `friday-core` (interfaces/config/logging), `friday-memory` (memory + Chroma), `friday-llm` (LiteLLM clients), and `friday-agent` (orchestration + tools). Supporting/runtime modules include `friday-cli`, `friday-sandbox`, `friday-tools`, `friday-mcp`, `friday-transcript`, `friday-optimization`, `friday-runtime`, `friday-speech`, `friday-telemetry`, `friday-finance`, and `friday-moltbook`.
- `packages/friday-cli/src` hosts runtime wiring (`container.py`, REPL/server hooks) and the Typer/FastAPI surface.
- `tests/` holds integration/lab/unit suites; each package has its own `tests_*` directory (for example `tests_memory`, `tests_cli`).
- `docs/` contains specs and plans; `main.py` is a thin entry point for quick smoke runs.

## Build, Test, and Development Commands
- `uv sync --all-extras`: install all dependencies (including dev extras) for the workspace.
- `uv run python main.py`: quick repository sanity check.
- `uv run pytest`: run package test suites configured by default (`packages/*/tests_*`).
- `uv run pytest tests/integration`: run integration tests only.
- `uv run pytest packages/friday-memory/tests_memory`: target a package’s tests.
- `uv run ruff check .`: lint with configured rules (E,F,I,UP,B,SIM).
- `uv run mypy packages tests main.py`: strict type checking.

## Coding Style & Naming Conventions
- Python 3.10+, 4-space indentation, snake_case for modules/functions, PascalCase for classes/dataclasses.
- Prefer explicit type hints; keep functions small and side-effect aware.
- Use `friday-core` structured logging utilities when instrumenting runtime code.
- For validation/config: use Pydantic models; simple configs may use dataclasses (see `FridayConfig`).

## Testing Guidelines
- Framework: `pytest` with `pytest-asyncio`.
- Async tests must use `@pytest.mark.asyncio`.
- Name tests `test_*.py` and `test_*` functions; place tests under `packages/<pkg>/tests_<pkg>` or top-level suites like `tests/integration`, `tests/lab`, and `tests/unit`.
- Add regression coverage for new behaviors and edge cases (e.g., missing API keys, telemetry toggles, persistence paths).

## Commit & Pull Request Guidelines
- Use short, descriptive sentence-style commit messages (see `git log`).
- PRs should include: what changed, why, how to validate (commands), and any config/env implications.
- Link relevant issues/specs and attach screenshots for UX-affecting changes.

## Security & Configuration Tips
- Never commit secrets or local state: `.env`, `.friday/*`, `chroma_db/`.
- Copy `.env.example` to `.env` and set `OPENAI_API_KEY`, `FRIDAY_LLM_MODEL`, `FRIDAY_CHROMA_PATH`, etc.
- Telemetry is opt-in via `FRIDAY_TELEMETRY_ENABLED=true`; ensure endpoints are reachable before enabling in shared environments.

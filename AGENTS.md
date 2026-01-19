# Repository Guidelines

## Project Structure & Module Organization
- `packages/` holds core libraries: `friday-core` (interfaces/config/logging), `friday-memory` (memory + Chroma context), `friday-llm` (LiteLLM clients), `friday-agent` (agent orchestration + tools), plus supporting modules (`friday-sandbox`, `friday-tools`, `friday-mcp`, `friday-transcript`, `friday-optimization`).
- `apps/friday-cli/src` contains the runtime wiring (`container.py`, REPL/server hooks) and Typer/FastAPI surface.
- `tests/` includes integration suites and `tests/lab` experiments; each package keeps its own `tests/` directory.
- `docs/` captures specifications and plans; `main.py` is a thin entry point for quick smoke runs.

## Setup & Tooling
- Python 3.10+ required; dependencies managed with `uv` workspace (`pyproject.toml`, `uv.lock`).
- Install everything (including dev extras) with `uv sync --all-extras`.
- Copy `.env.example` to `.env` and set `OPENAI_API_KEY`, `FRIDAY_LLM_MODEL`, `FRIDAY_CHROMA_PATH`, etc.; keep secrets out of git.

## Build, Test, and Development Commands
- `uv run pytest` runs unit/integration tests across packages; target suites with `uv run pytest tests/integration` or `packages/friday-memory/tests`.
- `uv run ruff check .` enforces lint rules (E,F,I,UP,B,SIM; line length 88 via formatter).
- `uv run mypy packages apps tests` runs strict typing (no untyped defs, warn on `Any`).
- `uv run python main.py` is a quick repo sanity check; prefer exercising features via package-level tests.

## Coding Style & Naming Conventions
- 4-space indent, snake_case for modules/functions, PascalCase for classes/dataclasses; prefer explicit type hints everywhere.
- Keep functions small and side-effect aware; use structured logging utilities from `friday-core` when instrumenting runtime code.
- When adding config or DTOs, use pydantic models for validation; favor dataclasses for simple configs (see `FridayConfig`).

## Testing Guidelines
- Default to `pytest` with `pytest-asyncio`; mark async tests with `@pytest.mark.asyncio` when needed.
- Name tests `test_*.py`/`test_*` functions and place near the code under `packages/<pkg>/tests` or `tests/integration` for cross-package flows (memory + LLM).
- Add regression coverage for new behaviors and edge cases (e.g., missing API keys, telemetry toggles, persistence paths).

## Commit & Pull Request Guidelines
- Commit messages follow short, descriptive sentences (see `git log`); keep scope focused.
- PRs should include: what changed, why, how to validate (commands), and any config/env implications; link issues/specs when relevant and attach screenshots for UX-affecting changes.

## Security & Operational Notes
- Do not commit API keys or local state (`.env`, `.friday/*`, `chroma_db/`); prefer environment variables.
- Telemetry is opt-in (`FRIDAY_TELEMETRY_ENABLED=true`); ensure endpoints are reachable before enabling in shared environments.

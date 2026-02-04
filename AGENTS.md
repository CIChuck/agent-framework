# Repository Guidelines

## Project Structure & Module Organization
- `packages/` contains core libraries: `friday-core` (interfaces/config/logging), `friday-memory` (memory + Chroma), `friday-llm` (LiteLLM clients), `friday-agent` (agent orchestration + tools), plus supporting modules like `friday-sandbox`, `friday-tools`, `friday-mcp`, `friday-transcript`, and `friday-optimization`.
- `apps/friday-cli/src` hosts runtime wiring (`container.py`, REPL/server hooks) and the Typer/FastAPI surface.
- `tests/` holds integration suites and `tests/lab` experiments; each package also has its own `tests/` directory.
- `docs/` contains specs and plans; `main.py` is a thin entry point for quick smoke runs.

## Build, Test, and Development Commands
- `uv sync --all-extras`: install all dependencies (including dev extras) for the workspace.
- `uv run python main.py`: quick repository sanity check.
- `uv run pytest`: run the full test suite.
- `uv run pytest tests/integration`: run integration tests only.
- `uv run pytest packages/friday-memory/tests_memory_memory`: target a package’s tests.
- `uv run ruff check .`: lint with configured rules (E,F,I,UP,B,SIM).
- `uv run mypy packages apps tests`: strict type checking.

## Coding Style & Naming Conventions
- Python 3.10+, 4-space indentation, snake_case for modules/functions, PascalCase for classes/dataclasses.
- Prefer explicit type hints; keep functions small and side-effect aware.
- Use `friday-core` structured logging utilities when instrumenting runtime code.
- For validation/config: use Pydantic models; simple configs may use dataclasses (see `FridayConfig`).

## Testing Guidelines
- Framework: `pytest` with `pytest-asyncio`.
- Async tests must use `@pytest.mark.asyncio`.
- Name tests `test_*.py` and `test_*` functions; place tests under `packages/<pkg>/tests` or `tests/integration`.
- Add regression coverage for new behaviors and edge cases (e.g., missing API keys, telemetry toggles, persistence paths).

## Commit & Pull Request Guidelines
- Use short, descriptive sentence-style commit messages (see `git log`).
- PRs should include: what changed, why, how to validate (commands), and any config/env implications.
- Link relevant issues/specs and attach screenshots for UX-affecting changes.

## Security & Configuration Tips
- Never commit secrets or local state: `.env`, `.friday/*`, `chroma_db/`.
- Copy `.env.example` to `.env` and set `OPENAI_API_KEY`, `FRIDAY_LLM_MODEL`, `FRIDAY_CHROMA_PATH`, etc.
- Telemetry is opt-in via `FRIDAY_TELEMETRY_ENABLED=true`; ensure endpoints are reachable before enabling in shared environments.

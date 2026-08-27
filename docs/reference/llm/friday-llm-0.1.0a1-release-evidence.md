# Friday LLM 0.1.0a1 Release Evidence

## Decision

- Implementation state: complete on 2026-08-27.
- Artifact state: built and validated locally; do not rebuild for upload.
- Release state: **HOLD**.
- Holds: the mandatory live LM Studio/Qwen lane has no available target, and
  TestPyPI/PyPI publication has not been authorized.
- Publication, tag, and PyPI URL: none.

This distinction is intentional. Deterministic wire capture proves the JSON
emitted through LiteLLM; it does not prove that LM Studio accepted the controls
or that the loaded model changed behavior.

## Release Identity

- Distribution: `friday-framework-llm==0.1.0a1`
- Import package: `friday_llm`
- Branch: `feature/friday-llm-reasoning-controls`
- Python requirement: `>=3.10`
- LiteLLM: exact `1.94.1`
- Internal dependencies: exact `friday-framework-core==0.1.0a0` and
  `friday-framework-telemetry==0.1.0a0`
- Supported release-one profile: LiteLLM OpenAI-compatible Chat Completions,
  LM Studio serving engine, explicit Qwen3.8 family and model revision.

LiteLLM `1.98.0` was investigated and rejected because it directly imports
`typing.NotRequired`, which is unavailable on Python 3.10. LiteLLM `1.94.1`
imports at the declared floor and preserves the required final wire shape.

## Focused Validation

The final package gate:

```text
LITELLM_LOCAL_MODEL_COST_MAP=True uv run pytest packages/friday-llm/tests_llm -q
165 passed, 8 skipped, 9 warnings

uv run ruff check packages/friday-llm scripts/check-package-metadata.py scripts/check-package-artifacts.py
All checks passed!

uv run mypy packages/friday-llm/src packages/friday-llm/tests_llm scripts/check-package-metadata.py scripts/check-package-artifacts.py
Success: no issues found in 35 source files

uv lock --check
Resolved 203 packages
```

The eight skips are the opt-in live-provider matrix. The warnings are upstream
LiteLLM/Pydantic deprecations and LiteLLM async logging-worker warnings; Friday
does not suppress them by mutating LiteLLM process globals.

Clean Python matrix results, each using the exact locked package inputs:

| Python | Result |
| --- | --- |
| 3.10.19 | 165 passed, 8 skipped, 4 warnings |
| 3.11.14 | 165 passed, 8 skipped, 4 warnings |
| 3.12.12 | 165 passed, 8 skipped, 9 warnings |
| 3.13.10 | 165 passed, 8 skipped, 9 warnings |

## Downstream And Repository Baseline

Validation-only consumers were not edited.

| Scope | Result |
| --- | --- |
| Friday Memory | 678 passed, 1 skipped |
| Friday Runtime focused compatibility | 42 passed |
| Top-level integration | 7 passed |
| Friday Chat | 373 passed, 2 failed |
| Friday Agent | 198 passed, 9 failed |

The two Friday Chat failures are PTY clear-screen assertions in untouched
display code. The nine Friday Agent failures pass a `MagicMock.model` into an
untouched `InteractionTurn.model_name` string field. Re-running the affected
scopes reproduced them independently of Friday LLM tests.

The configured root command stops during collection because both Friday Chat
and Friday CLI contain a top-level `test_display` module:

```text
uv run pytest -q
ERROR packages/friday-cli/tests_cli/test_display.py: import file mismatch
```

The non-mutating fallback `uv run pytest -q --import-mode=importlib` completed
with `2107 passed, 9 skipped, 15 failed`. In addition to the 11 failures above,
it exposed two order/context-sensitive runtime DI tool-registration failures
and two optional document-reader expectation failures in untouched packages.

Repository-wide Ruff reports 12 existing errors outside Friday LLM. The desired
repo-wide mypy command stops on the same duplicate `test_display` module name.
Focused Friday LLM Ruff and mypy gates are green.

## Artifact Evidence

Build directory:
`dist/friday-framework-llm-0.1.0a1/`

| Artifact | SHA-256 |
| --- | --- |
| `friday_framework_llm-0.1.0a1-py3-none-any.whl` | `527828b85fda1fc2c4d22d24fac3295cf3759eb86b39d649f0075de2f8a0d704` |
| `friday_framework_llm-0.1.0a1.tar.gz` | `c0e2a63330fc7449936399fe5d9f8d0be5736cba62d033c7e0d17bd7e19576ac` |

Completed checks:

- package metadata, license, README, project URLs, universal wheel tag, and
  exact internal/external dependencies;
- wheel and sdist content allowlist checks, including suspicious path and
  token-pattern canaries;
- `twine check` on both artifacts;
- clean-venv wheel install from the versioned artifact directory, import,
  typed fake-transport request, legacy constructor, and `pip check`;
- independent wheel rebuild from the sdist followed by the same clean-venv
  smoke and `pip check`.

The clean installs resolved the already-published Core and Telemetry `0.1.0a0`
dependencies successfully.

## Live Evidence Hold

The bounded live matrix is implemented in
`packages/friday-llm/tests_llm/test_live_lmstudio.py` and is disabled unless
`FRIDAY_LLM_LIVE=1` is set. On 2026-08-27:

```text
curl --max-time 2 http://127.0.0.1:1234/v1/models
curl: (7) Failed to connect to 127.0.0.1 port 1234
```

No live tests were run, and no model-acceptance or behavioral-effect claim is
made. To clear this hold, load the exact target model, record the environment
fingerprint required by the tactical plan, run the opt-in matrix, and attach
the sanitized results without prompts or reasoning text.

## Authorized Next Gate

After the live lane passes, obtain separate authorization for TestPyPI. Upload
these exact local artifacts, verify their hashes and clean installation, and
only then request separate production-PyPI authorization. Create a release tag
only after post-publication verification succeeds.

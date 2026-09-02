# Friday Framework Typed LLM Execution Log

- Status: Implementation complete; release candidate committed and under review
- Approval date: 2026-08-28
- Branch: `feature/friday-framework-typed-llm-adoption`
- Candidate cohort: `0.1.0a2`
- Parent plan: [Friday Framework typed LLM adoption plan](friday-framework-typed-llm-adoption-plan.md)
- Model library specification: [Friday model library technical specification](friday-model-library-technical-spec.md)

## Baseline

- Commit: `60a2925`
- Local branch created from `master` and `origin/master` at the same commit.
- Existing user changes, configuration backup, unrelated documents, and local
  state were preserved.
- Focused baseline command:

  ```text
  .venv/bin/pytest -q packages/friday-llm/tests_llm \
    packages/friday-runtime/tests_runtime \
    packages/friday-chat/tests_chat/test_llm_config_migration.py \
    packages/friday-chat/tests_chat/test_llm_adapter_migration.py \
    packages/friday-chat/tests_chat/compat/test_config_compatibility.py
  ```

- Result: `258 passed, 8 skipped, 11 warnings` in 18.52 seconds.
- Skips are opt-in live tests. Warnings are existing third-party LiteLLM
  Pydantic deprecations and asynchronous logging cleanup warnings.

## Initial Inventory

- Production direct `LiteLLMService(...)` constructors outside Friday LLM: 13.
- Production direct `LiteLLMEmbeddingService(...)` constructors outside Friday
  LLM: 6.
- Production legacy `.chat_completion(...)` call sites outside Friday LLM: 22.
- Primary construction owners: Friday Runtime, Friday Chat, Friday Memory
  maintenance/ingestion helpers, and Friday Chat reorganization.
- Injected legacy callers: Friday Agent, Friday Memory consumers, Friday Tools
  code generation, and Friday Chat compatibility adapters.

Counts are a migration baseline, not an assertion that every call must acquire
a direct Friday LLM dependency. Documentation examples inside Friday LLM and
fallback constructors used only by examples remain separately classified.

## Workstream Status

| Workstream | Status | Evidence |
| --- | --- | --- |
| FW-LLM-00 baseline and inventory | Complete | Focused baseline and call-site inventory above. |
| FW-LLM-01 shared construction/model library | Complete | Strict catalog, bindings, redacted service specs, pure resolvers, and service factories are public and tested. |
| FW-LLM-02 capability profiles | Complete | Explicit target composition and pre-I/O control validation remain owned by Friday LLM; examples claim only registered controls. |
| FW-LLM-03 Core boundary | Complete | Core protocol is compatibility-only; the typed public protocol lives in Friday LLM without a Core-to-LLM dependency. |
| FW-LLM-04 Runtime | Complete | Bounded local loader, relative path policy, resolved specs, canonical DI factories, and legacy compatibility are tested. |
| FW-LLM-05 Memory | Complete | Typed completion helper covers extraction, routing, consolidation, compaction, synthesis, fact checking, lifecycle, and large-file processing. |
| FW-LLM-06 Agent and Tools | Complete | Agent and code-generation requests use typed boundaries with isolated legacy adapters; reasoning is excluded from persisted prompt snapshots. |
| FW-LLM-07 Friday Chat | Complete | Primary, extraction, routing, compaction, maintenance, embedding, and smart-file roles use named services from one catalog. |
| FW-LLM-08 boundary packages | Complete | All 17 distributions and their exact internal pins are `0.1.0a2`; the lockfile is synchronized. |
| FW-LLM-09 compatibility-only audit | Complete | AST-based checked allowlists prevent new direct constructors or legacy completion calls outside named compatibility paths. |
| FW-LLM-10 documentation/compatibility | Complete | Repository and packaged examples, model catalog, README guidance, `.env.example`, diagnostics, and release helpers are synchronized. |
| FW-LLM-11 deterministic validation | Complete | Package, wire, type, lint, metadata, artifact, checksum, and clean-install evidence is recorded below. |
| FW-LLM-12 candidate/release | Candidate complete | Local artifacts are built and validated. Push, PR, tag, PyPI upload, and live-provider testing remain separate authority gates. |

## Implemented Contract

- Friday LLM exports strict immutable catalog and service models, a
  provider-independent `TypedLLMClient`, pure chat/embedding resolvers, and
  `from_spec` factories. Resolution validates kind, route/target identity,
  credential references, capability support, and merged generation controls
  before provider I/O.
- Runtime and Friday Chat load `friday.model-library/v1` from a bounded local
  YAML file relative to the referencing configuration. Duplicate keys,
  aliases, merge keys, custom tags, unsafe URLs, excessive size/depth/node
  counts, unresolved selected credentials, and partial canonical sections fail
  closed.
- Credential definitions contain environment-variable names only. Resolved
  secrets use `SecretStr`; validation errors and model representations do not
  echo secret values.
- The repository and packaged Friday Chat examples share one provider key per
  endpoint (`FRIDAY_LLM_API_KEY` and `FRIDAY_OPENROUTER_API_KEY`) and bind all
  LLM roles by name. Per-role credentials remain available for deployments
  that require least-privilege provider keys.
- Operation-owned overrides retain highest precedence. Canonical extraction,
  passage routing, and smart-file composition no longer overwrite role-profile
  temperature, token, or timeout defaults with hidden legacy defaults.
- Hidden reasoning may be retained only in bounded in-memory provider replay.
  Structured parsing uses final content only, and persisted Agent/Chat traces
  exclude reasoning content.
- Legacy inline construction and `.chat_completion()` remain available only in
  the `0.1.x` compatibility window and emit migration diagnostics or
  deprecation warnings at their isolated boundaries.

## Candidate Validation

### Static and contract checks

- Focused Ruff validation: passed for all changed source, tests, and release
  helper paths.
- Repository-configured mypy is blocked before project analysis by the installed
  NumPy stub using Python 3.12 type-statement syntax while the repository target
  remains Python 3.10.
- Focused mypy with the actual Python 3.13 validation interpreter: `Success: no
  issues found in 11 source files`.
- Metadata validator: all 17 `pyproject.toml` files passed version, license,
  author, README, URL, wheel-selection, and exact internal-pin checks.
- The boundary audit passes and fixes the exact allowed constructor and legacy
  call inventory in `tests/integration/test_typed_llm_boundary_audit.py`.

### Deterministic tests

- Friday LLM: `182 passed, 8 skipped`; skips are opt-in live-provider tests.
- Friday Runtime: `50 passed`.
- Friday Memory: `680 passed, 1 skipped`.
- Friday Agent: `209 passed`.
- Friday Tools: `233 passed, 2 deselected`; see baseline debt below.
- Friday Chat: `423 passed, 5 skipped, 3 deselected`; see baseline debt below.
- Remaining package suites: Friday CLI `155`, Core `107`, MCP `31`, Moltbook
  `4`, Sandbox `38`, Speech `15`, and Telemetry `53` passed.
- Experiment suites: `18 passed` across agent quality, prompt/transcript audit,
  provider-memory smoke, and workflow-artifact smoke.
- Total independently executed green tests: `2198 passed, 14 skipped`.
- The root one-shot pytest command has a pre-existing collection collision
  between Friday Chat and Friday CLI modules both named `test_display.py`;
  package suites were therefore run in isolated pytest processes.

### Live-provider validation

- On 2026-09-02, the opt-in Friday LLM and Friday Chat live suites ran against
  LM Studio at the allowlisted loopback endpoint using `qwen3.8-27b-mlx` with
  revision `lmstudio-community/Qwen3.8-27B-MLX-8bit`.
- Result: `17 passed, 21 warnings` in 60.16 seconds. Coverage included provider
  default, disabled, and enabled reasoning profiles; non-streaming and
  streaming completion; forced and streamed tool calls; Friday Chat controls;
  and a bounded turn-processing flow.
- A separate live smoke loaded `models-config.example.yaml`, resolved the
  `qwen38_chat_local` profile, and completed successfully with `finish=stop`.
- A second catalog-resolved live smoke used `nomic_embedding_local` and returned
  a 768-dimensional embedding.
- No cloud-provider request was made and no provider credential was persisted.

### Reproduced baseline debt

- Two Friday Tools tests named `*_missing_dependency` create malformed DOCX/XLSX
  files but assert only missing-dependency text. They fail when the optional
  readers are installed because the correct error is `File is not a zip file`.
  The typed code-generation and smart-file changes do not touch those readers.
- Three Friday Chat PTY tests fail independently of the LLM migration on this
  macOS environment: Rich emits no expected clear-screen bytes, and one bounded
  progress subprocess produces no PTY output before its fixed deadline. Their
  non-PTY command and configuration assertions pass; the failures were
  reproduced individually outside the sandbox.
- Third-party LiteLLM/Pydantic and asynchronous logging warnings remain.

### Artifacts

- `uv build --all-packages` produced 17 wheels and 17 source distributions in
  `dist/friday-package-cohort-0.1.0a2`.
- `scripts/check-package-artifacts.py` validated all 34 artifacts, including
  exact pins, required packaged Friday Chat YAML resources, metadata, and
  suspicious-path/secret checks.
- A clean temporary-environment install of `friday-chat==0.1.0a2` from the
  candidate directory passed imports, `pip check`, console `--help`/`--version`,
  packaged catalog loading with zero diagnostics, and the typed fake-transport
  smoke without provider I/O.
- The verified candidate checksums are recorded in
  [friday-package-cohort-0.1.0a2-artifact-sha256.txt](friday-package-cohort-0.1.0a2-artifact-sha256.txt).

## Repository Handoff

- Candidate commit: `2f71778` (`Adopt typed LLM configuration across Friday
  packages`).
- Remote branch: `origin/feature/friday-framework-typed-llm-adoption`.
- Pull request: [#4](https://github.com/CIChuck/agent-framework/pull/4), opened
  against `master` on 2026-09-02.
- The unrelated Friday Chat handoff edit, reference documents, and local
  pre-migration config backup were not included in the candidate commit.

## Remaining Authority Gates

Merge, tag creation, and PyPI upload have not been performed. They remain
separate authority gates under the parent plan.

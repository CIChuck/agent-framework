# Build Plan: Friday Framework PyPI Preparation

**Status:** Draft
**Target:** Publishable Friday framework package set
**Related Plan:** [friday-framework-uvx-distro.md](friday-framework-uvx-distro.md)
**Objective:** Prepare the Friday monorepo for PyPI publication while preserving
the ability to run Friday Chat and future Friday Web through `uvx`.

---

## 1. Conversation Snapshot

This plan memorializes the PyPI-preparation discussion. It is a living working
document and should evolve as packaging decisions become implementation tasks.

User goals:

- Publish the Friday agent framework on PyPI.
- In a perfect world, bundle the framework so users can install one high-level
  package.
- Let users run Friday Chat through:

```bash
uvx friday-chat
```

- Let users eventually run browser-based Friday Chat through:

```bash
uvx friday-web
```

Planning guardrails:

- Do not perform destructive actions during this review.
- Do not build packages as part of this planning pass.
- Discuss and document the process before changing packaging implementation.
- Keep API keys in environment variables, not in editable config files or
  published package artifacts.

## 2. Recommended Distribution Shape

Use a set of real PyPI distributions rather than trying to publish the whole
monorepo as one physical wheel.

Important PyPI naming constraint:

- The bare `friday` distribution name is already taken on PyPI.
- The `friday-agent` distribution name is already taken on PyPI.
- The generic `agent-framework` distribution name is also taken and should not
  be used for this project.
- Public distribution names should therefore use a project-specific namespace,
  with `friday-framework` as the current preferred candidate.

Recommended model:

| Distribution | Purpose | Primary use |
| --- | --- | --- |
| `friday-chat` | Terminal app package | `uvx friday-chat` |
| `friday-web` | Future browser app package | `uvx friday-web` |
| `friday-framework` | Convenience meta-package | `pip install friday-framework` |
| `friday-framework-core`, `friday-framework-memory`, etc. | Component libraries | Installed as dependencies |

Rationale:

- `uvx friday-chat` works best when the PyPI distribution name matches the
  command users run.
- A `friday-framework` meta-package can still provide a one-command framework
  install for users who want all packages.
- Component packages remain independently versioned, testable, and reusable.
- Heavy capabilities can move behind extras instead of forcing every user to
  install speech, sandboxing, MCP, telemetry, optimization, or document tooling.

Non-goal:

- Do not require the primary user path to be:

```bash
uvx --from friday friday-chat
```

That can be supported later if useful, but it is a less direct default
experience than publishing runnable app distributions.

## 3. Current Repo Observations

These observations came from the planning review and should be revalidated
before implementation.

- The root project is named `friday-framework` in `pyproject.toml`.
- The root project has `[project]` metadata and is intended to publish as a
  pure convenience/meta-package.
- Workspace package projects generally use `hatchling` and package-specific
  `pyproject.toml` files.
- Component package distribution names now use the `friday-framework-*`
  namespace while import packages and source folders remain `friday_*` and
  `packages/friday-*`.
- `packages/friday-chat/pyproject.toml` already declares:

```toml
[project.scripts]
friday-chat = "friday_chat.cli:app"
```

- A root MIT `LICENSE` file has been added and should be included in published
  artifacts.
- Development tooling such as `mypy` has been kept out of root runtime
  dependencies.
- `friday-optimization` needs package-shape review: its `pyproject.toml`
  declares wheel packages as `src/friday_optimization`, while the source tree
  observed during planning is `src/friday_opt`.
- Speech, finance, sandbox, moltbook, MCP, document readers, spreadsheets, and
  Langfuse support are modeled as extras instead of default root dependencies.

## 4. Configuration And Runtime State Model

PyPI and `uvx` installs must treat installed package code as read-only and
disposable.

Required model:

```text
installed package environment:
  package code
  package resource templates
  bundled web static assets

user-controlled locations:
  config.yaml
  cli-config.yaml
  future web-config.yaml
  transcripts
  memory/vector/chroma state
  graph state
  caches
  logs
```

Configuration lookup should align with
[friday-framework-uvx-distro.md](friday-framework-uvx-distro.md):

1. explicit `--config`,
2. `FRIDAY_CONFIG`,
3. user config directory,
4. package defaults or package templates.

Default user paths should be standardized before publication, likely using
XDG-compatible paths or `platformdirs`.

Secrets:

- API keys remain environment variables.
- Config templates may reference environment-variable placeholders such as
  `${OPENAI_API_KEY}`.
- `init` and `doctor` commands must not print secrets unredacted.
- Published templates must not contain local user paths, test secrets, or
  development-only assumptions.

## 5. Publication Preparation Task Plan

### Task 1: Define The PyPI Package Matrix

Goal:

- Decide which distributions are included in the first publication wave.

Work:

- Classify packages as required runtime, optional runtime, application package,
  or internal/deferred.
- Decide whether `friday-optimization` is corrected before first publication or
  deferred from the first wave.
- Decide whether `friday-framework` is a meta-package only, or also exposes
  console scripts for convenience.
- Define extras such as `speech`, `mcp`, `sandbox`, `telemetry`, `finance`,
  `optimization`, `web`, and `all`.

Current naming decision points:

- Use `friday-framework` as the candidate top-level PyPI distribution name
  instead of `friday`.
- Use `friday-framework-*` as the candidate component package namespace.
- Use `friday-chat` and `friday-web` as the application distribution names to
  preserve the direct `uvx friday-chat` and `uvx friday-web` user experience.
- Keep Python import package names such as `friday_core`, `friday_memory`, and
  `friday_chat` unless there is a later reason to rename imports.
- Before the first release, perform a final PyPI name availability and name
  ownership check for every intended distribution, especially `friday-chat` and
  `friday-web`.

Current Task 1 decision:

- Publish application packages as `friday-chat` and `friday-web`.
- Publish the top-level convenience/meta package as `friday-framework`.
- Publish component packages under the `friday-framework-*` distribution
  namespace unless a package-specific reason requires a narrower exception.
- Prioritize `uvx friday-chat` for the first publication wave.
- Publish only the packages needed for Friday Chat in the first wave.
- Defer `friday-optimization` from the first publication wave until its package
  path mismatch is fixed.

First-wave package matrix:

| Role | Public distribution name | Current source package | Notes |
| --- | --- | --- | --- |
| App | `friday-chat` | `packages/friday-chat` | Required for `uvx friday-chat` |
| Framework meta-package | `friday-framework` | root project | Publish after component packages; no console scripts by default unless later decided |
| Core library | `friday-framework-core` | `packages/friday-core` | Required by most packages |
| Telemetry library | `friday-framework-telemetry` | `packages/friday-telemetry` | Required by `friday-core`, `friday-llm`, and runtime stack |
| LLM library | `friday-framework-llm` | `packages/friday-llm` | Required by memory/runtime/chat |
| Transcript library | `friday-framework-transcript` | `packages/friday-transcript` | Required by runtime/chat |
| Memory library | `friday-framework-memory` | `packages/friday-memory` | Required by agent/runtime/chat |
| Agent library | `friday-framework-agent` | `packages/friday-agent` | Required by runtime/chat |
| Runtime library | `friday-framework-runtime` | `packages/friday-runtime` | Required by chat |
| CLI support library | `friday-framework-cli` | `packages/friday-cli` | Required by chat |
| Tools library | `friday-framework-tools` | `packages/friday-tools` | Required by chat; optional integrations live behind extras |
| Speech library | `friday-framework-speech` | `packages/friday-speech` | Optional extra |
| Finance library | `friday-framework-finance` | `packages/friday-finance` | Optional extra |
| Sandbox library | `friday-framework-sandbox` | `packages/friday-sandbox` | Optional extra |
| Moltbook library | `friday-framework-moltbook` | `packages/friday-moltbook` | Optional extra |

Deferred package matrix:

| Role | Candidate distribution name | Current source package | Reason |
| --- | --- | --- | --- |
| MCP library | `friday-framework-mcp` | `packages/friday-mcp` | Defer until MCP client/runtime integration plan is implemented or intentionally included as optional |
| Optimization library | `friday-framework-optimization` | `packages/friday-optimization` | Defer until `src/friday_opt` vs `src/friday_optimization` mismatch is resolved |
| Web app | `friday-web` | future package | Publish when the browser-based Friday Chat package exists |

Task 2 dependency cleanup result:

- Speech, finance, sandbox, and moltbook are now extras instead of default
  dependencies for root, chat, and tools metadata. They remain publishable
  first-wave packages if those extras are included in the first release.

Acceptance:

- The first publishable package set is explicit.
- No package with known broken package metadata is accidentally included.

### Task 2: Normalize Package Metadata

Goal:

- Make each published distribution acceptable for PyPI and understandable to
  users.

Work:

- Add or verify build-system metadata for the root `friday-framework`
  meta-package if it will be published.
- Add a root license file and ensure package metadata references it correctly.
- Normalize readme, description, authors, maintainers, classifiers, keywords,
  and project URLs across packages.
- Separate runtime dependencies from development dependencies.
- Move heavyweight or provider-specific dependencies into extras where
  practical.
- Verify that every wheel package path matches the actual import package.

Acceptance:

- Every included distribution has coherent metadata.
- The root `friday-framework` package can function as a clean meta-package.
- Application distributions retain clear console-script entry points.

Current Task 2 decisions and actions:

- Root distribution metadata uses `name = "friday-framework"`.
- Component package distribution metadata uses `friday-framework-*` names.
- Application distribution metadata keeps `name = "friday-chat"`; future web
  app metadata should use `name = "friday-web"`.
- Python import packages remain unchanged, for example `friday_core`,
  `friday_memory`, and `friday_chat`.
- Repository package folders remain unchanged, for example
  `packages/friday-core` and `packages/friday-memory`.
- The root `friday-framework` distribution is a pure meta-package with no
  console scripts.
- `Friday Team` is used as the package author across current distributions.
- Optional/heavy capabilities are moved behind extras in root, `friday-chat`,
  and `friday-framework-tools` metadata.
- `uv.lock` has been updated to reflect the renamed workspace distributions.

Distribution-name convention:

- `project.name` is the public PyPI distribution name and is used in dependency
  declarations.
- `tool.hatch.build.targets.wheel.packages` points to the Python import package
  and does not need to match the PyPI distribution name.
- Source folders under `packages/` are repository organization, not public PyPI
  distribution names.

### Task 3: Establish Versioning And Release Order

Goal:

- Avoid dependency-resolution failures when publishing interdependent workspace
  packages.

Work:

- Decide whether all Friday packages share one version or use independent
  package versions.
- Define dependency pins between Friday packages for published releases.
- Define the release order for component packages, app packages, and the root
  meta-package.
- Decide how pre-release versions are represented during TestPyPI rehearsal.

Acceptance:

- A deterministic package publication order exists.
- Published app packages resolve only against published compatible component
  versions.

Current Task 3 decisions and actions:

- Use lock-step versions for Friday packages for the first publication phase.
- Use exact internal pins for the first alpha release, for example
  `friday-framework-core==0.1.0`.
- Use pre-release versions such as `0.1.0rc1` for TestPyPI rehearsals, then use
  `0.1.0` for production PyPI if the rehearsal passes.
- If public PyPI name reservation is urgent, publish a minimal real-PyPI
  reservation build such as `0.1.0a0` before the clean `0.1.0` alpha. This
  reserves package names without consuming the final `0.1.0` release number.
- Publish leaf libraries first, then composed libraries, then app packages, then
  the root meta-package last.
- Current package metadata and `uv.lock` have been updated for exact
  `0.1.0` internal pins.

Component-upgrade exception for Friday LLM:

- The reasoning-and-sampling-controls upgrade is planned as the first
  independently versioned component update after the `0.1.0a0` name-reservation
  release.
- Its approved target is `friday-framework-llm==0.1.0a1` while its published
  dependencies on `friday-framework-core==0.1.0a0` and
  `friday-framework-telemetry==0.1.0a0` remain unchanged unless implementation
  proves that either dependency contract must change.
- The root `friday-framework==0.1.0a0` meta-package and other `0.1.0a0`
  distributions do not automatically consume this component update. A later
  coordinated framework release may update their exact pins after downstream
  compatibility validation.
- This exception does not establish unrestricted independent versioning for all
  packages. Each later component-only release must document dependency impact,
  downstream validation, and whether a coordinated meta-package release is
  required.
- Release helpers must accept an explicit target version and package subset;
  hard-coded `0.1.0a0` whole-workspace validation is reservation evidence, not
  a valid release gate for this component update.
- The authoritative scope and gates for this exception are in
  [friday-llm-reasoning-controls-tactical-implementation-plan.md](../upgrades/friday-llm/friday-llm-reasoning-controls-tactical-implementation-plan.md).
- Implementation was approved on 2026-08-27 under the plan's scoped FridayV2
  freeze exception. TestPyPI and PyPI publication still require their own
  explicit approvals.
- Package implementation, deterministic tests, Python-version validation,
  live LM Studio/Qwen validation, artifact checks, and clean-install smokes
  completed on 2026-08-27. Release is held pending separate TestPyPI/PyPI
  authorization; see the
  [release evidence](../../reference/llm/friday-llm-0.1.0a1-release-evidence.md).

Coordinated `0.1.0a1` dependency-cohort decision:

- Friday Chat clean installation proved that the component-only exception is
  not a publishable downstream graph: immutable `0.1.0a0` packages retain exact
  pins to the old LLM and to packages that transitively require it.
- On 2026-08-28 the maintainer approved returning every current Friday
  distribution and every internal exact dependency to lock-step `0.1.0a1`.
- The coordinated cohort includes optional extras, MCP, Optimization, Friday
  Chat, and the root meta-package so no supported installation shape can pull a
  mixed `a0`/`a1` graph.
- Implementation and local validation are authorized. Registry uploads, live
  provider calls, tags, and pushes remain separately gated.
- The authoritative scope and release gates are in the
  [Friday package cohort plan](../upgrades/friday-packages/friday-package-cohort-0.1.0a1-plan.md).

First alpha release order:

1. `friday-framework-telemetry`
2. `friday-framework-transcript`
3. `friday-framework-sandbox`
4. `friday-framework-moltbook`
5. `friday-framework-core`
6. `friday-framework-finance`
7. `friday-framework-llm`
8. `friday-framework-speech`
9. `friday-framework-memory`
10. `friday-framework-agent`
11. `friday-framework-tools`
12. `friday-framework-runtime`
13. `friday-framework-cli`
14. `friday-chat`
15. `friday-framework`

Deferred release order additions:

- `friday-framework-mcp` can be inserted after `friday-framework-core` when MCP
  publication is intentionally included.
- `friday-framework-optimization` can be inserted after
  `friday-framework-memory` once its package-shape issue is fixed.
- `friday-web` should publish after its backend/runtime dependencies are
  published.

Future version-bump process:

1. Choose the target version and release type, for example `0.1.1`, `0.2.0`, or
   `0.2.0rc1`.
2. Update every Friday package `project.version` in root and package
   `pyproject.toml` files.
3. Update every internal Friday dependency pin to the same target version while
   the project uses lock-step exact pins.
4. Run `uv lock` to refresh `uv.lock`.
5. Run metadata validation: TOML parse, stale-name scan, `uv lock --check`, and
   `git diff --check`.
6. Run package tests and build/artifact checks from Task 4 before any
   publication.
7. Publish TestPyPI release candidates first, using the documented release
   order.
8. After TestPyPI install and `uvx` smoke checks pass, publish the production
   version to PyPI in the same order.
9. Tag the release after production validation passes.

Future dependency-policy option:

- Exact pins are best for the first alpha because they make the multi-package
  release deterministic. After the package boundaries stabilize, consider
  changing internal pins to compatible ranges such as `>=0.2.0,<0.3.0` for
  non-app libraries while keeping app packages more tightly pinned.

Public name-reservation process:

1. Temporarily set all package versions and internal Friday pins to the
   reservation version, currently `0.1.0a0`.
2. Build local artifacts and inspect them before uploading anything.
3. Publish only the packages needed to reserve the desired public names.
4. Upload to real PyPI, not TestPyPI, because TestPyPI does not reserve
   production names.
5. Publish in dependency order so exact pins can resolve.
6. After reservation succeeds, decide whether to keep the working tree at the
   reservation version until the follow-up alpha work is complete or bump
   forward to the next planned pre-release.

Current reservation-build run:

- Reservation version: `0.1.0a0`.
- Artifact directory: `dist/pypi-reservation-0.1.0a0/`.
- Built wheels and source distributions for all current workspace
  distributions:
  - `friday-framework`
  - `friday-chat`
  - `friday-framework-agent`
  - `friday-framework-cli`
  - `friday-framework-core`
  - `friday-framework-finance`
  - `friday-framework-llm`
  - `friday-framework-mcp`
  - `friday-framework-memory`
  - `friday-framework-moltbook`
  - `friday-framework-optimization`
  - `friday-framework-runtime`
  - `friday-framework-sandbox`
  - `friday-framework-speech`
  - `friday-framework-telemetry`
  - `friday-framework-tools`
  - `friday-framework-transcript`
- Fixed the `friday-framework-optimization` wheel package path from
  `src/friday_optimization` to `src/friday_opt` after the first build produced
  a metadata-only wheel.
- `twine check` passes for all artifacts. Most packages still warn about
  missing long descriptions; this is acceptable for a reservation build but
  should be fixed before the clean `0.1.0` alpha.
- During the 2026-07-21 rate-limit pause, package-local `README.md` files and
  `[project.urls]` metadata were added across all packages. The remaining
  unuploaded `0.1.0a0` artifacts were rebuilt and now pass `twine check`
  without long-description warnings.
- The four packages already uploaded to PyPI at `0.1.0a0` cannot be changed in
  place; their PyPI descriptions should be corrected by publishing a future
  `0.1.0a1` or `0.1.0` version after reservation is complete.
- Artifact leak scan found no obvious local state or secret path names such as
  `.env`, `.friday`, Chroma paths, transcript databases, local key files, or
  PyPI recovery-code filenames.
- Upload is blocked until real PyPI credentials are provided in the shell
  environment.
- Real PyPI upload began after credentials were provided through
  `scripts/pypi.sh`, which is ignored by `.gitignore`.
- PyPI accepted the first four new projects, then returned `429 Too Many
  Requests` while creating `friday-framework-core`. A later slower retry still
  received `429`, which indicates PyPI's new-project creation rate limit rather
  than a local build or credential failure.
- Retried `friday-framework-core` on 2026-07-21 with valid Twine credentials and
  the same reservation artifacts. PyPI still returned `429 Too Many Requests`,
  so the new-project rate limit had not yet reset or been lifted.
- Retried `friday-framework-core` again on 2026-07-21 after revalidating the
  remaining artifacts and `twine check` results. PyPI again returned `429 Too
  Many Requests` before accepting any new artifact, so no additional projects
  were published in this retry.
- Retried uploads at 2026-07-21 17:30 EDT. PyPI accepted
  `friday-framework-core`, `friday-framework-finance`, `friday-framework-llm`,
  and `friday-framework-speech`, then returned `429 Too Many Requests` while
  creating `friday-framework-mcp`.
- Retried uploads at 2026-07-22 18:30 EDT after validating the nine remaining
  artifacts. PyPI accepted `friday-framework-mcp`,
  `friday-framework-memory`, `friday-framework-agent`, and
  `friday-framework-tools`, then returned `429 Too Many Requests` while
  creating `friday-framework-optimization`.
- Retried uploads at 2026-07-23 17:41 EDT after validating the five remaining
  artifacts. PyPI returned `429 Too Many Requests` while creating
  `friday-framework-optimization`, before accepting any additional artifact.
- Retried `friday-framework-optimization` at 2026-07-23 18:00 EDT after
  validating the targeted artifacts. PyPI again returned `429 Too Many
  Requests` before accepting any additional artifact.
- Retried uploads at 2026-07-23 20:55 EDT after validating the five remaining
  artifacts. PyPI accepted `friday-framework-optimization`,
  `friday-framework-runtime`, `friday-framework-cli`, and `friday-chat`.
  Uploading `friday-framework` first hit a DNS failure during Twine's
  `--skip-existing` preflight, then reached PyPI without `--skip-existing` and
  returned `429 Too Many Requests` before accepting the final meta-package.
- Fully uploaded reservation projects so far:
  - `friday-framework-telemetry`
  - `friday-framework-transcript`
  - `friday-framework-sandbox`
  - `friday-framework-moltbook`
  - `friday-framework-core`
  - `friday-framework-finance`
  - `friday-framework-llm`
  - `friday-framework-speech`
  - `friday-framework-mcp`
  - `friday-framework-memory`
  - `friday-framework-agent`
  - `friday-framework-tools`
  - `friday-framework-optimization`
  - `friday-framework-runtime`
  - `friday-framework-cli`
  - `friday-chat`
- Remaining projects to upload after the PyPI new-project limit resets or is
  lifted:
  - `friday-framework`
- Resume uploads with `--skip-existing` for multi-package retries so already
  uploaded files are not treated as failures. The final `friday-framework`
  meta-package retry currently omits `--skip-existing` to avoid Twine's legacy
  PyPI JSON preflight lookup after that lookup hit a DNS failure.
- A non-secret helper script exists at
  `scripts/resume-pypi-reservation-upload.sh`. It expects `TWINE_USERNAME` and
  `TWINE_PASSWORD` to already be set in the environment, uploads the remaining
  package queue, and spaces attempts using `PYPI_UPLOAD_DELAY_SECONDS` with a
  default of 60 seconds.
- A metadata validation helper exists at `scripts/check-package-metadata.py`.
  It checks lock-step version metadata, MIT license metadata, author metadata,
  README presence, project URLs, wheel package selection, and exact internal
  Friday dependency pins.
- An artifact validation helper exists at `scripts/check-package-artifacts.py`.
  It checks artifact counts, wheel import-package contents, long-description
  metadata, project URL metadata, root metadata-only wheel behavior, and obvious
  local state or secret path names.
- A local install smoke helper exists at `scripts/smoke-install-artifacts.sh`.
  The default mode creates a temporary venv and installs `friday-chat` from the
  local artifact directory while allowing third-party dependencies to resolve
  from package indexes. The `--wheel-only` mode installs all Friday wheels into
  a temporary target directory with `--no-deps` and validates imports using an
  existing dependency environment.
- A strict no-index install smoke was attempted and correctly failed because
  the reservation artifact directory contains only Friday wheels, not
  third-party wheels such as `pydantic`.
- The default online-dependency install smoke was attempted but blocked by DNS
  failures while pip resolved third-party packages from PyPI.
- The wheel-only smoke passed using `.venv/bin/python` for runtime dependencies
  and local built wheels for Friday packages:

```bash
PYTHON_BIN=.venv/bin/python \
  INSTALL_PYTHON_BIN=python3 \
  scripts/smoke-install-artifacts.sh --wheel-only
```

- Focused artifact validation for the 13 remaining unuploaded packages passed:

```bash
python3 scripts/check-package-artifacts.py \
  dist/pypi-reservation-0.1.0a0 \
  --skip-base friday_framework_moltbook \
  --skip-base friday_framework_sandbox \
  --skip-base friday_framework_telemetry \
  --skip-base friday_framework_transcript
```

- Focused artifact validation for the nine packages remaining before the
  2026-07-22 retry passed:

```bash
python3 scripts/check-package-artifacts.py \
  dist/pypi-reservation-0.1.0a0 \
  --skip-base friday_framework_moltbook \
  --skip-base friday_framework_sandbox \
  --skip-base friday_framework_telemetry \
  --skip-base friday_framework_transcript \
  --skip-base friday_framework_core \
  --skip-base friday_framework_finance \
  --skip-base friday_framework_llm \
  --skip-base friday_framework_speech
```

- Focused artifact validation for the five packages remaining after the
  2026-07-22 retry passed:

```bash
python3 scripts/check-package-artifacts.py \
  dist/pypi-reservation-0.1.0a0 \
  --skip-base friday_framework_moltbook \
  --skip-base friday_framework_sandbox \
  --skip-base friday_framework_telemetry \
  --skip-base friday_framework_transcript \
  --skip-base friday_framework_core \
  --skip-base friday_framework_finance \
  --skip-base friday_framework_llm \
  --skip-base friday_framework_speech \
  --skip-base friday_framework_mcp \
  --skip-base friday_framework_memory \
  --skip-base friday_framework_agent \
  --skip-base friday_framework_tools
```

Reservation upload command shape:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD='pypi-...'

PYPI_UPLOAD_DELAY_SECONDS=60 scripts/resume-pypi-reservation-upload.sh
```

Post-upload checks:

```bash
uvx friday-chat==0.1.0a0 --help
uv run --isolated --with friday-framework==0.1.0a0 python -c "import friday_core; print('ok')"
```

### Task 4: Define Build And Artifact Checks

Goal:

- Specify build validation without running it during this planning pass.

Work:

- Define local artifact checks for future execution:

```bash
uv build --all-packages
twine check dist/*
```

- Verify wheel contents include only intended package files and resources.
- Verify source distributions do not include local runtime state, secrets,
  Chroma databases, transcript databases, caches, or generated memory state.
- Verify web static assets are bundled in the future `friday-web` wheel without
  requiring Node/npm at runtime.

Acceptance:

- There is a documented artifact validation checklist.
- The checklist explicitly protects against leaking local state or secrets.

### Task 5: Add First-Run App Contracts

Goal:

- Make PyPI-installed apps usable without editable checkouts.

Work:

- Define `friday-chat init`.
- Define `friday-chat doctor`.
- Define future `friday-web init`.
- Define future `friday-web doctor`.
- Ensure app templates are loaded from package resources, not repo-relative
  paths.
- Ensure diagnostics report resolved config paths, missing environment
  variables, and writable data directories.

Acceptance:

- A user can install and configure Friday apps from PyPI without cloning the
  repository.
- A failed first run gives actionable diagnostics without exposing secrets.

### Task 6: Rehearse On TestPyPI

Goal:

- Prove packaging and installation behavior before production PyPI publication.

Work:

- Publish candidate artifacts to TestPyPI.
- Install from TestPyPI into a clean environment.
- Run isolated smoke checks for imports and console scripts.
- Validate dependency resolution for all included distributions.
- Run `uvx` smoke checks against TestPyPI for runnable app packages.

Example future commands:

```bash
uvx --index-url https://test.pypi.org/simple/ friday-chat --help
uvx --index-url https://test.pypi.org/simple/ friday-chat doctor
uvx --index-url https://test.pypi.org/simple/ friday-chat init --help
```

Note:

- Exact `uvx` index and dependency-index flags should be verified when release
  automation is implemented.

Acceptance:

- TestPyPI install and `uvx` checks pass from a clean environment.
- Missing config and missing environment-variable cases fail clearly.

### Task 7: Publish To PyPI And Validate

Goal:

- Publish production artifacts only after TestPyPI proves the release path.

Work:

- Publish component packages in the documented order.
- Publish app packages after their component dependencies are available.
- Publish the root `friday-framework` meta-package last.
- Run production install checks.
- Run production `uvx` checks:

```bash
uvx friday-chat --help
uvx friday-chat doctor
uvx friday-chat init --help
```

- Add future checks when `friday-web` exists:

```bash
uvx friday-web --help
uvx friday-web doctor
```

Acceptance:

- Production PyPI packages install into a clean environment.
- `uvx friday-chat` can start without relying on repository-local files.
- Published packages have correct metadata, commands, dependency resolution,
  and first-run diagnostics.

### Task 8: Update User And Developer Guides

Goal:

- Make PyPI installation and release expectations visible in durable docs.

Work:

- Update `docs/guides/02-getting-started.md` with PyPI and `uvx` install
  paths once implemented.
- Update `docs/guides/10-configuration.md` with installed-app config lookup
  rules.
- Update `docs/guides/13-troubleshooting.md` with first-run install, config,
  and API-key diagnostics.
- Update `docs/guides/15-contributing.md` with packaging rules for future
  features.
- Add or update a release checklist if the repository maintains one.

Acceptance:

- User-facing docs match the actual published install path.
- Contributor docs warn against repo-relative runtime assumptions.

## 6. Future Considerations

- Decide whether `platformdirs` should be a core dependency for stable config,
  cache, and data paths.
- Decide whether package versions should be locked-step across the monorepo.
- Decide whether all packages should publish immediately or whether
  exploratory packages should remain internal.
- Decide how release automation should handle TestPyPI credentials, PyPI
  trusted publishing, and artifact attestations.
- Decide whether `friday-chat` should offer a command to print a fully redacted
  effective configuration for support.
- Decide whether `friday-web` should be local-only by default when launched from
  `uvx`, and what production deployment mode should require.

## 7. Completion Criteria

This plan is complete when:

- The initial publishable package set is explicit.
- Package metadata is normalized for all included distributions.
- Runtime config and data paths are independent of source checkouts.
- `friday-chat` and future `friday-web` have package-resource first-run
  templates.
- TestPyPI rehearsal passes in a clean environment.
- Production PyPI publication passes clean install and `uvx` smoke checks.
- User and contributor guides reflect the published distribution model.

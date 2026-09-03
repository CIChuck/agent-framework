# Build Plan: Friday Framework `uvx` Distribution

**Status:** Draft
**Target:** PyPI packaging and `uvx` distribution for Friday Chat and Friday Web
**Objective:** Let users run Friday apps with simple `uvx` commands while keeping
configuration, API keys, runtime data, and user-editable state outside
temporary tool environments.

---

## 1. Conversation Snapshot

This plan captures the initial distribution discussion and is intended to evolve
over time.

Goal:

- Users should be able to run Friday Chat or the future web version through
  `uvx` with minimal installation friction.

Desired commands:

```bash
uvx friday-chat
uvx friday-web
```

Optional top-level framework install:

```bash
pip install friday
```

or:

```bash
uv tool install friday-chat
uv tool install friday-web
```

Key decision:

- The `uvx` package environment is temporary and must not be treated as the
  place where user-editable configuration or runtime state lives.
- Config, secrets, Chroma/vector data, transcripts, caches, and logs must live
  in stable user-controlled locations.

## 2. Distribution Model

Recommended PyPI distribution shape:

| Distribution | Purpose | User command |
| --- | --- | --- |
| `friday-chat` | Terminal Friday Chat app | `uvx friday-chat` |
| `friday-web` | Browser-based Friday app | `uvx friday-web` |
| `friday` | Meta-package for full framework install | `pip install friday` |
| `friday-core`, `friday-memory`, etc. | Library/runtime component packages | Dependency packages |

Do not require users to run:

```bash
uvx --from friday friday-chat
```

That works only if the `friday` meta-package exposes the executable, but it is a
worse user experience than publishing app packages whose distribution names
match their commands.

## 3. `uvx` Runtime Model

`uvx` runs commands from Python packages in isolated tool environments. Those
environments are not the right place for editable app configuration.

Required model:

```text
temporary uvx environment:
  package code
  package templates
  bundled static assets

stable user-controlled locations:
  config.yaml
  cli-config.yaml
  web config
  transcripts
  vector/chroma state
  graph state
  caches
  logs
```

The app must behave as if package code is read-only and disposable.

## 4. Pre-Framework-Update Task Plan

Before making additional feature updates to the agent framework, complete this
lightweight distribution-readiness pass. The goal is not to publish yet; the
goal is to memorialize and enforce the invariants that future framework work
must preserve.

### Task 1: Add Distribution Readiness Policy

Goal:

- Make the `uvx`/PyPI distribution assumptions part of the repository's
  engineering rules.

Work:

- Add a "Distribution Readiness" section to
  `docs/reference/policies/repository-engineering-policy.md`.
- State that installed package code must be treated as read-only.
- State that user-editable config, runtime data, caches, transcripts, Chroma
  state, graph state, and logs must live outside package installation
  directories.
- State that package examples and templates must not contain literal secrets.
- State that future CLI/web features must not require repo-relative paths or
  editable installs for normal execution.

Acceptance:

- Future feature plans can cite one policy section for distribution constraints.
- The policy explicitly forbids writing mutable runtime state beside installed
  package source.

### Task 2: Define Config Resolution Contract

Goal:

- Establish the config lookup order before more features depend on config
  behavior.

Work:

- Document the intended config lookup order:
  1. explicit `--config`,
  2. `FRIDAY_CONFIG`,
  3. user config directory,
  4. package defaults/templates.
- Document default config files:
  - `~/.config/friday/config.yaml`
  - `~/.config/friday/cli-config.yaml`
  - future `~/.config/friday/web-config.yaml`
- Decide whether this contract initially lives in a guide, a build plan, or a
  small config module docstring.

Acceptance:

- New feature work has a stable config-resolution target.
- No future feature assumes `config.yaml` lives beside installed package code.

### Task 3: Define Runtime Data Path Contract

Goal:

- Prevent future features from writing state into repo or package paths.

Work:

- Document default user data/cache paths for transcripts, memory, Chroma,
  graph, exports, logs, and caches.
- Decide whether to use strict XDG paths or `platformdirs`.
- Add an explicit rule that test fixtures and repo examples are not runtime data
  locations for installed apps.

Acceptance:

- Runtime state placement is explicit before MCP, `friday.md`, web, or other
  features add more state.
- Future config examples point to stable user data paths or placeholders.

### Task 4: Prepare Config Templates As Package Resources

Goal:

- Stop treating repo-local example config files as the installed runtime source
  of truth.

Work:

- Identify the templates needed for `friday-chat init`:
  - main runtime config,
  - CLI display config.
- Decide package-resource locations, such as
  `packages/friday-chat/src/friday_chat/config_templates/`.
- Ensure templates use environment-variable placeholders for provider keys.
- Keep existing repo examples only as development/reference copies until
  implementation migrates them.

Acceptance:

- The package has a clear future location for config templates.
- No future code needs to read `packages/friday-chat/config.example.yaml` from
  source checkout paths at runtime.

### Task 5: Add Minimal `init` And `doctor` Contract

Goal:

- Reserve and define the first-run command surface before more CLI commands are
  added.

Work:

- Add a task or stub plan for `friday-chat init`.
- Add a task or stub plan for `friday-chat doctor`.
- Define what `doctor` checks:
  - resolved config path,
  - missing referenced environment variables,
  - writable data/cache directories,
  - redacted effective config,
  - optional provider connectivity only if explicitly enabled.

Acceptance:

- Future CLI and web work can rely on `init`/`doctor` as the supported first-run
  path.
- Secrets are never printed unredacted by diagnostic commands.

### Task 6: Add Packaging Metadata Cleanup Tasks

Goal:

- Keep future work aware of PyPI publishing requirements without doing the full
  release yet.

Work:

- Add tasks to normalize package metadata before publication:
  - root build backend,
  - license file,
  - readme metadata,
  - authors/classifiers,
  - runtime vs dev dependencies,
  - optional extras for heavyweight dependencies.
- Record known package-shape issues, including any package whose distribution
  metadata does not match its import package.

Acceptance:

- PyPI-readiness gaps are tracked before they block release.
- Future package additions follow the same metadata expectations.

### Task 7: Update Guides With Distribution Invariants

Goal:

- Make the distribution model visible to users and contributors before new
  feature work expands the surface area.

Work:

- Update `docs/guides/10-configuration.md` with config path and environment
  variable conventions.
- Update `docs/guides/15-contributing.md` with distribution-readiness rules for
  new features.
- Update `docs/guides/13-troubleshooting.md` with first-run config and API-key
  diagnostics.

Acceptance:

- User and contributor docs describe the `uvx` constraints before feature
  implementation depends on them.
- Guide updates are required before this pre-work is considered complete.

### Task 8: Validate The Planning/Policy Pass

Goal:

- Close the prerequisite pass without building or publishing packages.

Validation:

```bash
git diff --check -- docs/reference/policies docs/guides docs/planning
uv run ruff check packages/friday-chat
uv run pytest packages/friday-chat/tests_chat
```

Acceptance:

- The policy, guide, and build-plan changes are internally consistent.
- No package build or PyPI publication command is required for this prerequisite
  pass.

## 5. Configuration Resolution

`friday-chat` and `friday-web` should resolve config in this order:

1. Explicit CLI flag:

   ```bash
   uvx friday-chat --config ./config.yaml
   ```

2. Environment variable:

   ```bash
   FRIDAY_CONFIG=/path/to/config.yaml uvx friday-chat
   ```

3. User config directory:

   ```text
   ~/.config/friday/config.yaml
   ~/.config/friday/cli-config.yaml
   ```

4. Built-in package defaults and templates.

The built-in package files are templates, not editable config.

## 6. User Config And Data Paths

Default stable paths:

```text
~/.config/friday/config.yaml
~/.config/friday/cli-config.yaml
~/.config/friday/web-config.yaml
~/.local/share/friday/
~/.cache/friday/
```

Candidate runtime data subpaths:

```text
~/.local/share/friday/transcripts/
~/.local/share/friday/memory/
~/.local/share/friday/memory/chroma/
~/.local/share/friday/memory/graph.json
~/.local/share/friday/exports/
~/.cache/friday/
```

Open decision:

- Whether to use strict XDG paths on all platforms or a `platformdirs`-based
  OS-native directory strategy.

Initial recommendation:

- Use predictable XDG-style paths for documentation and config examples.
- Consider `platformdirs` during implementation if cross-platform native paths
  are important for first release.

## 7. Secrets And API Keys

API keys should be provided through environment variables by default.

Generated config should use placeholders:

```yaml
llm:
  model: gpt-4.1-mini
  api_key: ${OPENAI_API_KEY}

embedding:
  model: text-embedding-3-small
  api_key: ${OPENAI_API_KEY}
```

Users can then run:

```bash
export OPENAI_API_KEY=...
uvx friday-chat
```

Do not generate `.env` files containing secrets unless the user explicitly asks
for that behavior.

## 8. First-Run User Experience

Recommended commands:

```bash
uvx friday-chat init
uvx friday-chat doctor
uvx friday-chat
```

For web:

```bash
uvx friday-web init
uvx friday-web doctor
uvx friday-web
```

Command responsibilities:

| Command | Responsibility |
| --- | --- |
| `init` | Create editable config files in the user config directory |
| `doctor` | Validate config, required environment variables, data paths, optional dependencies, and provider reachability where safe |
| app command | Start the CLI or web app using resolved config |

If no config exists:

- interactive startup may offer to initialize config,
- noninteractive startup should fail with an actionable message.

Example failure:

```text
No Friday config found.
Run: uvx friday-chat init
Config path: ~/.config/friday/config.yaml
```

## 9. Package Templates

App packages should include config templates as package resources.

Candidate structure:

```text
packages/friday-chat/
  src/friday_chat/
    config_templates/
      config.example.yaml
      cli-config.example.yaml

packages/friday-web/
  src/friday_web/
    config_templates/
      web-config.example.yaml
```

`init` should copy or render these templates into the user config directory.

Templates must:

- contain no literal provider secrets,
- use environment-variable placeholders,
- point runtime data to stable user data paths,
- include comments explaining where user data lives.

## 10. Friday Web Static Assets

For `uvx friday-web`, users should not need Node/npm.

Release model:

- Build React/Vite assets during release.
- Include compiled static assets in the `friday-web` wheel.
- Serve those assets from the FastAPI backend.

Runtime behavior:

```bash
uvx friday-web
```

Should:

- start a local FastAPI/uvicorn server,
- bind to `127.0.0.1` by default,
- print the browser URL,
- optionally open the browser if configured.

## 11. Package Metadata Requirements

Before PyPI publication:

- Every publishable package must have a valid build backend.
- Every app package must expose stable console scripts.
- Metadata should include license, authors, readme, classifiers, and Python
  version support.
- Runtime dependencies should not include development-only tools.
- Optional heavyweight dependencies should live in extras.

Important known packaging considerations:

- The root `friday` package should behave as a meta-package.
- `friday-chat` should remain a runnable app package.
- `friday-web` should be a runnable app package once implemented.
- Heavy packages such as speech, document readers, MCP server support, telemetry
  exporters, sandbox/docker support, and optimization dependencies should be
  optional where practical.

## 12. Candidate Implementation Phases

### Phase 1: Packaging Audit And App Entrypoint Contract

Goal:

- Define which PyPI packages are published and which commands they expose.

Work:

- Confirm package/distribution names.
- Confirm `friday-chat` console script behavior under installed-package use.
- Define `friday-web` console script contract.
- Decide first-release package set.
- Decide whether `friday` meta-package includes all app packages by default or
  exposes extras.

Acceptance:

- App package names match desired `uvx` commands.
- The root meta-package role is documented.
- Optional/heavy dependencies are classified.

### Phase 2: Persistent Config Manager

Goal:

- Ensure `uvx` executions use stable user config and data paths.

Work:

- Implement shared config path resolution.
- Add `FRIDAY_CONFIG` support if missing.
- Add user config directory fallback.
- Add user data/cache directory defaults.
- Ensure package templates are treated as read-only resources.

Acceptance:

- `uvx friday-chat --config ./config.yaml` works.
- `FRIDAY_CONFIG=/path/config.yaml uvx friday-chat` works.
- `uvx friday-chat` resolves `~/.config/friday/config.yaml` when present.
- Runtime data is written outside the temporary package environment.

### Phase 3: `init` And `doctor`

Goal:

- Make first-run configuration explicit and user-editable.

Work:

- Add `friday-chat init`.
- Add `friday-chat doctor`.
- Add equivalent `friday-web` commands when the web package exists.
- Validate missing environment variables referenced by config placeholders.
- Validate writable data directories.
- Redact secrets in diagnostics.

Acceptance:

- Fresh users can bootstrap config without finding package internals.
- `doctor` gives actionable errors for missing API keys and bad paths.
- No command writes secrets by default.

### Phase 4: PyPI Release Preparation

Goal:

- Prepare packages for public publication.

Work:

- Normalize package metadata.
- Add root meta-package build configuration.
- Move dev dependencies out of runtime dependencies.
- Review optional extras.
- Add release checklist and CI workflow for package build and metadata checks.

Acceptance:

- All selected packages have publish-ready metadata.
- Meta-package dependencies pin or constrain compatible internal package
  versions.
- Release validation includes package build and metadata verification.

### Phase 5: TestPyPI And PyPI Publication Validation

Goal:

- Prove that published artifacts install and run correctly from package indexes,
  not only from the local monorepo.

Work:

- Add a TestPyPI publication rehearsal checklist.
- Add a production PyPI publication checklist.
- Define release artifact verification:
  - source distributions and wheels are present for every selected package,
  - package metadata passes index validation,
  - package descriptions render correctly,
  - internal package dependencies resolve from the target index,
  - app console scripts are present in installed wheels.
- Define an isolated install test matrix using fresh virtual environments.
- Define post-publish `uvx` smoke tests for:
  - `uvx friday-chat --help`,
  - `uvx friday-chat doctor`,
  - `uvx friday-chat init --help` or equivalent,
  - future `uvx friday-web --help`,
  - future `uvx friday-web doctor`.
- Define version-pinned `uvx` smoke tests for released versions.
- Define failure-case tests for missing config and missing required environment
  variables.

Acceptance:

- TestPyPI rehearsal validates package metadata, dependency resolution, and
  console scripts before production PyPI publication.
- Production PyPI closeout includes a fresh-machine or clean-environment
  `uvx` smoke test.
- Post-publish smoke tests prove that config is resolved outside the temporary
  `uvx` environment.
- Failed first-run cases produce actionable messages and do not create secrets
  or runtime state in package installation directories.

### Phase 6: Friday Web `uvx` Runtime

Goal:

- Make `uvx friday-web` start a complete local browser app.

Work:

- Add `friday-web` package.
- Add backend console script.
- Bundle compiled frontend assets.
- Add local-only defaults.
- Share runtime config resolution with `friday-chat`.

Acceptance:

- `uvx friday-web` starts a local server using stable user config.
- No Node/npm install is required at runtime.
- The server does not expose secrets through config/debug APIs.

### Phase 7: Update User And Developer Guides

Goal:

- Document the `uvx` distribution model before release.

Work:

- Update `docs/guides/02-getting-started.md` with `uvx friday-chat`,
  `uvx friday-chat init`, and `uvx friday-chat doctor`.
- Update `docs/guides/09-cli-reference.md` with config resolution,
  `init`, `doctor`, and app startup flags.
- Update `docs/guides/10-configuration.md` with user config paths,
  environment-variable secret handling, and runtime data locations.
- Update `docs/guides/11-advanced-topics.md` with PyPI package structure,
  meta-package behavior, extras, and web asset bundling.
- Update `docs/guides/13-troubleshooting.md` with `uvx` isolation, missing
  config, missing API keys, bad data paths, and first-run diagnostics.

Acceptance:

- Guides clearly explain that `uvx` package environments are temporary.
- Guides identify where editable config and runtime state live.
- Guides document environment-variable API key setup.
- Guides explain when to use `uvx`, `uv tool install`, and `pip install friday`.
- Distribution work is not considered complete until guide updates are done.

## 13. Open Questions

- Should `friday-chat init` be interactive by default, or should it only write
  templates?
- Should `init` overwrite existing config, refuse, or create backups?
- Should `doctor` test provider connectivity or only validate local config and
  environment?
- Should the default config path be strict XDG or platform-native via
  `platformdirs`?
- Should `friday` meta-package install `friday-chat` by default?
- Should `friday-web` be included in the default `friday` meta-package or only
  in a `friday[web]` extra?
- Should `uvx friday-chat` auto-run `init` on first launch in interactive mode?
- How should multiple Friday versions share or migrate the same user config
  directory?
- Should TestPyPI smoke tests use the same package names, or should any packages
  require temporary pre-release version suffixes to avoid resolver ambiguity?
- Which post-publish `uvx` tests should run from CI, and which should remain a
  manual release-manager checklist?
- Should release validation require a clean machine, a container, or a temporary
  user home directory to prove config/data isolation?

## 14. Initial Validation Targets

```bash
uv run pytest packages/friday-chat/tests_chat
uv run mypy packages/friday-chat
uv run ruff check packages/friday-chat
git diff --check -- docs/guides
git diff --check
```

When `friday-web` exists:

```bash
uv run pytest packages/friday-web/tests_web
uv run mypy packages/friday-web
uv run ruff check packages/friday-web
```

Release validation should eventually include package build and metadata checks,
but those commands should be run only during release-preparation work, not during
read-only planning review.

Release-preparation validation should also include index and `uvx` checks:

```bash
# TestPyPI rehearsal, exact commands to be finalized during release work.
twine check dist/*
uvx --index-url https://test.pypi.org/simple/ --from friday-chat friday-chat --help
uvx --index-url https://test.pypi.org/simple/ --from friday-chat friday-chat doctor

# Production PyPI smoke, after publication.
uvx friday-chat --help
uvx friday-chat doctor
uvx friday-chat@0.1.0 --help
```

The exact index flags and dependency-index behavior must be verified during
release automation design, especially for packages whose dependencies are split
between TestPyPI and PyPI.

## 15. Completion Criteria

- Users can bootstrap editable config outside the temporary `uvx` environment.
- API keys are supplied through environment variables by default.
- `uvx friday-chat` can start from stable user config.
- `uvx friday-chat doctor` reports missing config, missing env vars, and bad
  runtime paths clearly.
- Future `uvx friday-web` behavior follows the same config and data model.
- PyPI package roles are documented.
- TestPyPI rehearsal and production PyPI closeout include `uvx` smoke tests.
- Post-publish `uvx` tests verify help, doctor/config diagnostics, version
  pinning, missing-config behavior, and temporary-environment isolation.
- User and developer guides are updated before closeout.

# Approved REM-003: Python 3.13.4 supported minimum

Status: Approved by repository maintainer, 2026-10-05.
Approval evidence: "Make it happen." in response to the recommendation to require
Python 3.13.4 or newer and align metadata, tooling, lockfile and active verification.
Initiative: friday-telemetry-rewire. Work unit: TELEM-01 / REM-003; CD-001 A04.
Delta base: 09fe69090f33ae9c047e2e101fe87727d52f9734.
Branch: feature/friday-telemetry-rewire. No lightweight exemption or waiver.

## Authority and objective

Explicit maintainer direction changes the support contract: all workspace
packages and the lab project require Python >=3.13.4. This supersedes the
3.10-minimum obligation in CD-001 A01/A03 and REM-002 prospectively. It does
not reinterpret historical results, repair LiteLLM, waive repository failures,
or change telemetry source behavior. Repository policies, the build/tactical
plans and CD-001 remain controlling outside this amendment.

Map VAL-003-F01 once: its minimum-runtime component is resolved by this explicit
support-policy change and current supported-runtime evidence. The root lint,
PTY timing, native-tool, optional-reader, guarded-Web and listener failures
remain unresolved; aggregate AC-06 stays nonpassing until separately resolved.
This directive authorizes no remediation or waiver of those components.

## Exact allowed files

Only Python requirement/tool-target statements, matching classifiers, interpreter
selection, setup/version guidance and Docker FROM versions may change in:

- `pyproject.toml`
- `uv.lock`
- `.python-version`
- `tests/lab/pyproject.toml`
- `scaffold.sh`
- `README.md`
- `packages/friday-sandbox/docker/Dockerfile.python`
- `packages/friday-agent/pyproject.toml`
- `packages/friday-chat/pyproject.toml`
- `packages/friday-cli/pyproject.toml`
- `packages/friday-core/pyproject.toml`
- `packages/friday-finance/pyproject.toml`
- `packages/friday-llm/pyproject.toml`
- `packages/friday-mcp/pyproject.toml`
- `packages/friday-memory/pyproject.toml`
- `packages/friday-moltbook/pyproject.toml`
- `packages/friday-optimization/pyproject.toml`
- `packages/friday-runtime/pyproject.toml`
- `packages/friday-sandbox/pyproject.toml`
- `packages/friday-speech/pyproject.toml`
- `packages/friday-telemetry/pyproject.toml`
- `packages/friday-tools/pyproject.toml`
- `packages/friday-transcript/pyproject.toml`
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `docs/guides/02-getting-started.md`
- `docs/guides/15-contributing.md`
- `docs/guides/FRIDAY-FEATURES.md`
- `docs/guides/OUTLINE.md`
- `docs/guides/10-configuration.md`
- `docs/guides/11-advanced-topics.md`
- `docs/reference/specs/tool_specification.md`
- `docs/reference/specs/sandbox_specifications.md`
- `friday-web/content/docs/getting-started/_index.md`
- `friday-web/content/docs/contributing/setup.md`
- `friday-web/content/docs/advanced/deployment.md`

Planning scope: this packet's CD-001, verification profile, tactical/build plan,
authority manifest, index, append-only execution log, REM-003 records and fresh
review artifacts; telemetry-only board/dashboard changes preserving prior dirty
changes. Generated friday-web/public outputs are excluded; source documentation
is updated for its next normal build. Historical accepted packets, prior review
requests/reports and execution artifacts remain immutable.

## Implementation and migration

- Set every project requires-python to >=3.13.4. Remove obsolete Python 3.10,
  3.11 and 3.12 classifiers. Keep the Python 3.13 classifier.
- Set root and package Ruff targets to py313 and root mypy to 3.13 without
  weakening rules or adding suppressions. Set .python-version to 3.13 (minor
  preference); the exact patch floor is enforced by package/lock metadata.
- Update scaffold defaults, contributor/setup guides and Python Docker examples
  to the new requirement; use python:3.13.4-slim[-bookworm] in FROM statements.
  Do not build, pull, run or publish images under this directive.
- Regenerate uv.lock using existing pins as preferences, cache/offline first,
  never --upgrade. Reject changes to surviving dependency versions or sources;
  removal of now-unreachable Python/platform alternatives is allowed. Public
  credential-free PyPI metadata/artifacts may be read if cache is insufficient.
  No source builds, interpreter downloads, new dependencies or shared .venv
  synchronization. Keep LiteLLM==1.100.1 and all manifest dependency constraints.
- Python <3.13.4 is unsupported. Existing installations must select a supported
  interpreter and recreate their environment through normal uv sync. The current
  3.13.10 environment already meets the requirement and remains unchanged.

## Criteria and required verification

R3-01: All 17 workspace projects plus lab declare >=3.13.4; packaging SpecifierSet
rejects 3.10/3.11/3.12 and 3.13.0-3.13.3, accepts 3.13.4 and installed 3.13.10.
R3-02: Tool targets, interpreter preference, scaffolds, Docker statements and
current installation/contribution guides match support policy; no source edits.
R3-03: uv lock --offline --check succeeds; TOML/lock graph comparison proves no
surviving dependency version/source changed and LiteLLM remains 1.100.1.
R3-04: Fresh-context read-only review of stable scope/authority and then candidate;
Python 3.13 syntax, changed-source mypy, changed-file Ruff, focused six-module
suite and synthetic Chat-observer/Composite import/lifecycle pass on installed
3.13.10 with no credentials, services or original application data.
R3-05: Board/docs validation and git diff --check pass. Capture root Ruff and
complete affected-package/root pytest against isolated base/candidate under
current guard/importlib profile; report failures as aggregate AC-06 failures,
never waive them or imply full initiative verification. Compare normalized
Ruff findings under old/new targets; target-driven diagnostics are explicitly
reported rather than suppressed. Exactly two live modules remain excluded from
root pytest. No new test exclusions or deadline changes.

Use /private/tmp/telem-01/REM-003 for disposable checkouts/evidence. Run tests
under the credential-free environment allowlist and unchanged non-loopback
network guard from REM-002; permit only already-approved three Chat fixture
privileged reruns if needed. Read-only test execution otherwise remains
unprivileged. Preserve original dirty paths and runtime state; no source/test
patches, provider calls, exporter activation, push, merge, release or deployment.
Retain existing synthetic ignored audit summaries only within isolated test roots.

Before product metadata/image/scaffold edits, freeze this amended authority and
obtain fresh directive readiness review. After implementation, commit a stable
candidate and request fresh delta and aggregate read-only review with exact
hashes, commands, exclusions and evidence. A delta result never substitutes for
aggregate VERIFIED. Stop on dependency version drift, unsafe tests, unapproved
paths/effects or incompatible authority. Correct bounded mechanical metadata
and documentation findings within this scope and submit a fresh candidate.

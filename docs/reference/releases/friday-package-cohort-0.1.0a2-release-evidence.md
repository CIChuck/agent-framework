# Friday Package Cohort 0.1.0a2 Release Evidence

- Evidence date: 2026-09-03
- Candidate source commit: `129d3ff`
- Merge commit: `a422c68`
- Artifact directory: `dist/friday-package-cohort-0.1.0a2/`
- Status: published to production PyPI and post-publication verified
- Publication date: 2026-09-03
- TestPyPI: not used
- Release tag: `v0.1.0a2`, annotated and pushed to `origin`
- GitHub Release: intentionally deferred until Friday 1.0

## Decision

The complete 17-distribution Friday family is published as one lock-step
`0.1.0a2` cohort. Every active project version and exact internal dependency
uses `0.1.0a2`. The maintainer separately authorized production publication
after the candidate merge, deterministic validation, installed-artifact
validation, and live provider-compatibility testing.

Provider compatibility did not alter workflow semantics. Agent, Runtime, and
Friday Chat orchestration remain provider and model independent. Provider and
model differences remain declarative profile, capability, translation, and
compatibility-test concerns.

## Candidate Evidence

The detailed implementation, package-test, baseline-debt, clean-artifact, and
live-provider results are recorded in the
[typed LLM execution log](../../planning/upgrades/friday-packages/friday-framework-typed-llm-execution-log.md).

Final artifact gates:

- 17 universal wheels and 17 source distributions were present.
- The custom artifact validator passed all 34 files.
- `twine check` passed all 34 files immediately before publication.
- Every local SHA-256 value matched the frozen
  [artifact manifest](../../planning/upgrades/friday-packages/friday-package-cohort-0.1.0a2-artifact-sha256.txt).
- Candidate clean-install, import, CLI, typed fake-transport, and bounded live
  provider-compatibility gates passed before publication.

## Production Publication

The projects were uploaded in the approved dependency order:

1. Telemetry, Transcript, Sandbox, and Moltbook;
2. Core;
3. Finance, Friday LLM, and Speech;
4. Memory;
5. Agent, Optimization, and Tools;
6. MCP;
7. Runtime;
8. CLI;
9. Friday Chat;
10. root Friday Framework.

After each layer, PyPI's published filenames and SHA-256 values were compared
with the frozen local wheel and source distribution before dependent packages
were uploaded. All 34 registry hashes matched.

PyPI Simple API propagation was briefly uneven. Initial strict clean-install
attempts stopped when newly published Friday Chat, Agent, and CLI versions were
not yet resolver-visible. A pip-based readiness probe later found MCP and
Runtime still propagating, then confirmed all 17 projects available. These were
registry propagation holds, not artifact or dependency failures.

## Post-Publication Verification

A new Python 3.13.10 virtual environment installed
`friday-framework[all]==0.1.0a2` and `friday-chat==0.1.0a2` with cache use
disabled and production PyPI as the only index.

Final results:

- all 17 Friday distributions installed at exactly `0.1.0a2`;
- `pip check` reported no broken requirements;
- Friday Framework, Runtime, Agent, and Chat imports succeeded;
- `friday-chat --version` reported `friday-chat 0.1.0a2`;
- `friday-chat --help` exited successfully.

Primary release pages:

- [Friday Framework](https://pypi.org/project/friday-framework/0.1.0a2/)
- [Friday Chat](https://pypi.org/project/friday-chat/0.1.0a2/)
- [Friday LLM](https://pypi.org/project/friday-framework-llm/0.1.0a2/)

The temporary ignored `.env` upload credential was removed after verification.
Because the PyPI token was disclosed in chat, it should be revoked in PyPI
account settings even though it is no longer stored in the checkout.

## Source Tag And GitHub Release Policy

The annotated `v0.1.0a2` tag resolves to publication-evidence commit `fc8ea18`
and is present on `origin`. GitHub Releases will not be created for pre-1.0
Friday versions; during alpha development, Git tags, PyPI releases, and checked-
in release evidence are the release record.

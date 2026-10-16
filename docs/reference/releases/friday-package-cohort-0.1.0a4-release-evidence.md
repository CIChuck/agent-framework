# Friday Package Cohort 0.1.0a4 Release Evidence

Status: published to production PyPI and post-publication verified.
Publication completed: 2026-10-16 UTC.

All 17 Friday distributions are published at `0.1.0a4`. Every project, wheel
and sdist advertises the canonical documentation https://gendevx.com/friday/.
The release synchronizes versions and internal pins without changing runtime
behavior or the 196 third-party workspace lock records.

Source delivery: [PR #10](https://github.com/CIChuck/agent-framework/pull/10)
merged the original branch as `465c5643`; [PR #11](https://github.com/CIChuck/agent-framework/pull/11)
merged alpha4 as `489aed28`. Both remote source branches were deleted.
Source candidate `e965917a` received a fresh independent
[VERIFIED review](../../planning/active/friday-alpha4-release/validation/independent-review/report.md).
191 focused source tests, six installed Chat import checks, changed Python
Ruff, focused Mypy, metadata, shell and offline lock checks passed.

All 17 wheels and 17 source distributions passed strict Twine and repository
artifact checks, including metadata, exact pins, packaged resources, source
correspondence and sensitive-content checks. The
[frozen SHA256 manifest](../../planning/active/friday-alpha4-release/validation/artifact-sha256.json)
exactly matches all
[production registry filenames and hashes](../../planning/active/friday-alpha4-release/validation/publication/published-files.json).
Artifacts remain locally in ignored `dist/friday-package-cohort-0.1.0a4/`.

Publication used the established dependency layers and the existing credential
only in the upload child environment. The first package's version-specific JSON
endpoint returned 404 after successful upload; the current project record
already showed alpha4. Verification therefore also accepts that project record
only when its version equals alpha4 and both hashes and Documentation URL match.
No conflicting file was overwritten, and no credential is retained in evidence.

A fresh Python 3.13.10 environment installed
`friday-framework[all]==0.1.0a4` and `friday-chat==0.1.0a4` using production PyPI
as its only index, without local artifact links and with caching disabled.
The command explicitly enables prereleases for the coordinated alpha pins.
Initial index-propagation and prerelease-selection attempts installed no cohort;
their command results are retained alongside the successful final installation.
[Command results](../../planning/active/friday-alpha4-release/validation/publication/production-install-results.json),
[outputs](../../planning/active/friday-alpha4-release/validation/publication/production-install-output.json)
and the [installed dependency snapshot](../../planning/active/friday-alpha4-release/validation/publication/production-environment-versions.json)
confirm:

- all 17 installed versions are exactly `0.1.0a4`, with the correct docs URL;
- `pip check` finds no broken requirements;
- framework, Runtime, MCP, Agent and Chat imports pass;
- typed LLM and Chat fake transports, legacy construction and packaged templates pass;
- `friday-chat --version` reports alpha4 and `--help` succeeds.

Smoke checks used isolated HOME/TMP directories and a network-denying guard.
No live model/provider calls were made. The six pre-existing temporary-checkout
links in the unchanged historical telemetry VAL-001 report remain documented
baseline debt; changed-file links and board/dashboard checks pass.

Release pages: [Friday Framework](https://pypi.org/project/friday-framework/0.1.0a4/)
and [Friday Chat](https://pypi.org/project/friday-chat/0.1.0a4/).
GitHub and PyPI delivery are complete. Maintainer lifecycle acceptance is separate.

# Friday Package Cohort 0.1.0a3 Release Evidence

Status: published to production PyPI and post-publication verified.
Publication completed: 2026-10-15 UTC (2026-10-14 America/New_York).

The maintainer explicitly requested production publication and subsequently replaced the rejected upload token. The complete 17-distribution Friday family is published at `0.1.0a3`. No credential values are present in this record.

Source version candidate `8b85bd91` was independently VERIFIED. Build source `40d7d38c` produced 17 universal wheels and 17 source distributions. Release-helper candidate `72f06012` was independently VERIFIED: its sole product edit corrects the stale LiteLLM artifact expectation from `1.94.1` to the already-declared `1.100.1`. No dependency or distribution contents changed in that correction.

All 34 files passed strict Twine validation and repository artifact metadata, resources, internal pins, suspicious paths and sensitive-content checks. A clean local-artifact installation passed before upload. The [frozen SHA256 manifest](../../planning/active/friday-alpha3-version-bump/validation/publication/artifact-sha256.json) exactly matches all [production registry filenames and hashes](../../planning/active/friday-alpha3-version-bump/validation/publication/published-files.json). Artifacts are retained locally under ignored `dist/friday-package-cohort-0.1.0a3/`.

Publication followed the dependency layers used for the previous cohort. The first authentication failure uploaded nothing. After credential replacement, transient PyPI HTTP 500 errors were handled with bounded retries and serialization of remaining uploads; matching existing files were skipped and conflicting files were prohibited. All 17 projects finished with both expected files verified. No TestPyPI upload was performed.

A fresh Python 3.13.10 environment installed `friday-framework[all]==0.1.0a3` and `friday-chat==0.1.0a3` with production PyPI as its only index, no local artifact links, and caching disabled. [Post-publication command results](../../planning/active/friday-alpha3-version-bump/validation/publication/production-install-results.json) and [outputs](../../planning/active/friday-alpha3-version-bump/validation/publication/production-install-output.json) confirm:

- all 17 Friday distributions installed at exactly `0.1.0a3`;
- `pip check` reports no broken requirements;
- Core, Telemetry, LLM, Transcript, Memory, Agent, Runtime, CLI, Tools, MCP and Chat imports succeed;
- installed typed LLM fake transport and legacy constructor checks pass;
- installed Chat packaged configuration/templates and typed fake transport checks pass;
- `friday-chat --version` reports `friday-chat 0.1.0a3`, and `--help` succeeds.

Smoke execution used isolated HOME/TMP directories and a network-denying guard; no live model/provider calls were made. The [installed dependency snapshot](../../planning/active/friday-alpha3-version-bump/validation/publication/production-environment-versions.json) records the tested production profile. Source-version tests previously passed all 191 focused cases; the release-helper repair passed its independent bounded checks.

Primary release pages: [Friday Framework](https://pypi.org/project/friday-framework/0.1.0a3/), [Friday Chat](https://pypi.org/project/friday-chat/0.1.0a3/), [Friday LLM](https://pypi.org/project/friday-framework-llm/0.1.0a3/), [Friday MCP](https://pypi.org/project/friday-framework-mcp/0.1.0a3/).

PyPI delivery is complete. Source push, release tag and GitHub Release were not included in this publication unit. Repository lifecycle acceptance remains distinct from verified release delivery.

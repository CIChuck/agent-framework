# REL-A3-002 release-helper review

VERIFIED

Reviewer: independent agent `/root/alpha3_publication_helper_review`, GPT-6 (exact runtime model revision unavailable). Date: 2026-10-15 UTC. Mode: fresh, read-only bounded work-unit review. No builder private reasoning was supplied or used; the controller supplied the frozen inputs and excluded prior source-version validation and subsequent publication checks from this unit.

Candidate: `72f06012437ae5b82ade9255dcc2a0c0119ea898`; base: `40d7d38c7b38670db9c8d0b92b8b2bd100301b50`; range: `40d7d38c..72f06012`; branch authority: `release/0.1.0a3`. The checkout was clean at initial inspection and at the end of the audit.

Read authority: `AGENTS.md`, repository engineering policy, independent validation policy, development task lifecycle policy, `docs/planning/active/friday-alpha3-version-bump/publication-authority.json`, and `directives/CD-REL-A3-002-publication.md`. The board remains started with granted implementation authority and identifies the production-publication gate.

Frozen authority SHA256:

- Publication manifest: `5902c8f4ccc30592b6982d05dcb6e046516215aaa52b2076b73a0d2d9f70f353`.
- Directive: `4a7f7ce1facec98784cddc83fa12c80a478ab2dc9c314c648a3cd73ea030cbde`, matching the manifest.
- Candidate helper: `549a599921caa6052f02d7890f47b9bf14b4210c23595eab01c29d4c64033c9e`.

The entire product diff is exactly one literal replacement in `scripts/check-package-artifacts.py:180`, `litellm==1.94.1` to `litellm==1.100.1`. All remaining helper bytes, including negative checks, are identical to base. The only other changed paths are the publication manifest, publication directive, board, and generated dashboard. Source dependency metadata, lock records, package code, tests, versions, and prebuilt artifacts are unchanged. The expected requirement agrees with `packages/friday-llm/pyproject.toml`, the resolved LiteLLM version and LLM requirement in `uv.lock`, and actual built LLM wheel metadata.

All commands below ran through `/private/tmp/friday-mcp-upgrade/venv/bin/python /private/tmp/friday-mcp-upgrade/credential-cleanup/publication/run_check.py <label> <argv...>` in the candidate checkout. Let `P=/private/tmp/friday-mcp-upgrade/venv/bin/python`. Complete receipts, guarded stdout and stderr are in `/private/tmp/friday-mcp-upgrade/credential-cleanup/publication/checks/<label>/`. Every check exited zero, pinned the candidate above, and recorded zero credential redactions.

| Label | Command after label | Observed evidence |
| --- | --- | --- |
| `a3pub-review-cohort-helpers` | `P -m pytest tests/integration/test_package_cohort_metadata.py packages/friday-chat/tests_chat/test_release_helpers.py -q` | 8 passed; includes stale internal pin and missing entry-point rejection |
| `a3pub-review-artifacts` | `P scripts/check-package-artifacts.py /private/tmp/friday-alpha3-pypi/dist` | 17 wheels and 17 sdists validated, including metadata, resources, suspicious paths/content |
| `a3pub-review-metadata` | `P scripts/check-package-metadata.py` | All 17 project metadata files validated |
| `a3pub-review-ruff` | `/private/tmp/friday-mcp-upgrade/venv/bin/ruff check scripts/check-package-artifacts.py` | All checks passed |
| `a3pub-review-board` | `P scripts/friday-dev-board.py validate` | 29 tasks validated |
| `a3pub-review-render` | `P scripts/friday-dev-board.py render --check` | Planning dashboard current |
| `a3pub-review-docs` | `P scripts/check-documentation-lifecycle.py` | 596 Markdown files checked |
| `a3pub-review-show` | `P scripts/friday-dev-board.py show friday-alpha3-version-bump` | started, granted, release branch and publication gate |
| `a3pub-review-whitespace` | `git diff --check 40d7d38c7b38670db9c8d0b92b8b2bd100301b50 72f06012437ae5b82ade9255dcc2a0c0119ea898` | No whitespace errors |
| `a3pub-review-audit-v2` | `P /private/tmp/friday-alpha3-pypi/helper-review-audit.py` | Exact diff and authority hashes verified; valid built LLM wheel accepted; isolated stale `1.94.1`, wrong `1.100.0`, and absent LiteLLM requirements each rejected specifically for missing `litellm==1.100.1`; all 34 original artifact digests unchanged |

The first audit also passed; v2 tightened the missing-requirement fixture to preserve all unrelated metadata headers. Both receipts are retained. The reviewer probe is outside the source checkout and creates only temporary wheel copies.

No findings or waiver-like changes in this helper unit. Residual boundary: this verdict covers the helper repair and its focused checks. Strict Twine, fresh local installs/imports/CLI/templates/fake transport, upload, registry hash equality, and production-index install remain controller-owned publication gates. No upload, network operation, install, source edit, commit, acceptance, or lifecycle mutation was performed by this reviewer. The prior source-version unit was not re-reviewed.

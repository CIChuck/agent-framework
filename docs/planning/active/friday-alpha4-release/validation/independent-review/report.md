# Friday alpha4 independent validation

**VERIFIED** — no blocking findings for the frozen source and local-artifact release gate.

Reviewer: `/root/alpha4_release_review`, a separate fresh-context Codex validator (GPT-6 family per agent identity; exact model build was not exposed). Review date: 2026-10-16T20:19:22.677815+00:00. Mode: full bounded candidate review; read-only source. Parent/controller supplied the handoff coordinates, acceptance criteria, known baseline debt and clean-install readiness, without builder private reasoning. The shared checkout was used instead of an isolated worktree; HEAD, clean tracked worktree, authority and governed file bytes were verified at both ends. No source edits, commits, pushes, merges, uploads, credentials or live-provider calls were performed.

## Frozen inputs

- Initiative / directive: `friday-alpha4-release` / `CD-REL-A4-001`.
- Base: `465c5643b855c76a3584c393e96fb7bd1c855396` (local Git merge commit records PR #10).
- Candidate: `e965917a9a236c4428972255e2017be81aa69d7f`.
- Branch: `release/0.1.0a4`.
- Full range: `git diff 465c5643b855c76a3584c393e96fb7bd1c855396 e965917a9a236c4428972255e2017be81aa69d7f`, retained in `candidate.diff`.
- Authority and directive hashes below are SHA256 of the exact candidate blobs. Every one of the 52 baseline hashes in `authority.json` was separately recomputed from the stated base.

| Input | SHA256 at candidate | Last changed revision |
| --- | --- | --- |
| `AGENTS.md` | `02c6360f0e2532a3ea761d7ae228fb105231c60d447146ead69c01c6ff99d152` | `816e64f35d58b4b1334388dd3b5b6fb312534176` |
| `docs/reference/policies/repository-engineering-policy.md` | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` | `0c8095f5132c9cc47573f27481dea59a7cc70c6c` |
| `docs/reference/policies/independent-validation-policy.md` | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` | `12c1e9e577409bf25f7fdc18fb7bb75a24f5ec07` |
| `docs/reference/policies/development-task-lifecycle.md` | `7087fb62381cc8a46128bc6745476d1aa08e1d577b4c73340760657ae834fe2a` | `30119a18f77a435cd40f84bfefb69c32ede54998` |
| `docs/planning/active/friday-alpha4-release/authority.json` | `eedde1ab89091cd75c17223e6b1656d29687ce3ac389a0989717d012857c9351` | `e965917a9a236c4428972255e2017be81aa69d7f` |
| `docs/planning/active/friday-alpha4-release/directives/CD-REL-A4-001.md` | `21046526cdb982fbbddb8ddde71c4b4511a4329a24a94720df68181622dc6a10` | `e965917a9a236c4428972255e2017be81aa69d7f` |

## Acceptance evidence

1. **Exact bounded source scope:** all 60 changed paths reconcile to the 52 explicitly authorized product paths and eight planning/authority/evidence paths. All 52 product files equal their baseline bytes with only `0.1.0a3` replaced by `0.1.0a4`. This covers all source defaults, exported versions, helpers, matching fixtures, current README examples and lock records. Deliberate alpha0 negative fixtures are unchanged. No historical authority/review/evidence product files were edited. The eight planning changes were read in full: alpha4 authority/directive/evidence plus board/dashboard delivery reconciliation; they do not infer maintainer acceptance. Evidence: `audit.json:source_scope`, `candidate.diff`, directive.
2. **All 17 projects:** versions and every internal pin are exact alpha4; all project Documentation URLs are `https://gendevx.com/friday/`; all 17 current READMEs advertise alpha4. No third-party declarations changed, and all 196 third-party lock records remain byte-equivalent as parsed data. Evidence: `audit.json:metadata`, `metadata.stdout`, `lock.stderr`, exact-substitution comparison.
3. **Source verification:** 8 cohort/release-helper tests and 183 modern MCP tests passed (191), plus five source Chat import tests. The distribution-metadata assertion was preserved and validated in the clean installed profile with all six existing Chat import tests. Changed-Python Ruff passed for 16 files; focused Mypy passed for four helper/cohort files. Metadata, shell syntax, offline lock check, board/dashboard and whole-range whitespace passed. Evidence: command/log table below and `checks.json`.
4. **Frozen artifacts:** 17 wheels and 17 sdists pass the repository artifact checker and strict Twine. Independent SHA256 verification exactly reconciles all 34 filenames to `artifact-sha256.json`; independently read artifact metadata matches all 34 `artifact-metadata.json` records, all versions, URLs, source dependencies including expanded self-extras, optional extras, Python requirement and license. Wheel RECORD hashes/sizes were independently checked. 1,150 archive source/resource files match exact candidate blobs; all configured tracked wheel source files are present. Sdists include the inherited repository `.gitignore`, separately byte-checked against the candidate root `.gitignore`. Markdown long descriptions match the candidate README after correct UTF-8 payload decoding. Chat entry point and all three packaged templates are present. Repository artifact checks found no suspicious paths or sensitive content. Evidence: `audit.json:artifacts`, `artifacts.stdout`, `strict-twine-corrected.stdout`.
5. **Clean local installation:** independently verified all 17 installed versions/Documentation URLs and every installed wheel member except installation-rewritten RECORD against the frozen wheel bytes. All 16 namespace modules resolve from the clean environment, and all existing six Chat import tests pass there. Independently reran pip consistency, typed/legacy LLM fake transport, Chat fake transport with packaged templates, CLI help and version. An active network-denying audit hook was verified before the installed import checks. Sanitized temporary HOME/TMPDIR and disabled telemetry were used; provider environment values were not inherited. Controller's ten successful installation results and installed-version manifest were also inspected and snapshotted. Evidence: `installed-review.json`, `installed-review-corrected-check.json`, offline log files, `controller-local-install-results.json`.
6. **Links and preserved state:** all 21 changed Markdown files pass the repository local-link check. Full lifecycle checking reports exactly six broken links in unchanged `docs/planning/active/friday-telemetry-rewire/validation/VAL-001/report.md`, all targeting the retired `/private/tmp/telem-01/review` checkout. This debt is expressly disclosed in the directive; the historical evidence bytes match the base. No unrelated failure remains. Final HEAD is unchanged, tracked worktree is clean and the shared development distribution metadata is still alpha3. Evidence: `audit.json:links`, `documentation-lifecycle-no-sync.stdout`, `shared-environment-version.stdout`, `final-evidence.json`.

## Reproducible commands and logs

The complete argv, working directories, relevant sanitized environment and exit codes are in `checks.json`, `followup-checks.json`, `installed-review-corrected-check.json` and the consolidated `final-evidence.json`. All relative log paths in this table are under this report directory.

| Check | Result | Evidence |
| --- | --- | --- |
| cohort-and-helpers | PASS | `cohort-and-helpers.stdout`, `cohort-and-helpers.stderr` |
| modern-mcp | PASS | `modern-mcp.stdout`, `modern-mcp.stderr` |
| source-chat-imports | PASS | `source-chat-imports.stdout`, `source-chat-imports.stderr` |
| metadata | PASS | `metadata.stdout`, `metadata.stderr` |
| artifacts | PASS | `artifacts.stdout`, `artifacts.stderr` |
| ruff | PASS | `ruff.stdout`, `ruff.stderr` |
| focused-mypy | PASS | `focused-mypy.stdout`, `focused-mypy.stderr` |
| lock | PASS | `lock.stdout`, `lock.stderr` |
| shell-syntax | PASS | `shell-syntax.stdout`, `shell-syntax.stderr` |
| board-validate | PASS | `board-validate.stdout`, `board-validate.stderr` |
| dashboard | PASS | `dashboard.stdout`, `dashboard.stderr` |
| whitespace | PASS | `whitespace.stdout`, `whitespace.stderr` |
| strict-twine-corrected | PASS | `strict-twine-corrected.stdout`, `strict-twine-corrected.stderr` |
| documentation-lifecycle-no-sync | BASELINE DEBT (six unchanged historical links) | `documentation-lifecycle-no-sync.stdout`, `documentation-lifecycle-no-sync.stderr` |
| installed-pip-check | PASS | `installed-pip-check.stdout`, `installed-pip-check.stderr` |
| installed-llm-fake-transport | PASS | `installed-llm-fake-transport.stdout`, `installed-llm-fake-transport.stderr` |
| installed-chat-fake-transport | PASS | `installed-chat-fake-transport.stdout`, `installed-chat-fake-transport.stderr` |
| installed-chat-help | PASS | `installed-chat-help.stdout`, `installed-chat-help.stderr` |
| installed-chat-version | PASS | `installed-chat-version.stdout`, `installed-chat-version.stderr` |
| shared-environment-version | PASS | `shared-environment-version.stdout`, `shared-environment-version.stderr` |
| installed-review-corrected | PASS | `installed-review-corrected.stdout`, `installed-review-corrected.stderr` |

Independent correspondence audit: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python /private/tmp/friday-alpha4-review-e965917a/audit.py`. Its source is retained in `audit.py`; outputs are `audit.json` and `audit.stdout`. The candidate is read directly from Git, and artifacts are read without extraction into the checkout. The corrected installation probe is `installed-review.py`.

For the documentation script's nested `uv run`, use `UV_CACHE_DIR=<repo>/build/release-cache UV_OFFLINE=1 UV_NO_SYNC=1 .venv/bin/python scripts/check-documentation-lifecycle.py`. Source tests use `-p no:cacheprovider`, temporary pytest directories and `PYTHONDONTWRITEBYTECODE=1`; Ruff uses `--no-cache`, and Mypy cache is within this report directory. Clean installed commands use `build/alpha4-work/local-install/bin/python` with `PYTHONPATH=<repo>/build/alpha4-work/guard`.

Invocation corrections retained in raw logs: initial Twine argv accidentally included the ignored distribution-directory `.gitignore`; corrected wheel/sdist-only argv passes all 34 artifacts. The initial lifecycle command attempted its nested uv default sync and failed sandbox DNS while resolving build dependencies; it was rerun with no-sync/offline, and shared metadata is verified unchanged. An optional custom provenance probe initially assumed find-links installs provide PEP610 `direct_url.json`; uv does not require that file, so the corrected probe compares installed member bytes directly to frozen wheels. The archive audit was corrected to decode UTF-8 metadata payloads and recognize the inherited, candidate-matching root `.gitignore`. These were reviewer invocation/probe assumptions, not candidate findings; no assertions in product tests were weakened.

## Residual limits and next boundary

This verdict covers the candidate source, frozen local artifacts and clean local installation on Python 3.13.10/macOS arm64. The full repository suite and live provider/API behavior were not exercised for this mechanical release. The six known historical links remain disclosed debt. No production registry publication or production-index installation has occurred as part of this review; those independently authorized delivery steps require the controller's subsequent immutable registry filename/hash verification and fresh production install evidence. No credential handling or publication script was inspected or executed by this validator.

`VERIFIED` is independent validation, not maintainer acceptance or a claim that delivery/publication has completed. Any change to reviewed source, tests, configuration, authority, directive or candidate requires a fresh review. Retained alpha3 reports were treated as history and did not supply alpha4 acceptance.

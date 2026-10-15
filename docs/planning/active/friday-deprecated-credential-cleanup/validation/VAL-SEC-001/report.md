VERIFIED

# VAL-SEC-001 — independent full work-unit review

Link-only correction: repository-relative source links replace temporary checkout paths. The original review bytes are preserved in [report.original.txt](report.original.txt); prior hashes refer to that original. See [correction provenance](link-correction.json). Review findings, candidate, and verdict are unchanged.

## Candidate and review identity

- Initiative: `friday-deprecated-credential-cleanup`; work unit: `SEC-001`.
- Base: `0f5cf2c413092d3c12ae691c547defa22dc3dbc5`.
- Frozen candidate: `a65f1366fcb0baf4cbd1198f75933fe72ad68641`.
- Exact selected range: `0f5cf2c413092d3c12ae691c547defa22dc3dbc5..a65f1366fcb0baf4cbd1198f75933fe72ad68641`.
- Review mode: full bounded work-unit review, not a repository-wide sanitization or provider-revocation review.
- Reviewer: separate Codex validation agent `/root/sec001_removal_review`; model family: GPT-6 (exact deployed variant/version unavailable).
- Review date: 2026-10-14 UTC. Independent final checks began 2026-10-14T13:17:38.702525+00:00; report generated 2026-10-14T13:19:58.474371+00:00.
- Fresh context: reviewer received the validation request and environment instructions, not builder private reasoning or a prior validator verdict. Controller supplied subsequent safety/status summaries; those claims were not accepted as evidence and relevant facts were independently checked.
- Checkout: clean local branch `security/remove-deprecated-credentials` at the frozen candidate; final HEAD and clean status reconfirmed. No candidate mutation, staging, commit, publication, provider contact or remediation occurred. Review artifacts are confined to `/private/tmp/friday-mcp-upgrade/credential-cleanup/review`.

## Authority and precedence

The current authority manifest records the original removal instruction and final maintainer direction verbatim: “yes. don't waste time.  The plan is to rotate the keys And disable the old keys.” The controlling directive reconciles the bounded four-path removal with the 54 additional disclosed tracked copies. Its latest criterion 3 governs; the earlier repository-wide absence criterion and deferred expansion proposal do not enlarge this unit.

Sources: [docs/planning/active/friday-deprecated-credential-cleanup/authority.json](../../authority.json); [docs/planning/active/friday-deprecated-credential-cleanup/directives/CD-SEC-001-remove-deprecated-credential-artifacts.md](../../directives/CD-SEC-001-remove-deprecated-credential-artifacts.md) (line 13); [AGENTS.md](../../../../../../AGENTS.md) (line 46); [docs/reference/policies/independent-validation-policy.md](../../../../../reference/policies/independent-validation-policy.md); [docs/reference/policies/repository-engineering-policy.md](../../../../../reference/policies/repository-engineering-policy.md); [docs/guides/security-configuration-guidelines.md](../../../../../guides/security-configuration-guidelines.md).

Verified SHA256 pins:

| Authority | SHA256 |
| --- | --- |
| `authority.json` | `b08f9f348c3560587efdf29b57fe1bd037e3a79c2280761ca6becbea2b397741` |
| `CD-SEC-001` | `02caf340c9bc8d2f2c4879fbdf15d335f72f8bde7650710d3f10c1a44b1fb87c` |
| `AGENTS.md` | `02c6360f0e2532a3ea761d7ae228fb105231c60d447146ead69c01c6ff99d152` |
| `docs/reference/policies/repository-engineering-policy.md` | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` |
| `docs/reference/policies/independent-validation-policy.md` | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` |
| `docs/guides/security-configuration-guidelines.md` | `bfeef92007f506a8a8a0a5faa4596fafeffdae400fc150986a00d548c41d48ee` |
| `docs/dev-skills/independent-code-validator.md` | `578fe10d00df438be8c0dc2537ee08c08c3361ebb3615db0fd17e148b928f508` |

The directive hash matches `authority.json.directive_sha256`. All four baseline product SHA256 values match their Git base blobs. See [audit.json](audit.json). Repository policy and fresh independent review requirements were read directly; no prior report substituted for this full candidate review.

## Findings

No mandatory requirement violation, blocker, critical or high finding remains in this bounded unit. The proposal's historical “scope decision pending” wording is understood as proposed/deferred metadata; current authority, directive, packet and execution log explicitly prohibit implementing the broader removal. It grants no extra authority.

## Requirement-to-evidence matrix

| Requirement | Evidence and conclusion |
| --- | --- |
| Directive criterion 1, lines 14–15: retire only the two named artifacts and prevent re-add | Git tree metadata confirms both paths absent; selected range deletes exactly those two paths. Independent `git check-ignore --no-index -v` confirms the anchored config rule at `.gitignore:28` and retained `.friday/` rule at line 12. No other runtime store deletion or product path change exists. `audit.json`, `ignore.stdout`, `commands.json`. |
| Criterion 2, lines 16–19: original/fixture option parity, unchanged fixture, meaningful migration | Private in-memory YAML comparison independently confirms the original, sanitized fixture and retained option ledger have the same 406 paths; original/fixture hashes and original blob metadata match. Fixture base/candidate bytes are identical. Safe test diff removes the obsolete original-vs-fixture test and redirects the example baseline to `_load_fixture()`; the existing behavior-section assertion remains unchanged, with no skip or self-comparison. Remaining config loading, missing-placeholder, diagnostics, traceability and secret checks remain. `audit.json`; test file lines 42–97 and remaining tests; independent compatibility run 30 passed. |
| Criterion 3, lines 20–24 and scope clarification lines 48–55: bounded removal and honest exposure disclosure | Complete range inspected without emitting deletion contents. All 48 added/modified blobs scanned privately against eight known exposed literals: no matches. Added evidence contains no original values or credential-bearing baseline copies. Packet records 54 remaining paths (52 SQLite/backups, one finance integration test, one accepted archive) and historical exposure. All 54 proposal blob IDs match current tree metadata; this verifies disclosed locations without repeating a broad content scan. No issuer validity calls occurred. `audit.json`, authority, directive, additional-exposure-summary and execution log. |
| Criterion 4, lines 25–27: focused tests, full Chat, static and documentation checks | Independent final-candidate compatibility: 30 passed, including 17 config cases; changed-file Ruff and Mypy, board, docs, render and whitespace exit 0. Full Chat receipt/log evidence: 828 passed, 5 skipped, one deprecation warning, exit 0. Receipt hash/provenance caveat and baseline diagnosis below. No changed-source warning or failure exists. `commands.json`, retained `validation/evidence/*` and `audit.json`. |
| Criterion 5, lines 28–30: stable candidate and fresh read-only review, no premature initiative closeout | Frozen HEAD verified and unchanged through review; board remains started/local with independent-review/provider-rotation gate. This report supplies the full independent work-unit review. Whole initiative stays started pending confirmed replacement/invalidation and maintainer acceptance. No delivery authority inferred. |
| Execution constraints, lines 32–43 | Existing private Python 3.13 environment and unchanged guard used with explicit replacement environment, fresh review-only HOME/TMP/cache, telemetry disabled and synthetic fixture credentials. Guard SHA256 agrees with every retained passing preflight and preserved guard copy; independent guard probe rejects external DNS before resolution. No installs, sync, live integration/provider requests, inherited credentials or shared user stores. Runtime/package source, fixture and package metadata unchanged. `commands.json`, `guard.stdout`, `audit.json`. |

## Commands executed and exact results

All commands used the isolated candidate directory as cwd. Exact argv, replacement environment, timestamps, exit codes and stdout/stderr SHA256 are retained in [commands.json](commands.json). Each output is separately retained beside this report. Independent source audit and evidence inspection results are in [audit.json](audit.json).

| Check | Exact argv | Result |
| --- | --- | --- |
| guard | `/private/tmp/friday-mcp-upgrade/venv/bin/python -c import sitecustomize,socket; print('guard loaded:',sitecustomize.__file__); try: socket.getaddrinfo('guard-denial.invalid',80) except RuntimeError: print('external DNS denied'); else: raise SystemExit('guard did not deny DNS')` | exit 0; guard loaded: /private/tmp/friday-mcp-upgrade/guard/sitecustomize.py; external DNS denied |
| compat | `/private/tmp/friday-mcp-upgrade/venv/bin/python -m pytest packages/friday-chat/tests_chat/compat -q` | exit 0; ..............................                                           [100%]; 30 passed in 3.03s |
| ruff | `/private/tmp/friday-mcp-upgrade/venv/bin/ruff check packages/friday-chat/tests_chat/compat/test_config_compatibility.py` | exit 0; All checks passed! |
| mypy | `/private/tmp/friday-mcp-upgrade/venv/bin/python -m mypy packages/friday-chat/tests_chat/compat/test_config_compatibility.py` | exit 0; Success: no issues found in 1 source file |
| board | `/private/tmp/friday-mcp-upgrade/venv/bin/python scripts/friday-dev-board.py validate` | exit 0; Development board validation passed: 27 tasks |
| docs | `/private/tmp/friday-mcp-upgrade/venv/bin/python scripts/check-documentation-lifecycle.py` | exit 0; Documentation lifecycle validation passed: 580 Markdown files checked |
| render | `/private/tmp/friday-mcp-upgrade/venv/bin/python scripts/friday-dev-board.py render --check` | exit 0; Planning dashboard is current |
| whitespace | `git diff --check 0f5cf2c413092d3c12ae691c547defa22dc3dbc5..a65f1366fcb0baf4cbd1198f75933fe72ad68641` | exit 0; no output |
| ignore | `git check-ignore --no-index -v tests/integration/memory/config.yaml tests/integration/memory/.friday/quarantine/tool_outputs.jsonl` | exit 0; .gitignore:28:/tests/integration/memory/config.yaml	tests/integration/memory/config.yaml; .gitignore:12:.friday/	tests/integration/memory/.friday/quarantine/tool_outputs.jsonl |

Additional read-only commands: `git status --short --branch`; `git diff --name-status BASE..CANDIDATE`; safe path-specific diff for `.gitignore`, compatibility test and board/dashboard; `git ls-tree` for deleted paths and proposal blob metadata; private `git show`/SHA256/YAML reads for baseline hashes and option parity. Deleted contents were never printed or persisted. `git diff --check` returned no output.

## Retained validation evidence and provenance

Independently parsed every passing evidence directory's preflight, receipt, stdout and stderr; output hashes, command argv, product before/after hashes, recorded authority/directive hashes at the named revision, and guard hash all reconcile. All eight retained passing checks exit 0 and have empty stderr. Their SHA256 receipts are:

| Directory | Receipt SHA256 |
| --- | --- |
| candidate-board | `ca7369068bde559a16161abec5f44fde1babbfaa53148f347e733ffe072b2f46` |
| candidate-docs | `409b8d3fa17f4fcd851c914c7cbae96322dc29022a47642adeb8c7adb965dd38` |
| candidate-mypy | `73c72648be3705eba5076e05ff28ad911565554046ff5a9a47cd4a3f5c8a788f` |
| candidate-render | `7517c5c51f693fb7c36201411999bbf3eec4e2d5aebeac98fb0c25cfb7399e43` |
| candidate-ruff | `d88b142200fb5955f4d28bbfd0d243fd1c2ffb3a4bdf84b2023ccaff2d2f55a1` |
| corrected-chat-full | `b9efd44f806681b57bc6a707d566ca355281c6adc37e61efe5cbe744f0d989d3` |
| corrected-compat | `9ed283dbc8be534a8709edf63aad764bc416c5d17675d9e3ff076ed2c611c77e` |
| corrected-config | `066649de5f712bdb1f8c64c093f537c7aa6ce0a4a296eb107352e59027cae2af` |

Important provenance qualification: those preflights name `995d2e875204c010639e9ce74b8f9229f7e59c64`, an earlier authority commit, rather than this frozen candidate. They tested a worktree containing the final four-path product state: every recorded product-before/product-after hash exactly matches the candidate. The earlier revision-to-final diff contains only those four product paths plus this packet's metadata; runtime source, other tests, fixtures, dependency metadata and validation scripts are unchanged. The full Chat result therefore supports these exact product bytes, not a claim that its revision label was the final commit. Independent focused/static/board/docs/render checks were rerun at the final frozen HEAD. No builder summary alone supports a passing assertion.

The one full-suite warning is `DeprecationWarning: Legacy Memory LLM injection is deprecated; provide a TypedLLMClient` at unchanged `packages/friday-chat/src/friday_chat/reorganization/mutation.py:245`. It does not originate in a changed source file. The retired comparison explains the one fewer test than the unchanged-base run.

## Skipped checks; baseline failures versus regressions

The full Chat suite was not duplicated: retained raw logs and receipts were independently verified, tested product bytes match the candidate, and focused checks passed at final HEAD. No specific remaining concern warrants another full run. No repository-wide lint/type suite, broad historic rescan, provider tests, credential-management effects or history rewrite was performed; they are outside the directive/request. No waiver was inferred.

Seven retained earlier harness receipts were independently hash-checked against their recorded digests and stdout/stderr. Initial collection failures name the missing `friday_memory.models.vector_metadata` module; sparse-exclusion correction restored it without changing product bytes. An early suite failed fixture socket/process cases; permitted-loopback rerun reduced this to two subprocess/PTY failures. An unchanged-base run reproduced those two failures. The isolated subprocess output explicitly reports `ModuleNotFoundError: No module named 'tests_chat'`; corrected importable test package paths yield the passing full run with the same guard. These earlier failures remain preserved as infrastructure evidence, not erased or represented as successful checks. No candidate regression remains in the required gates.

## Residual risk and next gate

This is verification of two current-tree removals and their compatibility migration. The eight known values remain disclosed across 54 other tracked paths; Git history and existing clones/copies retain removed material. No scan proves invalidation or erasure. Provider rotation/replacement and disabling old keys remain pending external confirmation. The archived accepted evidence was not modified; deferred proposal actions were not executed.

The controller may record this bounded unit's independent validation and propose its repository-removal work complete. The whole initiative must remain started until provider revocation/replacement is confirmed and maintainer acceptance is recorded. This result grants no push, merge, publication, history rewrite or provider-management authority.

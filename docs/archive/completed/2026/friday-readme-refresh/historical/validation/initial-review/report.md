# Independent README review — CHANGES_REQUESTED

Reviewer: Codex independent review agent `/root/readme_refresh_review` (GPT-6 family; exact serving build unavailable). Review completed 2026-10-15 UTC / 2026-10-14 America/New_York. Mode: fresh-context, read-only aggregate documentation/example review. The request supplied frozen authority and candidate, not builder reasoning. Subsequent controller observations were not used as substitutes for independently reproduced evidence. No candidate edits or delegated agents.

Candidate: `b6dad87b568aee3a81dc20e145bb2644e4796609`, branch `docs/readme-refresh`.
Base: `25bf721cdac21e6cb05bbcae79c6cdba3b1b2065`; reviewed range `25bf721cdac21e6cb05bbcae79c6cdba3b1b2065..b6dad87b568aee3a81dc20e145bb2644e4796609`.

Authority: `docs/planning/active/friday-readme-refresh/authority.json`, SHA256 `30034e9a414c68b65e2933b9bad1ab79b588b53d714cd71eadae9d87d653c1c0`.
Directive: `docs/planning/active/friday-readme-refresh/directives/CD-DOC-001-readme-refresh.md`, SHA256 `73a398a1ac03290817323c20fd06f4e7e831562ab1c5b6de8f045db023984f5c`.

Read authority, AGENTS.md, engineering policy, independent-validation policy and task-lifecycle policy. Reviewed root plus all 16 package README entrypoints for users and contributors, bounded changes, metadata/import/install claims, examples, retained MCP limits, telemetry ownership/privacy and queued Langfuse status, Optimization placeholders, support/contributor links and rendering. Scope excludes unrelated guide rewrites and product fixes.

## Finding DOC-001 — Medium — Finance exception handling overstates implemented normalization

Affected file: `packages/friday-finance/README.md:45`.

Violated requirement: CD-DOC-001 requires accurate implemented behavior, meaningful limitations and assertions checked against published alpha3 APIs/source; the authority forbids source/API changes.

Evidence: the README directs users to handle “typed authentication, rate-limit, timeout and not-found errors.” `packages/friday-finance/src/friday_finance/providers/massive/client.py:49-52` constructs `MassiveAuthError` for a missing key, while `client.py:98-109` maps only exceptions whose message contains `429` to `MassiveRateLimitError` and otherwise uses a bare re-raise. The declared `MassiveTimeoutError` / `MassiveNotFoundError` classes (`exceptions.py:28-37`) have no implementation raise sites. Upstream authentication failures likewise are not normalized to the missing-key exception.

Independent offline reproduction: `review/contracts.py` injects synthetic callables through installed alpha3 `MassiveAgentClient.execute_query`, with no provider request and no real key. A `TimeoutError`, synthetic 404 `LookupError`, and synthetic 401 `RuntimeError` are returned as the exact same exception objects, rather than Friday timeout/not-found/authentication wrappers; a synthetic 429 becomes `MassiveRateLimitError`. Results are in `review/contracts-results.json`.

Risk: a reader handling only the advertised Friday exception classes can miss actual timeout, missing-resource and remote-authentication failures.

Required mitigation: change only the README to distinguish implemented missing-key/rate-limit handling from propagated SDK/transport errors, and avoid suggesting that the declared timeout/not-found exception classes are currently wired into provider failures. Do not implement exception normalization as part of this documentation task.

Required verification: inspect corrected wording against `client.py:98-109`; rerun README render/link/compile checks and confirm the bounded diff remains documentation-only. The existing synthetic reproduction can be rerun if needed; no new product test or live request is required. Documentation impact is this paragraph only; no runtime or configuration change.

## Independently reproduced evidence

- `review/audit.py` checks the frozen hashes, clean status, exact 17 README scope and allowed governance-only additions. No source, API, metadata, version, dependency or lock changes exist in the selected diff.
- All 17 metadata readme paths, version `0.1.0a3` and Python `>=3.13.4` agree. Installation examples and extras were checked against project metadata; all 426 installed member Python source files byte-match the frozen checkout.
- Inspected `/private/tmp/friday-readme-validation/check.py` and its installed audit guard before execution. Reran it with `/private/tmp/friday-alpha3-pypi/production-install/bin/python`: all 22 Python fences compile; 18 offline scenarios exit 0. Manually checked output assertions, including greeting, agent registry, alias SPY, typed request 0.3, MCP child/server echo, ephemeral memory/runtime, mock sandbox, disabled speech, telemetry events/flush, registry and SQLite round trip. Template copying and fake Chat configuration also complete.
- Four explicitly live examples were compiled and source-inspected, not executed: Finance query, Moltbook profile read, local-model completion and real Runtime startup. Imports, constructor/method parameters and prerequisites match source, subject to DOC-001's exception-handling claim.
- `review/contracts.py` independently confirms installed Chat `--help` flags, `--version` output `0.1.0a3`, and the documented debug telemetry YAML against `FridayChatConfig`.
- `review/audit.py` checks 167 README links, local repository targets and used heading anchors. All 17 descriptions render through `readme_renderer.markdown` without warnings; rendered HTML copies are outside the checkout under `review/`.
- Board `validate`: passed, 30 tasks. Board `render --check`: current. `scripts/check-documentation-lifecycle.py`: passed, 603 Markdown files. `git diff --check <base>..HEAD`: passed. These checks ran with isolated HOME/TMP/cache, `UV_NO_SYNC=1`, `UV_OFFLINE=1` and the existing validation environment, without installing anything.
- MCP profile/limits and server/client distinctions match protocol/server source. Telemetry ownership, closed versus generic/legacy content guarantees and optional exporter limitations match factory/config/lifecycle/provider/event source. Optimization modules are docstring-only. No other mandatory README discrepancy was established.

Reproduce the deterministic documentation audit:

```bash
/private/tmp/friday-alpha3-pypi/tools/bin/python /private/tmp/friday-readme-validation/review/audit.py
/private/tmp/friday-alpha3-pypi/production-install/bin/python /private/tmp/friday-readme-validation/check.py
```

Rerun the guarded contract check with `sh /private/tmp/friday-readme-validation/review/run-contracts.sh`; it supplies the same isolated environment/guard used by the sample checker. Audit results: `/private/tmp/friday-readme-validation/review/audit-results.json`; scenario results: `/private/tmp/friday-readme-validation/results.json`; contract results: `/private/tmp/friday-readme-validation/review/contracts-results.json`.

Residual limits: no external URLs were fetched, provider credentials read, provider calls made, Docker started, shared user stores accessed, distribution rebuilt/published or Git remote written. Links are verified against local candidate targets, not remote publication; live provider correctness and complete MCP conformance are outside this documentation review. Markdown checks establish renderability, not screenshot-based GitHub/PyPI visual identity. No broad product suite was run or required. Published alpha3 long descriptions remain immutable. Validation is not maintainer acceptance or delivery authority.

Final freeze check: HEAD remains the candidate on the requested branch and `git status --porcelain` is empty. Result: **CHANGES_REQUESTED** for DOC-001 only; create a fresh frozen candidate after the bounded wording correction and obtain fresh validation.

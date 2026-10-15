CHANGES_REQUESTED

Fresh-context read-only final delta and aggregate review of CD-GUIDE-001 and REM-GUIDE-001, 2026-10-15. Reviewer: Codex agent `/root/guides_refresh_final_review`; exact underlying model/version is not exposed. No remediation, delegation, commits, board mutation or publication performed. The implementation agent's conclusions were not acceptance evidence. The initial independent report was read as prior review evidence, its retained artifacts were hash-checked, and the final candidate was independently checked below.

Frozen input: `/private/tmp/friday-guides-final-review-request.json`. Checkout `/private/tmp/friday-guides-refresh`, branch `docs/guides-refresh`, candidate `6fb53e00877214d813656b204f950c8a0b725d05`. Aggregate base `123d9ed943519c4e68bf9249705e55d1a1ebf8b8`; aggregate range `123d9ed943519c4e68bf9249705e55d1a1ebf8b8..6fb53e00877214d813656b204f950c8a0b725d05`. Remediation base `6691aa2428b81ed96fd8d404f6b3f5a0f1e82f13`; remediation range `6691aa2428b81ed96fd8d404f6b3f5a0f1e82f13..6fb53e00877214d813656b204f950c8a0b725d05`.

Read controlling AGENTS.md, repository engineering policy, development task lifecycle, independent validation policy, authority.json, CD-GUIDE-001 and REM-GUIDE-001; all eight requested hashes match. All 25 original-guide hashes match the aggregate base. The candidate was clean at the requested HEAD before and after the review. `authority-scope-check.json` records exact expected/actual hashes and per-guide comparison. All evidence in this directory is outside the candidate.

GUIDE-003 — Low severity, mandatory aggregate whitespace gate failure

Affected file: `docs/planning/active/friday-guides-refresh/validation/initial-review/replay.log:1-29`.

Authority: CD-GUIDE-001 lines 36-37 requires board/render/docs and whitespace checks; REM-GUIDE-001 lines 28-32 repeats aggregate whitespace verification and permits governance/evidence updates. Independent validation policy permits VERIFIED only when mandatory deterministic checks pass or have an approved waiver. No whitespace waiver applies.

Reproduction:

```bash
cd /private/tmp/friday-guides-refresh
git diff --check 123d9ed943519c4e68bf9249705e55d1a1ebf8b8..6fb53e00877214d813656b204f950c8a0b725d05
```

Observed: exit 2, exactly 29 trailing-whitespace diagnostics in the newly committed historical replay log. For example, line 1 ends `friday-config | ` and line 29 ends `rendered 25 | `. Full output: `whitespace.log`. This file was added during remediation and is in the aggregate committed range; it is not pre-existing base debt. Guide-only whitespace checks pass.

Risk: evidence packaging violates the required branch-wide gate, despite correct guide content and passing behavioral probes. This is a low-impact repository hygiene issue, not a runtime defect, but it is a violated explicit requirement rather than an optional advisory.

Required mitigation: correct the committed representation of the retained log within the authorized evidence scope so the aggregate whitespace command passes. Preserve provenance of the original raw bytes and reconcile relevant artifact/hash manifests; do not silently rewrite the historical independent report or leave stale hashes. A lossless encoded raw artifact plus a whitespace-clean readable representation is one viable approach. Freeze a new candidate and obtain fresh review. No product or guide-content correction is required by this finding.

Verification: rerun the exact aggregate command, verify retained-evidence provenance/hashes, confirm all 25 guides and all 75 code fences are unchanged from this candidate, and rerun the appropriate docs/board checks. Documentation/configuration impact: validation evidence only; no runtime configuration or package behavior change.

Prior findings resolved on this candidate

- GUIDE-001: all four descriptions are corrected consistently in `05-tools.md:148`, `09-cli-reference.md:87`, `09-cli-reference.md:139`, and `13-troubleshooting.md:124`. They retain Chat `tools.context.required_tools`, suppress optional automatic choices, and subject the required/manual union to admission/count/schema budgets. The CLI prose explicitly distinguishes agent-profile `required_tools`; the Tools guide separately identifies profile fields. Source `friday_chat/tools/selection.py:325`, `:667-669`, `:712` and the manual-only candidate branch agree. Independent guarded probes observe manual `('manual_tool',)`, preview and turn schemas `('required_tool', 'manual_tool')`; optional tools stay absent. Replacement, deduplication, clear-to-automatic behavior, unknown names, count rejection and token rejection were also checked. Rejected sets do not enter manual mode. Evidence: `independent-probes.py`, `independent-probes.log`, `retained-contract-replay.log`.
- GUIDE-002: `14-appendices.md:218` marks `web_screenshot` as a stub; the legend at line 79 includes raised and returned unimplemented outcomes. Source `friday_tools/web/fetch.py:112-155` unconditionally returns an unimplemented error. The guarded inert-URL probe returns that error while HTTP-client construction is forbidden. A full static comparison finds 145 named tool classes, 145 catalog rows, no missing classes and no stub/status mismatches. No suggestion that installing a dependency activates this handler remains. Evidence: `independent-probes.log`, `static-review.json`.

Completed independent validation

- `audit.py`, `audit.log`, `authority-scope-check.json`: 8/8 authority hashes, 25/25 original-guide hashes and 14/14 retained initial-evidence artifact hashes match. The remediation changes exactly four guides; other 21 guides and every one of 75 fenced blocks are byte-identical to the initial reviewed candidate. All 60 aggregate changed files are the 25 guides or authorized initiative/board evidence. No source, test, package metadata, dependency or lock change exists. All 19 numbered-guide outline section lists exactly match current level-two headings. Aggregate/remediation patches and structural index retained.
- Inspected and independently replayed supplied `check-guides.py`: 25 coherent metadata records; 29 Python fences compile; 24 complete offline scenarios execute against the installed production alpha3 package, including an owned MCP stdio server/client pair; 34 owning-schema checks pass; canonical model-library/role loading and a non-started real Chat assembly pass; fake CLI interaction passes; all 25 Markdown bodies render; 560 links and 48 local anchors pass; 14 Bash fences pass syntax checking. Zero checker errors. Evidence: `replay.log`, `replay/results.json`.
- Independently replayed the retained contract helper with private paths: the role-specific override loads in its documented canonical configuration; all 48 CLI table commands are registered; the remaining canonical commands are `/help` and `/exit`, explicitly covered by the surrounding prose. Evidence: `retained-contract-replay.py`, `.log`.
- `static-review.py`, `.json`, `.log`: all 16 workspace distributions match installed version 0.1.0a3; all 429 source/template files compared with installed alpha3 are byte-identical, excluding Python caches and OS metadata. Distribution/import/extra inventories reconcile with the reference and examples. Static tool inventory is complete as above.
- Board `validate`: exit 0, 31 tasks. Board `render --check`: exit 0, dashboard current. Documentation lifecycle: exit 0, 612 Markdown files. Commands used UV_NO_SYNC=1, UV_OFFLINE=1, the pre-existing pinned venv and private HOME/cache. No install/sync occurred.
- Guide-only `git diff --check <aggregate range> -- docs/guides`: exit 0. Full aggregate command: exit 2 for GUIDE-003 only.

Aggregate assessment

All 25 current guides were checked for cross-guide terminology, metadata, example ownership, task navigation and consistent implemented/placeholder/queued/application boundaries. The unchanged 21-guide source-review baseline is the hash-verified initial independent report, supplemented here by replayed scenarios, full package/source inventory and current source checks of Chat assembly, CLI precedence, required/manual selection, placeholders and the source catalog. Source-derived distinctions remain consistent across the series: Chat real mode retains deterministic orchestration/speech adapters; headless Runtime and Chat schemas differ; memory quality/persistence/context inclusion differ; native and MCP output paths have different guarantees; provider-neutral Langfuse remains queued.

The aggregate guide restructuring retains complete public-API recipes, canonical model/agent/workflow examples, precise CLI and package references, detailed memory budgeting/recovery, security and speech limits, and source links. The MCP aggregate diff preserves material dated transport/profile, trust, ownership, refresh/result/schema and optional-role boundaries; its added paired stdio recipe works independently of repository test fixtures. No product scope drift or additional substantive guide finding was identified. The prior report's all-guide coverage and replay evidence are complete for its stated local/offline profile; its original verdict remains historical CHANGES_REQUESTED.

Review limits and harness notes

No network, provider calls, credential access, hardware/audio, Docker, shared user stores, install/sync, public HTTP listener, publication or full product suite was used. The two live Python snippets and two callable API fragments compile only; external URL reachability and current external tool releases were not checked. HTTP/deployment security prose was compared with retained source/contracts rather than exercised against a live listener. These checks do not establish production certification, provider quality or semantic acceptance.

Two preliminary reviewer probe failures are retained: the guard refused a temporary write because TMPDIR was outside its private replay subtree, then an assertion incorrectly expected the public `manual_names` property to return None rather than its documented empty tuple outside manual mode. Both reviewer-harness errors were corrected and the final guarded probes pass. Neither was a candidate defect. The audit script's initial failure on the real whitespace gate led to GUIDE-003; the final audit records that nonzero outcome explicitly.

Exit gate: repair GUIDE-003's evidence representation, freeze a new commit, and request fresh independent validation. This review does not authorize completion, maintainer acceptance, delivery or product implementation changes.

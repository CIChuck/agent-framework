CHANGES_REQUESTED

Independent work-unit and aggregate branch review of CD-GUIDE-001, 2026-10-15.
Reviewer: fresh-context Codex agent `/root/guides_refresh_independent_review` (exact model/version is not exposed to this agent). Mode: read-only frozen candidate; no remediation or delegation. No builder reasoning or conclusions supplied as decision evidence. The replayable checker was inspected and independently rerun; its assertions were supplemented with independent source inspection, static inventory and contract probes.

Inputs: `/private/tmp/friday-guides-review-request.json`; checkout `/private/tmp/friday-guides-refresh`, branch `docs/guides-refresh`; base `123d9ed943519c4e68bf9249705e55d1a1ebf8b8`; candidate `6691aa2428b81ed96fd8d404f6b3f5a0f1e82f13`; exact reviewed range `123d9ed943519c4e68bf9249705e55d1a1ebf8b8..6691aa2428b81ed96fd8d404f6b3f5a0f1e82f13`.

Controlling authority read: AGENTS.md; repository-engineering-policy.md; development-task-lifecycle.md; independent-validation-policy.md; initiative authority.json and CD-GUIDE-001-guides-refresh.md. All six requested authority SHA256 values match, as do all 25 guide baseline SHA256 values (`authority-check.json`). Candidate remained clean and at the same commit through final checks. All review outputs are outside the checkout in this directory.

1. GUIDE-001 — Medium: describe the required-tool union when documenting manual injection.

   Affected candidate locations: `docs/guides/05-tools.md:148`, `docs/guides/09-cli-reference.md:87`, `docs/guides/09-cli-reference.md:139`, and `docs/guides/13-troubleshooting.md:125` describe `/inject-tools` as setting the “exact manual [tool] schema set” without stating that configured required tools remain included. A reader can reasonably infer that `/inject-tools manual_tool` exposes only that named tool.

   Actual source: `packages/friday-chat/src/friday_chat/tools/selection.py:325` selects the policy path when `tools.context.required_tools` is nonempty; `:667-669` unions configured required names with manual names, and `:712` selects that union. The manual branch suppresses optional candidates, not configured required tools. This behavior also appears in the installed alpha3 package. The independent guarded probe configures `required_tool`, injects only `manual_tool`, and observes:

   ```text
   manual_names: ('manual_tool',)
   preview_selected: ('required_tool', 'manual_tool')
   turn_selected: ('required_tool', 'manual_tool')
   ```

   Violated authority: CD-GUIDE-001 lines 14-18 requires accurate public API/configuration/CLI behavior and precise integration boundaries; lines 30-35 requires checking command behavior against source. Risk: incorrect expectations about which schemas remain visible and why a seemingly small manual set can consume budget or fail selection.

   Required mitigation: correct all four descriptions consistently. Explain that manual mode suppresses optional automatic choices but retains `tools.context.required_tools`; those names and the manually requested names must fit the same admission/budget policy. This is a documentation correction; do not change selection behavior under this unit.

   Verification: rerun the independent required-plus-manual probe, then ensure the Tools guide, CLI table/prose and troubleshooting guide describe that result. Documentation/configuration impact: expose the existing `tools.context.required_tools` interaction explicitly, distinct from agent-profile `required_tools`.

2. GUIDE-002 — Medium: mark the screenshot tool as a stub.

   Affected candidate location: `docs/guides/14-appendices.md:218` marks `web_screenshot` / `WebScreenshotTool` as “implementation present.” The catalog defines a stub as an explicit unimplemented operation at lines 77-80, and presents the status column as a guide to capability availability.

   Actual source: `packages/friday-tools/src/friday_tools/web/fetch.py:112` labels the class a stub; `:120` says “Not yet implemented”; `:150-155` unconditionally returns an error explaining that screenshot functionality is not yet implemented. The independent guarded probe calls it with an inert `https://example.invalid` argument and gets that error without network access. An independently generated AST inventory covers all 145 statically named tool classes and identifies this single catalog/stub classification mismatch (`static-review.json`).

   Violated authority: CD-GUIDE-001 lines 14-18 requires accurate claims and real public APIs; line 23 prohibits presenting plans as implemented capabilities. Risk: an integrator selects an unavailable screenshot operation on the strength of the verified catalog.

   Required mitigation: change this row to “stub” and, if useful, state that an application-supplied browser implementation is required. No runtime/tool implementation work is authorized here.

   Verification: repeat the catalog/source comparison and offline stub probe; all explicit unimplemented tools should be classified consistently. Documentation/configuration impact: catalog status only; do not suggest installing Playwright alone makes this handler functional.

Validation evidence and scope

- `authority-check.json`: 31/31 requested authority/baseline hashes match. HEAD/branch/clean status and `git diff --check <base>..<candidate>` checked before and after review. Exact guide patch retained in `guide-diff.patch`, structural change index in `guide-diff-structure.txt`, and full changed-file statistics in `diff-numstat.txt`. All 38 changed files are guides or authorized initiative/board evidence; no product source, tests, dependency/metadata/lock changes.
- `replay.log` and `replay/results.json`: independently reran the inspected supplied checker via the pinned Python, with private HOME/TMPDIR, synthetic data and a Python audit guard against network, credential-file/shared-checkout access and writes outside private output. 25 guides have coherent version/date/title/description/status/audience/type metadata; all 29 Python fences compile; 24 complete offline scenarios execute, including paired owned MCP stdio client/server; 34 owning configuration-schema checks pass; canonical Chat config and role resolution pass; non-started real Chat assembly confirms Framework model/memory plus deterministic orchestration/speech adapters; CLI fake interaction and all 25 Markdown renders pass; 560 parsed links with local-target existence checks and 48 local anchors checked; 14 Bash fences pass syntax checking. Zero checker errors.
- `independent-contract-probes.py` / `.log`: independently reproduce GUIDE-001 and GUIDE-002; additionally load the service-specific override fragment in its documented canonical context and compare the CLI table against the real registry. All 48 table commands are registered; the remaining two canonical commands are `/help` and `/exit`, explicitly covered by surrounding prose.
- `static-review.py`, `.log` and `.json`: independent metadata/import-directory/extra inventory for all 16 workspace packages; all are version 0.1.0a3 and match installed versions. All 429 package source/template files compared against installed alpha3 have identical bytes (OS `.DS_Store` and Python caches excluded). All 145 statically named tool classes have catalog rows; the screenshot status is the single detected stub classification mismatch.
- `board-validate.log`: `friday-dev-board.py validate`, exit 0, 31 tasks.
- `board-render.log`: `friday-dev-board.py render --check`, exit 0, dashboard current; no mutation.
- `documentation-lifecycle.log`: `check-documentation-lifecycle.py`, exit 0, 610 Markdown files. Its subprocess uses UV_NO_SYNC=1, UV_OFFLINE=1, the existing pinned venv, and private HOME/cache; no sync/install.
- `reproduce.sh`: exact replay commands using existing pinned tools and private output. Two preliminary reviewer-harness failures are preserved separately: initial probe omitted TMPDIR and the audit guard refused a temporary-file write; the initial CLI comparison failed to normalize leading slashes. Both harness issues were corrected, and the final independent probes pass. Neither was a candidate failure.

All-guide substantive review coverage

| Guide | Source/schema/handler basis and assessment |
| --- | --- |
| 01-executive-summary | Package metadata, source/public exports and Runtime/Chat assembly: current scope and alpha/application boundaries are explicit. |
| 02-getting-started | Chat CLI/config/templates, installed resources and episodic API: complete offline start and template-copy recipes replay; live setup labeled. |
| 03-core-concepts | Core contracts, Runtime config/kernel, Chat processor and Memory assembler/layout: construction/lifecycle and ownership boundaries reconciled. |
| 04-adaptive-memory | Controller, collection manager, transcript adapters, vector adapter, lifecycle decay/scorer and recovery: examples replay and distinctions preserved. |
| 05-tools | Tool definition/base/registry, Chat registry/selection/loop, sandbox policy: useful recipes, subject to GUIDE-001. |
| 06-agents | Profile, loader, registry, interactive/autonomous classes: schema/default/factory/cache/placeholder descriptions checked; loader recipe replays. |
| 07-multi-agent | Orchestrator, registry, namespace policy/controller/coordinator, Chat assembly: routing/policy recipes replay; deterministic Chat and host concurrency limits explicit. |
| 08-workflows | Workflow models/loader/engine and Chat adapter: canonical/flat files load and validate; approval, artifacts, dispatch and deterministic adapter limits retained. |
| 09-cli-reference | CLI, command registry and tool/transcript/reset/replay handlers: options, command membership and material side effects checked, subject to GUIDE-001. |
| 10-configuration | Chat parser, model library/controls, RuntimeConfig and templates: complete configs resolve; role override separately replayed; schema/path/env/application distinctions checked. |
| 11-advanced-topics | LLM typed requests/capabilities, Telemetry config/factory/lifecycle, Sandbox and MCP source: recipes replay; provider ownership/deployment limits explicit. |
| 12-use-cases | Tools/Transcript composition, Chat/framework boundaries, Finance provider client and optional packages: offline composition replays; designs separated from shipped applications/semantic acceptance. |
| 13-troubleshooting | Same owning loaders/handlers/backends: diagnostics preserve state and distinguish failures, subject to GUIDE-001. |
| 14-appendices | All package metadata and all 145 statically named tool classes: complete inventory/navigation, subject to GUIDE-002. |
| 15-contributing | Workspace metadata, AGENTS and current policies/scripts: paths and authority/review/check boundaries reconciled. |
| 16-desktop-deployment | Chat CLI/templates/config and metadata: explicit configuration/state/launcher conventions, fake/real setup and rollback limits retained. uv installation commands were syntax/source reviewed, not executed. |
| 17-mcp-client | Runtime MCP configuration/provider, client protocol/stdio/adapter, Chat output/ingestion: full config stanzas validate; owned modern round trip replays; admission/result/refresh/ownership contracts retained. |
| 18-mcp-server | Modern registry/server, protocol limits, stdio and HTTP policy/source: explicit registration recipe replays with client; HTTP fragment compiles; detailed bounded schema/lifecycle/trust contracts retained. |
| 19-mcp-migration | Package metadata, pinned local protocol contract and dated client/server source: transport/profile matrix, explicit upgrades, role exclusions and rollback preserved. |
| FRIDAY-FEATURES | Current source/metadata/board: implemented, deterministic, stub and queued distinctions substantially accurate; follows owning guides. |
| OUTLINE | All guide headings and subject owners: structure and links correspond to current guides. |
| README | All 25 documents and reading paths: working task navigation and consistent release/example conventions. |
| memory-management-guidelines | Assembler pruning cascade, layout defaults/arithmetic, budget models/monitor, background coordinator, decay/inclusion source: formulas/defaults/order and caveats checked; monitor recipe replays. |
| security-configuration-guidelines | Core models/sanitizer/quarantine, agent processor and Chat helpers/MCP output: owning schema and scanner example replay; per-path limits and retention distinctions checked. |
| speech | Standalone config/service/selection/playback/harness/Picovoice and Chat assembly: disabled/selection recipes replay; live provider and deterministic Chat limits explicit. |

The large legacy-guide contraction retains a technical series with working public-API recipes, schema examples, a source catalog, current CLI/config references and implementation links. It removes old non-existent APIs, unsafe state-reset advice and unsupported deployment/compliance assertions. The MCP diff preserves the material pre-existing transport/profile, trust, ownership, result, refresh and schema constraints; additions make the stdio recipe independently usable outside repository test fixtures. No MCP contract regression identified in this documentation diff.

Limits and residual risk

No network, live provider, credential, hardware/audio, Docker, public HTTP deployment, paid API, shared user store, package install/sync, push or publication was used. External URL reachability and external tool release behavior were not checked; the reviewed implementation and captured local contracts are the basis. The live Runtime startup and ElevenLabs snippets compile only. The refresh and HTTP constructor fragments compile; their surrounding source contracts were inspected. HTTP security/cleanup claims were source/contract reviewed, not re-exercised against a live listener. No full product suite was run, as explicitly excluded for this documentation-only unit. These checks establish documentation/reproducible offline behavior within the stated limits, not provider quality, semantic acceptance or production certification.

Exit gate: correct GUIDE-001 and GUIDE-002 within the authorized guide scope, freeze a new candidate and request fresh independent validation. This report does not authorize acceptance, delivery or runtime implementation changes.

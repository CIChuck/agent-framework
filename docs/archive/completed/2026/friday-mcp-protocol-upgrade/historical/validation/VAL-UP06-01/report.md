# MCP-UP-06 independent aggregate review

**BLOCKED**

Reviewer `/root/mcp_up06_fresh_aggregate_validator`, separate fresh read-only Codex agent, GPT-6 family (exact serving model/version unavailable), reviewed on 2026-10-14 UTC / 2026-10-13 America/New_York. Candidate `92c6f6742df9be84b7046a89a830a6dcc3f67dc8`; product commit `72246581126d4c4d067cce927fee9406413c3ca6`; whole-feature range `1302b5fe3091304c08d1df77ea5fb1d2a4ec3666..92c6f6742df9be84b7046a89a830a6dcc3f67dc8`; accepted UP-06 baseline `c90ed023a053943b63d085b70452bbbb11dd28e9`.

The controlling closeout instruction is contradictory with the canonical lifecycle and unmodified board checker. A defensible full aggregate verdict cannot be reached under the frozen authority. This is an authority blocker, not a demonstrated runtime failure. No `VERIFIED`, whole-feature conformance, completion proposal, maintainer acceptance or delivery authorization is supplied.

## VAL-UP06-001 — contradictory closure authority

CD-MCP-UP-006 step 7 (`directives/CD-MCP-UP-006-aggregate-migration-closeout.md:63-66`) requires a completed/local whole-initiative review index while retaining frozen original authority paths. AGG-AC-12 (`:83`) and `up06-aggregate-contract.md:125-130` further require a review-packet index linked to immutable active historical authority, without moving/rehashing frozen originals. The active `docs/planning/active/friday-mcp-protocol-upgrade/README.md` is explicitly pinned by the request/authority at SHA256 `af1c1e6c9cc5a532a0d99cdab0674c449b7d8e689fbc9fed6f492c5d005d459b` and must remain.

Higher controlling `development-task-lifecycle.md:61-78` requires completed/normal work under `docs/planning/review/` and one current task packet README. The current checker has no immutable-backing exception: `_current_packet_paths` (`scripts/friday-dev-board.py:190-200`) inventories every lane directory with README; `validate_board` (`:276-281,346-357`) requires the state-derived lane and rejects inventoried packets absent from the board. Its frozen source is retained in [inputs](inputs/scripts/friday-dev-board.py).

The original checker [read-only in-memory probe](closure_probe.py) returns these reproducible results ([raw](checks/closure-probe/stdout), [receipt](checks/closure-probe/receipt.json)):

1. Actual current candidate validates without errors and inventories the frozen active packet.
2. Hypothetically marking this same task completed while retaining its active packet yields `tasks[24].packet must be under docs/planning/review/ for state=completed, condition=normal`.
3. Hypothetically pointing it at the required review index, while preserving the frozen active README and adding the review path to the in-memory inventory, yields `current planning packet is absent from board: docs/planning/active/friday-mcp-protocol-upgrade/`.

The hypothetical review directory was deliberately not created. The separate `packet does not exist` message is an acknowledged simulation artifact; it is not the finding. The unregistered-active-packet error follows the actual checker set difference and survives creating the review README. Only an in-memory deep copy of the board and simulated inventory entry changed; no checker logic, candidate files or actual board were modified. A shadow task, removal/renaming of the frozen README, inferred historical exemption, or unapproved checker change cannot silently supply missing authority.

**Exact exit gate:** Chuck Russell must approve a concrete bounded reconciliation of the immutable active-authority backing with the canonical completed review packet, including exact policy/checker semantics and any additional authorized files/tests beyond the current eight-path product budget, or expressly authorize a different pin-preserving migration and reconcile its frozen-path constraints. Any approved implementation must produce a new stable candidate and revised exact review authority, followed by fresh full independent aggregate validation and every required check. The validator makes no repair and infers no exception. Independent-validation policy `:64-66,217-223` explicitly requires stopping for contradictory authority and reporting `BLOCKED`.

## Inputs and unaffected inspection

Read candidate AGENTS, engineering/lifecycle/independent-validation policies, exact `validation-request-UP-06.json`, approved `authority-UP-06-amendment-001.json`, parent CD006/contract and fixture-only AMEND001 with separate approval receipts, initiative build/profile/role contracts, five accepted unit receipts and original reports, current aggregate test source and migration guidance. Frozen proposed labels are historical; matching separate receipts grant the exact scope. No builder private reasoning or verdict was inherited. Historical reports are required input evidence, not present aggregate conclusions. Policy memory was consulted only for governance navigation; current candidate policy supplied the controlling evidence.

[Scope audit](scope-audit.json) inventories all 9,186 whole-feature changed paths: 67 products and 9,119 governance/evidence paths. [Full selected diff](full-product.diff) includes the complete product diff plus selected archive closeout records; [UP-06 diff](up06-product.diff) independently confirms exactly the eight approved documentation/test/fixture paths relative to the accepted baseline. The amended authority freezes 74 of 78 accepted products, because three accepted guides/README and the explicitly approved fixture may change. The runner snapshots 82 current source paths: those 78 plus four additional approved paths. The original parent freeze count was 75 before the fixture exception; the operative amended count is 74. All 19 metadata pins match. [Initial integrity](initial-authority-integrity.json) verifies 181 listed control/manifest/product/metadata/tool hash rows without mismatch.

All 19 complete original primary captures have matching stored hashes, decoded hashes and sizes, independently checked from their original frozen inventory and retained safely under [primary-captures](primary-captures/). [Capture inventory](primary-capture-integrity-and-clauses.json) preserves 725 normative-line inventory entries from dated 2026 and explicit 2025 sources/schemas. This verifies capture completeness/integrity; it does not claim semantic conformance to every clause. No public refresh was performed. All 235 entries of current builder archive match their stored/decoded size/hash contracts ([archive integrity](builder-archive-integrity.json)); builder maps/excerpts were navigation only.

[All 20 criterion dispositions](criterion-dispositions.json) retain all twelve aggregate requirements and all eight initiative dependencies. AGG-AC-11/12 and UP-AC-08 remain blocked; other full-criterion verdicts remain undetermined. Source/example/subset execution observations are not a complete requirement/field/null/bounds/privacy ledger or whole-feature PASS. Full semantic diff/interaction/field review stopped at the governing conflict.

## Checks actually executed

Exactly nine of the 24 required commands completed normally with the unmodified frozen `run_check_UP06_amend1.py` and fresh `independent-UP06-001-*` labels. Exact argv, per-command allowlisted environment, candidate/source/control/metadata hashes, stdout/stderr hashes and timestamps are in each receipt/preflight. The one additional in-memory closure probe exited 0 and demonstrates the blocking condition, not product conformance.

| Required command ID | Raw exit | Observation | Evidence |
| --- | --- | --- | --- |
| board | 0 | 26 tasks valid | [raw](checks/board/stdout), [receipt](checks/board/receipt.json) |
| next | 0 | MCP aggregate review selected | [raw](checks/next/stdout), [receipt](checks/next/receipt.json) |
| show | 0 | started/granted; named feature branch; in-review gate | [raw](checks/show/stdout), [receipt](checks/show/receipt.json) |
| aggregate-examples | 0 | 49 passed in 24.64s | [raw](checks/aggregate-examples/stdout), [receipt](checks/aggregate-examples/receipt.json) |
| documented-configs | 0 | 33 passed, 16 deselected in 6.93s | [raw](checks/documented-configs/stdout), [receipt](checks/documented-configs/receipt.json) |
| server-focused | 0 | 1108 passed in 21.19s | [raw](checks/server-focused/stdout), [receipt](checks/server-focused/receipt.json) |
| server-http | 0 | 706 passed in 16.22s | [raw](checks/server-http/stdout), [receipt](checks/server-http/receipt.json) |
| original-clients | 0 | 1505 passed in 23.11s | [raw](checks/original-clients/stdout), [receipt](checks/original-clients/receipt.json) |
| mcp | 0 | 2679 passed in 67.89s (0:01:07) | [raw](checks/mcp/stdout), [receipt](checks/mcp/receipt.json) |

The remaining fifteen required checks were **not run** after the controlling conflict: cross-package/core-runtime-chat-telemetry, candidate root, fresh baseline root, changed Ruff, candidate/baseline root Ruff, narrow/MCP/full/baseline Mypy, docs, render, whitespace, and candidate/baseline column Mypy. [Command dispositions](command-dispositions.json) enumerates all exact 24 commands and their executed/not-run state. Consequently the exact 327 diagnostic-and-fix object comparison, four column diagnostic objects, complete root warnings and nine grouped skip rows were **not independently re-established** by this review. Builder/prior counts or results do not close those gates.

The controller explicitly directed stopping additional costly required-profile repetition once contradictory authority was reproducibly established. The current owned MCP child finished normally before the paused outer profile controller received SIGTERM/SIGCONT; no test child was interrupted. Outer controller exit 143 is the deliberate orchestration stop, not a child test failure. [Stop record](stop-at-conflict.json) and [failed read-only probes](failed-inspection-probes.json) retain the process-inventory sandbox denial, absent optional candidate-local skill directories and interim missing receipt probe. No failed attempt was rewritten or deleted.

## Integrity, effects and residual limitations

[Final integrity and chronology](final-integrity-chronology.json) compares the first frozen-runner preflight with final actual 82 source / 76 control / 19 metadata / 74 preserved-product hashes, authority, original UP05 runner, UP06 runner and guard. Every corresponding object is equal. Candidate and accepted baseline remain clean at their exact dispatched HEADs. This is governed-file preservation; no claim of all-runtime-file equality is made. Shared root product/state was not inspected or edited.

Actual library snapshots [before](library-review-before.json) and [after](library-review-after.json) each rehash all **22,009 references / 21,992 unique paths / 192 distributions**, preserving the 17 identical overlapping references. Every expected hash matches, both full actual dictionaries and original input hashes are equal, and strict chronology is verified: before snapshot ends 2026-10-14T02:30:13.611049+00:00; first child starts 2026-10-14T02:30:17.094868+00:00; last actual child ends 2026-10-14T02:33:05.737434+00:00; final actual snapshot starts 2026-10-14T02:33:55.359455+00:00. The copied helper uses new phases and evidence output only; no prior helper/sample was overwritten.

Only approved named synthetic stdio fixtures, literal-loopback verified private TLS JSON/SSE, official SDK/deterministic/ASGI counterparts and original guarded fixture effects were used. Authorized loopback escalation was used. Per-command private HOME/TMP/checker cache and transient check outputs are outside the safe artifact archive; approved ignored synthetic relative-CWD outputs remain untouched. No nonloopback/public DNS/provider/user-store/secret access, installs/sync, production service/publication, git mutation or repair occurred. The guard and frozen runner remain unchanged. Protected excluded contents were not read. Fake non-MCP Runtime/Chat services keep model/storage inert while real YAML/public registry boundaries execute in the subset tests.

Fresh context shares environment/tools and supplied exact authority/effect inputs with the controller; no builder reasoning/conclusions were used. No further agents were spawned. Optional OAuth/MRTR/Tasks/interactive/agent/resource/prompt roles, real credentials/deployment/providers and full independent aggregate conformance remain unverified. The blocking condition does not imply an unobserved runtime regression or invalidate historical bounded unit acceptance.

The explicit SAFE [evidence manifest](evidence-manifest.json) lists each original review artifact by relative path, bytes and SHA256; it excludes runtime HOME/cache/TMP/stores, private TLS keys, .git and bytecode. Its self-entry is excluded because a manifest cannot hash itself. Every listed entry is verified at seal, and report/manifest SHA256 are delivered separately. No evidence bytes are mutated after seal.

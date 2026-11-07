# RET-001 implementation evidence

Status: local implementation complete; final after/installed checks pending
Execution phase: implementation
Validation state: not_ready

Approved directive SHA `b760a9a8f8b94e120e5d26914d9bdf45f037a6a3f7f9552cd3d4054d829da9df`, source baseline
`6f291ca5755a616d9185c86dff104b660a1fba8c`, actual approval-preparation HEAD
`87102cd61848b763cbe13e9e605f7584ba517739`. [Approval](../../approval/command-retirement.md)
records the exact maintainer decision including RET-GATE-01–03. No future unit
or delivery is authorized. Source equality was established before editing.

Removed only specified catalog/handler/helper/import/admission entries and four
CommandContext fields. Retained handler/parser/metadata behavior is preserved;
custom registries may still register old spellings. Seven current guides remove
unsupported instructions. Historical matrices, source inventories and fixtures
remain unchanged. [Assertion ledger](assertion-disposition.json) preserves all
519 original function/assertion records:23 changed/retired nodes fit the approved
map and496 original function ASTs are identical. New tests cover216 seeded/
tripwire/absent-runtime negatives plus catalog, fields and registration freedom.

Before:826 Chat,145 foundation/cohort,155 CLI pass; lint and three-source mypy
pass. Guard self-tests deny DNS/public bind/unowned loopback/real stores and
allow owned loopback. Current metadata fields match the immutable50/3 oracle.
The controller's first metadata comparison incorrectly included planning-only
PAR annotations; its failure is a harness error, not product drift. It was
corrected using frozen Git source and the seven metadata fields. The before
functional suites and source hashes were already captured before source removal.
A working Chat run after mapped edits passed1038 tests; final candidate checks
will be recorded separately. Two early replacement fixtures needed proper public
selection synchronization and a runtime for /memory; only test setup was corrected.

Before broad limits:534 root Ruff findings; one existing root pytest test_display
collection collision;37 whole-Chat format failures. Preserve their exact source/
input attribution rather than introduce new failures or claim broad success.
All after-change commands, artifact/current-input equivalence, versions, scope
audits and independent outcome are still required before VERIFIED. Root stores,
providers and external application destinations remain blocked.

Raw receipt location: `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/friday-retirement-8py3ou5y`. Original before manifests,519-node assertion
inventory, guard scripts/hashes and per-command logs are retained there. The
final request/receipt will bind their identities. Two uncommitted working example
configurations remain byte-identical and excluded from commits/artifact inputs.

# RET-001 — builder implementation and verification

Status: builder checks complete; fresh independent validation pending
Execution phase: validation
Validation state: in_review

[Exact approval](../../approval/command-retirement.md) binds CD-CMD-RET-001 SHA
`b760a9a8f8b94e120e5d26914d9bdf45f037a6a3f7f9552cd3d4054d829da9df` and source base `6f291ca5755a616d9185c86dff104b660a1fba8c`.
Intervening administrative commits were product-identical before editing. Actual
builder start is the approval-preparation commit recorded in Git history; the
source artifact candidate is `97e75b062aa5f826fbf9e528bb18dd18b747804e`. Final review request binds
the later evidence/status-only candidate and exact diff. No further product
change follows that artifact candidate.

Removed only the approved nine catalog/handler entries, 11 registry functions,
seven tools functions, related unused imports/exports, run-tool admission entry
and four CommandContext fields. All retained source function/class ASTs are
identical to the approved source base after excluding exactly those four fields.
Generic registration/parser/help and retained /tools behavior remain unchanged;
custom registries can still register an old spelling. No defaults enter the
neutral foundation; no dependency/lock/runtime/TUI change. Seven allowed guides
remove unsupported instructions without invented replacements or notices.

[Assertion ledger](assertion-disposition.json):519 original test functions;23
changed/retired nodes are governed by the directive's map;496 function ASTs remain
identical. Seven slash-only tests retired,219 added checks including216 negative
parameter cases produce the net212 increase:826 before to1038 after. Retained
selection/budget/model-byte/retrieval/PTY/cleanup guarantees use existing APIs.
Nine PAR ledger rows are implemented/pending independent review; historical
source handlers/line snapshots, source inventory and metadata fixtures preserved.

## Actual checks

| Check | Before | Final after |
| --- | --- | --- |
| Full provider-free Chat, committed-example/xterm control |826 passed|1038 passed|
| Foundation/cohort |145 passed|145 passed|
| Framework CLI |155 passed|155 passed|
| Focused lint |pass|pass|
| Three-source mypy |pass|pass|
| Full selected format |37 older failures|36 failures; no new file failure|
| Root Ruff |534 errors|same534 errors, focus passes|
| Root pytest |one test_display collision|same single collection error|
| Board/metadata/lock |36 tasks/18 projects/214 packages|pass, same scope|
| Docs lifecycle |858 files pass|859 files pass|

Guard self-tests establish forbidden DNS/public-bind/unowned-loopback/real-store
actions fail and disposable owned loopback works. Application imports use the
pinned guard plus the directive's DNS/bind supplement; sanitized environments,
no bytecode/pytest/Ruff cache, scratch mypy cache, no downloads/root-venv sync.
Before and after logs remain separate. Whole-file formatting of one mapped
test module fixed a newly detected import-layout regression with identical AST.
No original fixture was softened or new skip/xfail added.

## Clean artifacts and installed proof

Fresh Chat wheel/sdist built from candidate Git export, never dirty examples.
The default129-version install initially lacked local Friday package wheels;
built11 unchanged workspace dependencies offline from the same Git inputs, as
permitted by the directive. No external dependency resolution was used. Final
Chat build uses the final candidate export; reused11 packages are proven equal
to that export. The Chat artifact checker and installed dependency check pass.

Outside checkout with isolated -I -B and guard before imports: exact41 canonical
names/three aliases, all retained metadata equal the pinned oracle projection,
216 no-effect cases, focused help, exit/clear aliases, Chat --help, finance/SDK
imports and no friday launcher pass. All390 wheel source/data members equal
Git inputs and isolated installed files; all129 versions equal frozen profile.
All sdists are compared with matching candidate project files, including Hatch's
inherited root .gitignore. No user config/state/credential enters artifacts.

## Controller harness corrections and limits

The initial metadata probe compared whole planning rows including three PAR
annotation columns; corrected to the seven metadata fields using frozen Git
source. Before tests/source hashes were already captured. Two new test fixtures
needed public selection synchronization and a runtime for the memory metric;
corrected setup only. Initial installed source checks incorrectly mapped nested
config-template and inherited .gitignore paths; corrected to exact project/root
Git paths. Failed diagnostic receipts remain preserved; only final proof is
claimed successful. An initial artifact search included unrelated foundation
negative-fixture directories; the failed install completed no profile. Final
installation uses only freshly built exact workspace wheels and frozen versions.

Root lint/collection/old-format debt is not passing; no implicit waiver. No full
optional-cohort, live provider/tool/user-store, physical terminal/audio or full
platform/TUI/refactor acceptance. Both original working examples are unchanged
and excluded. [Durable receipts](receipts.json) hold actual argv/exits/probes,
version/artifact/source/guard hashes and selected logs; raw large manifests/logs
remain under `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/friday-retirement-8py3ou5y`. Fresh independent review must verify current inputs and
all criteria, not inherit builder conclusions. No push/PR/merge is authorized.

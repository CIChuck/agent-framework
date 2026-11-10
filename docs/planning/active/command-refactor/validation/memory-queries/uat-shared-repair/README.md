# Shared entity-quote and ingestion repair — candidate

Status: round1 requested3 current-document corrections; correction1 awaits fresh
OpenAI review. Runtime/tests/artifacts remain frozen at47134ad6.
[Correction](correction1/README.md); [original review](review-round1/report.md).
[Directive](../../../remediation/REM-CMD-MEMQ-UAT-003-shared-quote-ingest.md) and
[approval](../../../approval/memory-queries-shared-uat-repair.md) record the current
maintainer instruction. Base0e5c3237; the earlier Chat-only proposal remains held.

Shared Friday Commands normalizes one matching outer quote pair at the entity
handler, after determining raw lowercase nodes mode. The global parser and Chat
projection remain unchanged. A shared Memory metadata builder omits absent
optional descriptions; Chat uses it for both ingestion branches. Explicit empty
and non-empty descriptions, chunk counters and protection are preserved.

Builder observations: focused37, Commands/cohort621, controlled Chat1420/5skip,
CLI155, relevant Memory183 pass with canonical origins at collection/finish/after.
The controlled Chat fixture lane uses committed private YAML fixtures; the2 known
raw dirty-example failures remain failed/unwaived, inspected from the prior
verified diagnostic evidence rather than rerun here. Original76-row fixture stays
byte-exact:67 unchanged +1 fully asserted quote-row change +2 kind refusals +6
approved optionR superseded rows. Only the two precisely allowed old tests change.

All4 current mutants have named CALL AssertionError witnesses, with unchanged
control28 passing and3 canonical private-copy origin boundaries. Product exceptions
and setup failures earn no credit. Changed-path Ruff/mypy3, new formatting and both
no-new-debt inventories pass; adapters.py retains47 baseline format fragments.
Root/whole-file formatting/dirty-YAML whitespace debt remains failed/unwaived.

Offline affected wheels and installed checks are recorded in exact receipts.
No full historical D0-D3 replay is claimed. No model/provider/config/budget,
maintenance behavior, personal store, dependency/lock, migration or user-data change.
Human results for all3 issues are pending; the diagnostic patch does not repair
the actual verification reply. [Combined retest](../../../uat/memq-repair-retest.md).

Excluded attempts: the first real-graph test incorrectly expected uppercase NODES
not to match a fixture node named nodes; the existing case-insensitive graph lookup
correctly selected it as an ordinary name. The expectation was corrected with exact
read-call assertions, without changing product behavior. The first private mutation
setup lacked a parent directory and ran0 tests; it is preserved, excluded and
superseded by a new private control/copy set. No supplied input or user state changed.

[Exact evidence](evidence.json); [installed proof](installed_repair_probe.py).

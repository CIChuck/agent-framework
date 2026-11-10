# MEMQ directive council round3 — CHANGES_REQUESTED

Scope: directive/design readiness only. Frozen reviewed candidate:
`818b42eeca4495cf34292e934dbdac34e31ca4db` on `feature/command-retirement`.
Two correction cycles are consumed; remaining findings return to Chuck Russell.
No automatic further correction or review was initiated.

| Seat | Outcome | Advisory score | Exact original report |
| --- | --- | --- | --- |
| GPT-6.1 Sol/high | BLOCKED: reviewer isolation | 9.4/10 | [Sol](sol.txt) |
| GPT-6 Astra/high | VERIFIED | 9.5/10 | [Astra](astra.txt) |
| Claude Opus5.5/high | CHANGES_REQUESTED | 8.9/10 | [Claude](claude.txt) |

The candidate has an open low-severity document finding. The formal council is
also incomplete because the Sol receipt cannot be counted as compliant VERIFIED.
Scores and majority agreement do not resolve either issue.

## Remaining matters

1. **MEMQ-DIR-R3-CLAUDE-001 — Low, candidate document finding.** Reviewed
   README line215 still says “Await separate maintainer direction and approved
   scope for a next unit.” It is in the SESSION acceptance paragraph but has no
   historical/superseded qualifier. CR06/REM2 requires every unqualified current
   instruction to agree. Sol treated this as optional; Astra found the context
   sufficient. The controller retains Claude's finding because the sentence is
   literally an unqualified current imperative. Required correction: explicitly
   mark it historical or point to the current MEMQ gate. No technical contract,
   product, test or dependency change is required.
2. **MEMQ-DIR-R3-SOL-001 — protocol blocker for Sol's formal receipt.** Sol
   wrote `/private/tmp/memq-sol-current-path` outside its assigned fresh scratch.
   Candidate and supplied-evidence identities still match, and no product defect
   was found by that seat. The write violates the explicit isolation rule and
   cannot be repaired retrospectively. The file is preserved; no deletion,
   restoration, waiver or replacement review was performed.

[Evidence](evidence.json) preserves every original report hash, exact frozen
[request](council-request.json)/[manifest](frozen-manifest.json), the matching
precloseout identity audit and the external locator's recorded identity.

[Proposed one-sentence patch](proposed-readme-fix.patch) is concrete and
reviewable, **not applied**. It replaces the last sentence with:

> The post-SESSION instruction “Await separate maintainer direction and approved scope for a next unit” is historical and superseded by the current MEMQ next gate above.

## Criteria and evidence

CR01..05 are resolved by all seats. CR06 is partially resolved because the two
bold current gates and phase labels agree but the old SESSION imperative remains.
Astra passes MR01..10; Sol supports MR01..09 but blocks MR10 on its own conduct;
Claude carries its Low finding in MR01 and supports the remaining design criteria.
No aggregate VERIFIED result is claimed. The raw reports retain full matrices.

Each seat independently reproduced finite76-case captures/replay, four
supplemental cases, guard18/comparator14 controls, correction controls, format
inventory, tooling and board/docs checks. Export reuse differs by seat and is
explicit in the reports. Independent union witnesses reject unchanged-expanded,
missing/extra/nested members at the actual helper assertion; Claude also ran the
real pytest node with canonical private origins. Setup/operator mistakes are
excluded from rejection credit. Marker classes prove membership feasibility,
not future MQ models or whitelist correctness.

The controller inspected these reports/receipts and corroborated source text;
it did not rerun their complete plans or inherit prior verdicts. Current source
and technical authority remain the reviewed bytes. The precloseout audit matches
72 pins,1255 protected files, dirty2, ignored3 and88 supplied raw identities,
plus HEAD/branch/logical index/staging. The subsequent administrative recording
updates current state/history only. The known external locator is preserved.

Existing root Ruff534, root test_display conflict and baseline whole-file
formatting failures remain failed/unwaived. Future D1/D2/D3 implementation,
mutations, builds, installed proof, UAT and acceptance remain unperformed here.
The current README helper is syntactic and cannot substitute for manual semantic
review; expanding it is advisory, not a newly authorized parser project.

## Escalation and stop

The [council skill](../../../../../../../../.agents/skills/council/SKILL.md) says:
“Return unresolved mandatory findings to the human rather than looping indefinitely.”
The [independent-validation policy](../../../../../../../reference/policies/independent-validation-policy.md)
says: “After two unsuccessful remediation cycles, stop and return the unresolved
findings to the maintainer.” This report returns the remaining low document
finding and invalid seat receipt. Additional correction/review needs maintainer
direction. No product D0/D1, acceptance, later-family or delivery follows.

# PILOT-001 D1 — maintainer decision after council round three

Candidate: `19d0b9d1885bfcd89b410d3903968af3ae17b046`.
**CHANGES_REQUESTED**. Claude 9.4/10, OpenAI 9.5/10, Gemini 9.8/10.
All three reviewers confirm correct runtime behavior. The [raw reports and
controller proposal evidence](council-round3.json) preserve their independent
verdicts and the non-majority disposition.

## One mandatory finding: VAL-D1-R3-001

The [general-help sorting test](../../../../../../../../packages/friday-commands/tests_commands/test_pilot.py#L91) reverses `PILOT_SPECS` from
`(help, exit, cls)` into `(cls, exit, help)`, which is already canonical order.
A missing-sort implementation therefore passes its two parameterized cases
and the full existing G1 set. The implementation currently sorts correctly.

Proposed exact change, **not applied**:

```diff
-    catalog = Catalog(tuple(reversed(PILOT_SPECS)))
+    catalog = Catalog(PILOT_SPECS)
```

The unchanged expected output stays `(cls, exit, help)`. The proposed input is
`(help, exit, cls)`, so the assertion now distinguishes sorting from pass-through.
No assertion is weakened and no product, contract or directive change is needed.

Controller scratch reproduction used real pytest with the package import
origin checked and the guard explicitly loaded:

| Test bytes | Implementation | Result |
| --- | --- | --- |
| Current | Scratch no-sort mutant | 2 passed; confirms the coverage gap |
| Proposed scratch copy | Correct current source | 2 passed |
| Proposed scratch copy | Same no-sort mutant | 2 failed, as required |

All original repository test bytes remain SHA-256
`a24550047d774e541e3a8996de12d4ae1c658cde2705dc7f76f142eef5ae77cb`.
The complete original G1 suite has 217 passing tests; the full suite has not
been rerun with the proposed change because it is still an unapplied proposal.

## Proposed bounded continuation

1. Authorize one additional pass for this one-line fixture change only.
2. Apply it, run the full G1 suite and focused lint/format, and retain a
   reproducible no-sort mutation rejection. Verify runtime/frozen inputs and
   both dirty configurations remain unchanged.
3. Freeze a candidate for fresh council delta plus aggregate D1 verification,
   under the existing council-after-deliverable instruction. Do not broaden
   into optional advisories or D2 while the mandatory finding remains open.
4. After D1 conformance reconciliation, continue the already approved D2 and
   D3 deliverables with their own council checkpoints. Whole-pilot acceptance
   and external delivery remain separate decisions.

Two unsuccessful remediation cycles are complete. The
[independent-validation policy](../../../../../../../reference/policies/independent-validation-policy.md#L244) requires returning unresolved
findings to the maintainer at this point. Existing pilot construction approval
is retained; this decision concerns one additional correction/review pass.
No further correction or review is started automatically.

Controller round-three end verification matched HEAD/status/index, all 29
current authority/deliverable pins and all 17,108 protected file hashes before
these evidence/status closeout records. Approved documents, source, tests,
harness, baseline and original dirty configurations remain unchanged.

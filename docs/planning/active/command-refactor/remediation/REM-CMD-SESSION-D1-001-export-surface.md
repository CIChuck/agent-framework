# REM-CMD-SESSION-D1-001 — exact export-surface test

Cycle: 1. Base: `363d67a4f26ef49ab83b1ebb5b06c9ab143d2b31`.
Authority: existing [exact SESSION approval](../approval/session-views.md),
SV-01 and directive SESSION-01; bounded mechanical correction under the
repository independent-validation policy. No new construction approval needed.

## VAL-SD1-001 — mandatory test completeness

Product exports are correct, but `added <= set(api.__all__)` cannot detect an
extra export or loss of a prior name. Change only that assertion/expected-value
block in `packages/friday-commands/tests_commands/test_session_views.py` to an
independent exact ordered 24-name list: preserve the 18 baseline exports and add
exactly the six approved names, with no duplicates. Keep every other test body,
parameter and assertion unchanged; no production/module/README change.

Rerun full Commands/cohort S1, focused Ruff and changed-test format. In private
source copies with canonical import origins checked before and after pytest,
prove an added seventh export and a removed NoData export cause the corrected
test assertion to fail. No setup/collection error earns rejection credit.
An unchanged control must pass. Optionally exercise reorder/duplicate refusal
within that same assertion. Preserve pre-fix test results separately.

Record exact before/after test hashes and test-only AST delta. Keep frozen
contract/directive/preparation, approval, old D1/S0 reports/receipts and all
runtime/model/dependency/lock/Chat bytes unchanged. Clarify ADV-1 in metadata:
the 2,999 count is FunctionDef/AsyncFunctionDef nodes whose name starts test_,
using ast.walk per 277 files, including nested/class nodes; 9,072 counts all
syntactic Assert nodes. Neither number is the pytest collected-case count.

Freeze a new candidate. Obtain fresh delta plus full bounded D1 reviews from
available Claude Opus 5.5 and GPT-6.1 Sol; retain Gemini as unavailable/no score
after the recorded quota failure, without retry or substitute. The selected
three-provider roster remains historical. This availability report follows
the council skill's unreachable-provider instruction and records no invented
maintainer waiver. Controller must reconcile review coverage and current
mandatory findings before advancing to already-approved D2. No SESSION
acceptance, later-family work, delivery or additional automatic loop follows.

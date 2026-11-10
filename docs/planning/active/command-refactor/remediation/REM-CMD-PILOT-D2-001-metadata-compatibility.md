# REM-CMD-PILOT-D2-001 — metadata compatibility amendment and correction

Status: **proposed; maintainer decision required**. No product remediation or
D3 advancement is authorized by this document until Chuck Russell approves it.
Initiative: `friday-command-refactor`. Unit: `PILOT-001 D2`, remediation cycle 1.
Branch: `feature/command-retirement`. Reviewed candidate: `d261f021`.

## Authority and reason for the decision

The [exact pilot approval](../approval/pilot.md) remains in force for its scope.
Its immutable [contract](../pilot-command-contract.md) is SHA-256
`e625123b8222262fb02b32aeadb2cae5c91d18ff573f04763b0af7ea3f22eb8c`;
its [construction directive](../directives/CD-CMD-PILOT-001-help-exit-clear.md)
is SHA-256 `b85be3a04035e1f8318cc6566f7767aad00355b61c49e2650c6327981fd2a982`.
Those original bytes remain unchanged. Approval of this document would add the
bounded PC-04/PILOT-06 amendment below; it would not reopen other decisions.

PC-04 explicitly says: “If another legacy value cannot cross the typed boundary
without an observable change, stop for a contract decision.” The
[round-one council](../validation/pilot/implementation/d2/council-round1.json)
returned CHANGES_REQUESTED: Claude 8.7; Sol VERIFIED 9.6; Gemini VERIFIED 9.9.
One mandatory finding, **D2-PC04-DETAIL-01**, remains. Reviewer scores do not
settle that compatibility decision.

[Independent before/after characterization](../validation/pilot/implementation/d2/detail-characterization.json)
confirms that a custom command with `detail=False`, `0` or `[]` rendered general
and focused help before the refactor, but the new typed projection raises
TypeError. Old general help ignored truthy non-string detail; old focused help
already raised for it. Byte-valued argument text formerly rendered through
f-strings but is rejected by the new typed models. The 41 defaults and all
196 frozen observations still match; this finding concerns custom metadata.

## Decision proposed for approval

1. Preserve falsy legacy detail values by projecting `metadata.detail or None`
   at the Chat-to-shared boundary. `None`, `False`, `0`, `""` and `[]` must produce
   the same general and focused help as no detail. Public Chat registration and
   stored metadata remain unchanged; no stricter registration check is added.
2. Support the declared string types for other text fields, alongside PC-04's
   existing required/default/choices exceptions and the falsy-detail exception
   above. Truthy non-string detail and non-string text fields, such as byte-valued
   argument names/descriptions, are outside the supported rendering contract.
   Help may raise TypeError for these values even where the old renderer printed
   them. This explicitly accepts that limited behavior change for incorrectly
   typed custom metadata. Registration still accepts the same inputs; focused
   and unknown help must avoid unrelated invalid entries.
3. Do not stringify unsupported fields or introduce Any, casts, suppressions,
   another help-selection engine, a new neutral data variant, or new registration
   validation. Valid string metadata and all default definitions remain exact.

Approval would authorize this bounded decision, the correction/tests below and
one fresh three-provider D2 council pass under the existing two-cycle rule.
It would not accept D2 or the whole pilot, grant D3 advancement before D2 council
reconciliation, or authorize push, PR, merge, release or further family/TUI work.

## Correction, allowed paths and non-goals

- In `packages/friday-chat/src/friday_chat/commands/pilot.py`, change only the
  detail projection needed for item 1. No renderer/selection/dispatch redesign.
- In `packages/friday-chat/tests_chat/test_command_pilot.py`, add general,
  focused and async-wrapper regression coverage for all listed falsy details;
  characterize the supported string and unsupported non-string cases; verify
  unrelated invalid metadata is not projected during focused/unknown help.
- Add explicit `@pytest.mark.asyncio` to the new async tests, closing Claude A4
  under AGENTS.md. Do not change existing Chat tests or their assertions.
- Record exact approval with this document's SHA-256 in a new approval record;
  update current packet/board/dashboard/log/authority and new D2 correction
  evidence/reports. Preserve original reports, receipts and their hashes.
- Preserve D1, Chat app/contracts, the other 38 commands, dependency/lock bytes,
  all frozen approved design/harness/baseline files and both dirty examples.
  Other advisories are deferred; no opportunistic refactor is included.

## Required checks and acceptance evidence

1. Compare the falsy-detail cases with the independently captured old outputs;
   prove direct general/focused help and the real shared async help path agree.
   Preserve string detail and cover truthy non-string detail/byte-valued text
   refusals under the explicit decision. Retain lazy unrelated-entry behavior.
2. Run full G2 and G3 commands from the approved directive, plus unchanged G1
   Commands/cohort regression, affected Ruff, seven-source-file mypy, and format
   checks. Report old registry formatting debt separately; no blanket cleanup.
3. Reproduce all 196 frozen observations from a clean Git export of the new
   committed source. Do not alter the baseline, capture program or guard.
4. Recheck existing source/test/assertion preservation, unchanged dependencies/
   lock, metadata, board/dashboard, docs and whitespace. Root lint/collection
   failures remain failed and unwaived; report any new failure as a regression.
5. Freeze a new candidate/request and obtain fresh-context read-only review by
   all three council providers. Assess this correction first, then full bounded
   D2 conformance; advisory scores target at least 9 but never override findings.
6. Reconcile all three results before D3. D3 still owes G4/G5 full regression and
   candidate wheel/sdist/default-install proof, followed by its own council.

Stop if correction needs broader source/API changes, changes observable behavior
outside the explicit decision, alters frozen inputs or requires real stores/live
services. Return new scope decisions to the maintainer; no automatic expansion.

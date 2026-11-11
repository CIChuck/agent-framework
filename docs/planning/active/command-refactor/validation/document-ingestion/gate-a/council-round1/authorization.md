# Gate-A harness directive — council authorization

Recorded 2026-11-11. Maintainer: Chuck Russell.

> Dispatch the council to view the construction directive. To make sure this is tight: no change to production code. Isolated test environment

This authorizes one fresh, read-only design/source-feasibility review by the
established GPT-6.1 Sol, GPT-6 Astra and Claude Opus 5.5 council, at high effort.
All seats assess the complete [directive](../../../../directives/CD-CMD-INGEST-GATE-A-001-readiness-harness.md),
the [criteria](criteria.md) and applicable pinned parents. The target is zero
mandatory findings and coverage/overall scores of at least 9.5 from every seat.
Scores must be honest; they never waive a finding or grant construction approval.

The explicit scope is no production-code/configuration/store/environment changes,
versioned test-only code under `tests/readiness/ingest/`, generated state under
`.friday_test/`, and the operator-confirmed production-offline/shared-LM-Studio
window. Reviewers create only private external scratch evidence. No harness,
environment, model/server action, fixture conversion or package install is allowed.

The directive's construction source is `494eed4f1c15d79d29cf0acc5e2203d7c7ebe5ef`.
Its unchanged SHA256 is `e44d4e4b28736d66a1de1e66314cb6da25343430dec0933be4ac9f1645ec91ad`.
The controller freezes a new documentation-only review candidate and an external
exact request/manifest after this authorization is committed. The dispatched
request binds that candidate, exact diff, protected identity and all input hashes.

This is round 1 of one authorized review pass. It grants no automatic remediation
loop, replacement council, construction, stage activation, acceptance or delivery.
Current explicit authorization supersedes prior metadata saying no council was
authorized; it leaves all runtime/effects prohibitions in place.

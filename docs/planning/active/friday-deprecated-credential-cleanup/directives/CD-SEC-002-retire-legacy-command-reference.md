# CD-SEC-002 — retire the deprecated command reference

Execution authorized by Chuck Russell on 2026-10-14: "replace the two tests’ legacy command reference for that folder. it is fully deprecated". Current explicit instruction selects this bounded extension of the started security/remove-deprecated-credentials initiative; Langfuse remains queued and unauthorized.

Allowed product files: packages/friday-chat/tests_chat/compat/test_command_surface_parity.py and packages/friday-chat/tests_chat/compat/fixtures/legacy_command_names.yaml. Packet/board closeout metadata only otherwise. No runtime or package API change.

Plan: extract the original registered commands and aliases using the existing AST extraction semantics, include both fallback-only commands, freeze the exact 52-name set in a static fixture, and have both existing parity tests load that independent baseline. Retain the subset comparison against the current registry, required aliases/fallback assertions, count assertion and other tests. No baseline derived from the current registry, skips, weakened assertions or removal of the parity checks. The old script and entire deprecated folder remain untouched.

Acceptance criteria:
1. The static fixture equals all 52 names extracted from the pre-change legacy script plus fallback-only commands. Record the base revision, legacy source SHA256, fixture SHA256, and exact equality in a value-free provenance record; command names are not credentials.
2. Both parity checks use the fixture and no longer read or parse the deprecated folder. No unrelated test/runtime changes.
3. All compatibility tests pass while the private candidate's tests/integration/memory directory is temporarily unavailable; restore the private directory in a finally block. Never move or remove the main checkout's data. Existing assertions and actual-registry comparison remain meaningful.
4. Changed-file Ruff/Mypy, board/render and whitespace checks pass. Run documentation lifecycle validation and require no new failures relative to the base; preserve/report pre-existing failures according to AGENTS.md. No whole-suite rerun required for this test-only reference migration unless a failure warrants it.
5. Stable candidate commit and fresh-context read-only full work-unit validation before completion. Retain SEC-001 evidence unchanged; provider rotation/revocation stays pending, initiative started and delivery local.

Verification: existing private Python 3.13 environment, unchanged external-access guard, explicit clean environment, private HOME/TMP/cache, synthetic fixture credentials only. No installs, inherited keys, live-provider requests or external effects. Documentation/configuration closeout: test fixture provenance, packet execution/validation status and canonical board next gate.

Non-goals: delete/untrack the deprecated folder or any databases, sanitize additional secrets or historical evidence, rotate keys, change packaged runtime, update other baseline fixtures, push/merge/history rewrite. Stop on baseline mismatch, extra product paths, regression, unrelated drift or credential-bearing output.

Baseline clarification before formal review: the documentation checker reports two existing broken colon-line links in unchanged VAL-SEC-001/report.md (line 21). That report is byte-identical to base 85f14f24 and remains immutable. Criterion 4 records this existing documentation debt rather than changing prior evidence or unrelated checker behavior. No code scope or parity requirement changes.

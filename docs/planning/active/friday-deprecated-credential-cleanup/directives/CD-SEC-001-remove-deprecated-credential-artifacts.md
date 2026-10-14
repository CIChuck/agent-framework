# CD-SEC-001 — remove deprecated credential artifacts

Status: execution authorized by Chuck Russell's current removal instruction.

Explicit maintainer direction controls this security task. Four product paths:
delete tests/integration/memory/config.yaml; delete the tracked
tests/integration/memory/.friday/quarantine/tool_outputs.jsonl; add the exact config
path to .gitignore; mechanically migrate the active compatibility test's reference
to its existing sanitized fixture. This test adjustment is necessary to complete
the requested removal without leaving the active Chat suite dependent on a deleted
file. No runtime source, fixture values, package metadata or public contract changes.

Acceptance criteria for this repository-removal unit:
1. Neither credential-bearing path exists in the candidate tree; exact ignore
rules prevent accidental re-add. No other runtime store or dirty file is removed.
2. Before deletion, original/fixture active option paths are equal. Retain the
sanitized fixture unchanged; compare shipped examples against it. Remove the
obsolete original-vs-fixture comparison rather than introduce a self-comparison,
skip, weakened assertion or replacement fixture containing original values.
3. All eight previously identified exposed literals are absent from every tracked
non-binary current candidate blob, including gzip payloads. No provider validity
calls, secret values, deletion diffs or credential-bearing baseline copies enter
new audit evidence. A scan is not proof of revocation or historical erasure.
4. Focused config/compatibility tests, full Friday Chat tests, changed-file Ruff
and Mypy, board/docs/render/whitespace checks pass; record any infrastructure or
baseline failure accurately. A changed-source warning/failure is a blocker.
5. Stable commit and fresh read-only independent full work-unit review before
proposing this unit completed. Whole initiative remains started until provider
revocation/replacement is confirmed and maintainer accepts completion.

Verification uses the existing private Python 3.13 environment, installed packages,
the unchanged deterministic guard, fresh private HOME/TMP/cache and synthetic
test credentials. No install/sync, inherited credentials, external DNS/services,
model/exporter activation or user-store access. Existing Chat fixture-only
127.0.0.1 peers may run with the unchanged guard; OS loopback escalation is allowed
only for those retained fixtures if needed. No key management effects authorized
without provider-account access and identity information.

Non-goals: rewrite/force-push history, change source/runtime configuration behavior,
refactor legacy scripts, delete other .friday/vector/cache data, rotate every key
in an unrelated account, change provider settings, push/merge/deploy, or implement
Langfuse/MRTR. Historic accepted MCP source/control/manifest bytes remain fixed.

Stop on unexpected dependencies, extra source scope, secret-bearing evidence,
validation regressions, unexpected external effects or unrelated workspace drift.

# Command refactor — next-phase checkpoint

Branch: feature/command-retirement
Status: exact RET-001 approved; local implementation undergoing final verification
Execution phase: implementation
Validation state: not_ready

Chuck Russell approved the exact strengthened CD-CMD-RET-001 by “i approve the
document proceed.” [Approval](approval/command-retirement.md) binds directive
SHA `b760a9a8f8b94e120e5d26914d9bdf45f037a6a3f7f9552cd3d4054d829da9df` and product base
`6f291ca5755a616d9185c86dff104b660a1fba8c`. Older draft/unapproved labels in frozen directive/history
record their earlier state; this explicit approval supersedes those labels only
for this bounded unit, including RET-GATE-01–03.

[Unit evidence](validation/retirement/README.md) records before suites, caller
audit, assertion-preservation map, precise removals and working1038-test Chat
result. Final after-change/static/broad-baseline checks and clean candidate-Git
artifact/default-install proof must finish. Then freeze a stable candidate for
fresh read-only independent validation. Stop at findings or maintainer acceptance;
no automatic pilot/family construction, delivery, store migration or TUI work.

The accepted foundation checkpoint was merged in [PR13](https://github.com/CIChuck/agent-framework/pull/13)
at6f291ca5; old branch deleted and fresh retirement branch prepared. Its earlier
3116-test aggregate verification applies to that checkpoint. Retirement changes
are local and need their own validation. The two original working examples stay
protected/excluded. The full refactor remains started and unaccepted.

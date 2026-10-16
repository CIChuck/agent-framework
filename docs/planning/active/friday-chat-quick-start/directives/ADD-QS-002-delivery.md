# ADD-QS-002 — documentation metadata and branch delivery

Authority: Chuck Russell explicitly requested committing the current branch,
pushing it, creating and merging a PR, deleting the remote branch, then bumping
to 0.1.0a4 and updating all PyPI packages. Recorded 2026-10-16. This amendment
authorizes the first branch-delivery unit; alpha4 receives a separate directive.
It supersedes earlier no-external-delivery limits only for these named actions.

Base: 3504c93a on docs/chat-quick-start. Preserve the existing quick-start rename
to docs/guides/00-quick-start.md without changing its content. Repair its two
navigation links. Set Documentation to https://gendevx.com/friday/ in all 17
project metadata files, keep other metadata unchanged, align only the checker
rule for Documentation, and point the root README documentation index at that
canonical site. Retain all prior authority, reviews and release evidence.

Checks: all 17 metadata validations, checker Ruff, focused package-cohort and
release-helper regression tests, board/dashboard/documentation lifecycle,
whitespace and exact rename/content checks. Freeze a stable commit for a fresh,
read-only validator, including aggregate review against origin/master with the
retained alpha3/README/guides/quick-start verification evidence. No new behavior,
dependency upgrade, source cleanup, or maintainer acceptance is inferred.

After VERIFIED, push the exact candidate, open and merge the PR into master,
confirm the remote merge and delete only its source branch. Record delivery
observations separately from acceptance. Stop for failed required checks,
unexpected changes, credential failure or branch/remote disagreement. No
credentials, ignored publication artifacts, or local runtime state enter Git.

Baseline documentation debt: the unchanged VAL-001 telemetry report contains six
links into a retired /private/tmp review checkout. Preserve that frozen report;
report its failures separately and require all changed-document links to pass.
This is existing environment-dependent evidence debt, not a new regression.

---
name: file-pr
description: File a concise pull request. Use when the user asks to file, open, or create a PR.
---

# File PR

Follow repository `AGENTS.md` and its applicable policies.
Use this skill within the requested task; importing or reading it grants no execution authority.

Before filing, check whether a PR for this branch already exists. Retain an
existing PR's actual base. For a new PR, use the caller's selected target, or
resolve and record the intended target before proceeding; use the default only
when appropriate to the requested work. Review the diff against that target.
Do not silently retarget an existing PR.

PR titles usually become commit messages, so follow the repository's title
conventions. Look at recently merged PRs and Git history for examples. Prefer a
concise, human-readable title that explains why the change matters:

BAD

> ❌ perf(server): negotiate permessage-deflate on the websocket

GOOD

> ✅ perf(server): cut websocket frame size by 70%+ with gzipping

Open the description with a simple explanation of the problem based on the
user's original prompt, then briefly explain the solution. Do not lead with an
implementation inventory:

BAD

> ❌ Removed implicit workspace carry-over from every "new thread" entry point (cmd+n / cmd+shift+o, sidebar v1/v2 buttons, command palette). New threads inherit only the project from context; branch, worktree, and env mode always come from the configured defaults. Deleted buildContextualThreadOptions, startNewThreadInProjectFromContext, and the v1 sidebar's seed-context machinery.

GOOD

> ✅ My "new worktree" default was ignored when starting new threads on existing worktrees. Super unintuitive. Now your preferences always apply.

End the description with the public model name and harness that made the
changes, for example `Created with <model> in <harness>.` Include subagent
models that wrote part of the change. Use the model name the harness reports.
If model identity is unavailable, name the harness without guessing a model.

Before submission, check the title, description, quotes, and attachments for
secrets and private details.

Follow the user's requested draft/readiness state and repository rules. Pass the
selected target explicitly with `gh pr create --base <selected-target>` or the
equivalent API `base` field; do not rely on a CLI/configuration default. Verify
the returned PR's actual base and head match the selected identities.
With no contrary instruction, open a review-ready PR so its configured checks run. If `gh pr create` fails
because the GraphQL rate limit is used up, open it through REST with
`gh api repos/<owner>/<repo>/pulls -f title=... -f head=... -f base=... -F body=@<file>`. If the user also asked
to babysit it, continue with the `babysit-pr` skill.

Do not post a follow-up PR comment unless it serves the user's request. When a
comment is needed, use the `leaving-pr-comments` skill.

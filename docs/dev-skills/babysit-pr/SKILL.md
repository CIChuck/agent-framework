---
name: babysit-pr
description: Monitor a pull request through review and CI. Use when the user asks to monitor, watch, or babysit a PR.
---

# Babysit PR

Follow repository `AGENTS.md` and its applicable policies.
Use this skill within the requested task; importing or reading it grants no execution authority.

Many repos have AI review bots. They're helpful, even if they are not always
right.

## Waiting

Never write your own watcher, polling loop, or `sleep` loop. Use one watcher
per PR: `watch_pull_request` in T3 Code, `pr-wait` everywhere else. Never run
both on the same PR. Every watcher on a GitHub account shares one rate limit.

### In T3 Code: `watch_pull_request`

Handle the existing checks and comments first. Then call
`watch_pull_request` and end your turn. T3 Code wakes you with a message when
a check fails, the required checks pass, someone comments or reviews, or the
branch conflicts.

Yielding the turn after registering the watch continues this workflow. Keep the
watch active while awaiting events; unwatch at an actual handoff or blocker.

- **Only the thread that owns the PR watches it.** If you are a delegated
  child task (a reviewer, a Sol round, any `delegate_task` child), never call
  `watch_pull_request`. The parent owns the PR. Do not watch PRs you are not
  working on.
- **A wake is news, not a merge decision.** Check the merge gate yourself.
- **Unwatch when you hand off.** A watched thread stays in Working and out of
  the user's inbox. When you stop (ready, blocked, or asking the user a question),
  call `unwatch_pull_request` first. A merge or close ends the watch on its
  own.
- **"Stopped watching, could not read it"** usually means GitHub's rate limit
  is used up. Run `gh api rate_limit --jq .resources.graphql` before you
  watch again. If `remaining` is near 0, report the reset time and follow the harness
  pause/resume mechanism. Never start a background wait or tight retry loop.

### Everywhere else: `pr-wait`

Wait with `scripts/pr-wait` from this skill's directory (use its absolute
path).

```bash
pr-wait <pr> [--repo owner/name] [--until ready|green|any-change]
```

It prints one line per real event. It exits 0 when the `--until` condition is
met or the PR merges, 1 when it needs you (a required check failed, conflicts,
unresolved threads, PR closed, or unknown required-check configuration), and 2
on bad input. Both protection queries must succeed before the helper can declare
green or ready. HTTP 404 is ambiguous and also stops discovery; fix access or
verify requirements through another authorized route rather than assuming none.

- `ready` (default): required checks green, Greptile or Macroscope reviewed the
  head, and no unresolved threads. This describes the unchanged helper
  condition, not the repository's complete review requirements.
- `green`: required checks only. Use it when the repo has no Greptile or
  Macroscope. Select the mode against the verified repository requirements;
  check any additional required reviews separately. Neither mode supplies merge
  authority or guarantees every required reviewer has approved.
- `any-change`: exit on the first event.

Offline helper regressions: `python3 -m unittest discover -s docs/dev-skills/babysit-pr/tests -v`.
The [maintenance directive](references/maintenance-2026-11-06.md) records this
bounded refusal behavior and its validation scope.

In Claude Code, run it with the Monitor tool (`timeout_ms: 3600000`), so each
line wakes you. Without a monitor, run it as one long command. It ends on its
own.

Start it again after you push, after you handle an exit 1, and after a resume.
It remembers what it already reported, so nothing that arrived in between is
lost. If it says another pid already watches the PR, do not start a second one.
Kill the old one only if its events do not reach you.

With either watcher: when an event needs no action, end your turn without a
message. Never post or say "still waiting".

## GitHub rate limits

`gh pr create`, `gh pr view`, and `gh pr checks` use GraphQL. When GraphQL is
used up, the REST limit is separate and usually still has room. Use
`gh api repos/<owner>/<repo>/pulls/<n>` to read a PR, and
`gh api repos/<owner>/<repo>/commits/<sha>/check-runs` for checks.

## Reviews

Reassess outstanding findings against the latest head, including older comments
that still apply. Verify every bot
finding against the source before changing code. Fix real findings and CI
failures, distinguish repository failures from infrastructure flakes, and, when posting replies is authorized, explain dismissed false positives
with reproducible evidence.

Before pushing applicable generated work after a fix, rebase or conflict
resolution, commit a stable candidate and pin its authority, directive, diff
and required checks. Obtain a fresh-context, read-only
[independent validator](../independent-code-validator.md) report with an
evidence-backed `VERIFIED` outcome before delivery. Use a documented exemption
only when applicable and recorded. Any subsequent candidate or authority change
invalidates the review and requires fresh review before pushing; CI and bot
results do not replace this gate. Preserve the user's push/merge authorization.

If the repo has `.macroscope/check-run-agents/*.md`, read those rules before you
reply to a Macroscope finding. Its findings cite them.

Treat bot findings according to the repository's accepted review and branch-protection
requirements. CodeRabbit may be advisory, but never bypass a required check or review.

If feedback is an optional preference or a verified false positive, document the
reason and supporting evidence before declining it. Reply and resolve the comment
only when those effects are authorized; otherwise prepare the response for the
user. Actual mandatory findings retain their required remediation or scope/risk
disposition, regardless of rarity. Use the `leaving-pr-comments` skill for every
comment posted on the user's behalf.

Screenshots and videos help as well, when you have a way to upload them.

Keep the PR at the size the user's goal needs. Review loops tend to grow a
PR one cheap-looking fix at a time. Classify findings against approved requirements.
Security, contract, permission and data-loss violations remain mandatory even
on rare or unintended paths. Fix mandatory findings within authorized scope;
report out-of-scope mandatory findings for scope/risk disposition rather than
silently implementing or waiving them. A written dismissal does not satisfy
required remediation or authorize merging.
Decline only optional preferences or verified false positives with a documented
reason and evidence. List remaining optional suggestions as follow-ups.
Prefer the smallest fix that satisfies the requirement.

## Base branch and merging

Keep an eye on changes to the PR's actual base branch and rebase when needed. `pr-wait` reports when
new base commits touch this PR's files, and when the PR becomes BEHIND or DIRTY.
`watch_pull_request` reports conflicts only, so check for BEHIND yourself
before you call the PR ready.
If an overlapping PR makes this one obsolete, stop monitoring, report it to the
user, and ask before closing the PR unless closure was explicitly authorized.

If nothing has changed, stay quiet rather than posting filler comments. Stop
when `pr-wait` exits 0, or in T3 Code when the merge gate passes on the latest
head. Merge only when the user explicitly requested it;
otherwise report that the PR is ready. Right before a merge, run `git fetch` and
check the PR again. Never merge when it is BEHIND or DIRTY, or when base commits
that landed after the last green run touch this PR's files. Rebase, complete any
required fresh independent validation, push, and wait for green again.

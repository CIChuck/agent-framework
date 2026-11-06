---
name: full-stop
description: Prepare an explicitly requested full-stop PR workflow for human merge. A plain request to stop or pause means stop, not this workflow.
---

# Full Stop

Follow repository `AGENTS.md` and its applicable policies.
Use this skill within the requested task; importing or reading it grants no execution authority.

Do the same work as `full-send`, but stop with the PR ready for the user to merge.
Never merge it.

Read [full-send](../full-send/SKILL.md) for its proof, bounded review and PR
preparation workflow. An explicit full-stop PR workflow request authorizes those
steps within accepted scope; merge permission does not apply. Apply repository
policies and all actual approval boundaries. If the user's intent is
to stop current work, stop rather than starting PR preparation.

## No merging

You may commit, push, rebase, fix conflicts, and use `--force-with-lease` on
this task's branch. Never merge, enable auto-merge, enter a merge queue, push
directly to the default or selected target branch, bypass branch protection, or
delegate those actions. Work only on a separate task branch.

Disable existing auto-merge and remove the PR from any merge queue before
work begins; check again before each push. Report these changes. If you
cannot prevent automatic merging, report the blocker before proceeding.

## Stop at the gate

Use full-send's merge gate as the readiness check, including its applicable
frozen-candidate independent validation step. Replace its merge and final
report steps with a handoff. Proof and review must cover the final diff;
recheck behavior changes and meaningful conflict fixes before handoff.

Fetch the target branch and check the live PR's head, base, checks, reviews,
and mergeability. Confirm it is open, not a draft, and not set to merge
without the user. If someone else merged it, report that instead.

- **Ready to merge:** the merge gate passes. Leave the PR open and unmerged.
- **Waiting for required approval:** only human approval remains. Confirm
  that this is the actual blocker.
- **Blocked:** explain what prevents readiness, what you tried, and what is
  needed. Follow full-send's rules for asking the user.

In T3 Code, call `unwatch_pull_request` before the handoff or a question.
Report the PR link, final head, verdict, proof, reviewer outcome, and remaining
risks. State whether the PR is still open and unmerged.

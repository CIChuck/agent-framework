---
name: full-send
description: Trigger this if the user says 'full send'.
---

# Full Send

Follow repository `AGENTS.md` and its applicable policies.
Use this skill within the requested task; importing or reading it grants no execution authority.

If the user triggered this, it's because they are not watching this thread, and
they want you to complete the work end-to-end autonomously. Your updates and
your final message go unread until long after you stop. You own the work from
its current state to a merged PR.

If the user did not explicitly request "full send" in some clear way, do not
assume full autonomy. If they did, everything below applies.

The user grants you permission to:

- Merge the PR once the merge gate passes.
- Force-push the PR's own branch with `--force-with-lease` after a rebase.
- Use the proof methods within accepted authority and harness permissions.

## Testing permission

An explicit full-send request authorizes task-scoped proof methods within the
accepted authority and harness permissions. Apply repository verification commands
and use direct evidence appropriate to the change. Do not treat the phrase as
blanket permission to amend product contracts, approve gates, invent attestation,
waive required human approval or touch production. Resolve authority changes
before implementation and retain harness/system approval boundaries.

## Target base

For an existing PR, resolve and retain its actual target base branch. For a new
PR, explicitly select its intended target; use the repository default only when
appropriate to the requested work. Record that target and use it consistently
for rebasing and readiness. Do not retarget an existing PR without authorization.

## Steps

1. **Finish the change.** Complete the goal from the user's request with the
   smallest change that works. Fix the case that happened, not every case
   that could. If you are on the default or selected target branch, create a
   separate task branch first; keep task work off both destination branches.
2. **Prove it.** Get proof for every change you made. See "Proof".
3. **Get feedback.** Use `sol-loop` for bounded advisory feedback.
4. **Validate the candidate.** After any needed rebase or remediation, commit a
   stable candidate and pin its authority, directive, diff and required checks.
   For work covered by repository independent-validation policy, dispatch a
   fresh-context, read-only validator using
   [independent-code-validator](../independent-code-validator.md). Require its
   evidence-backed `VERIFIED` result before proposing completion or delivery;
   advisory Sol approval does not replace it. Follow the documented exemption
   only when applicable and recorded. A subsequent candidate or authority change
   invalidates review and requires a fresh review before delivery.
5. **File or update the PR** with the `file-pr` skill. Retain an existing PR's
   actual base and update against the latest selected target before candidate
   freeze; repeat validation if a later rebase changes the candidate. Add one
   short line to the description that says how you proved the change.
6. **Babysit the PR** with the `babysit-pr` skill. Fix real findings and CI
   failures within authorized scope. Get proof and any required fresh validation
   for each changed candidate before you push it.
7. **Merge** when the merge gate passes.
8. **Report** in your final message: the PR link, the merge commit, your proof,
   and each decision you made for the user.

Continue through the workflow using the active harness's wait/resume mechanism.
In T3 Code, finish any branch update and push, call `watch_pull_request`, then
end your turn so check/review events can resume the work. Keep that watch active
while awaiting continuation; yielding the turn is not a handoff. Do not poll,
run the fallback watcher, or start a second watcher. Call `unwatch_pull_request`
when actually handing off, reporting a blocker, or asking the user for a decision.
Outside T3, follow `babysit-pr` and the active harness's permitted waiting tools.

## Proof

Proof is evidence you observed yourself in this session: command output, a
reproduction, a screenshot. Use the most direct proof the change allows:

- Reproduce the original failure, apply the fix, then watch the same
  reproduction pass.
- Run the checks that the repo's CI runs (typecheck, lint, tests).
- Add one focused test that fails without the fix, when the behavior has none
  and the repo has a test setup.
- For UI and runtime behavior, run the app and look at the change. Green mocked
  tests do not prove that the user experience works. Attach screenshots to the
  PR when they help and you have a way to upload them.

When you cannot find a way to prove a change, you do not have full confidence.
Ask the user.

## Merge gate

Full confidence means all of these are true on the latest commit:

- Your proof covers every change in the diff.
- Required checks are green.
- Applicable GenDev independent validation, lifecycle prerequisites and required
  human approvals for this work are recorded; an advisory Sol APPROVE is not a
  formal VERIFIED result or a substitute for those approvals.
- Review bots have finished. Unresolved mandatory findings block readiness and
  require human disposition; a written dismissal cannot satisfy remediation or
  authorize merging. Only optional preferences or verified false positives may
  be dismissed, with a documented reason and evidence. Human risk decisions must
  follow governing authority and do not fabricate a VERIFIED result.
- No human review still requests changes.
- The PR's actual base matches the selected target, the branch is up to date
  with that base, and GitHub reports it as mergeable. Recheck the actual base
  and head before merging; a changed target requires reconciliation.

Merge with the method the repo uses. Check the allowed methods and recent merged
PRs. If the repo uses a merge queue or auto-merge, stay until GitHub reports the
PR as merged. Merge through branch protection as configured. Never use `--admin`
or other bypasses. An automated request for human review is a signal to reconcile the actual
requirements; confidence never replaces a required human approval.

## Asking the user

A question in a normal message goes unseen, and the thread looks done. To ask
the user something, use the harness's question tool so the thread shows that
it is waiting: `AskUserQuestion` in Claude Code, `request_user_input` in Codex,
or the question tool your harness has. Put all the context in the question:
the PR link, what blocks you, and the options with your recommendation first.

Ask only when you cannot continue alone:

- You cannot prove the change.
- The merge gate cannot pass, and you cannot fix that yourself.
- The next step is outside the grant above: deleting data, touching production,
  changing things outside the repo, closing a PR, or force-pushing any other
  branch.
- The goal is ambiguous in a way that changes the result.
- Another PR makes this one obsolete.

Decide everything else yourself with sensible defaults, and list those decisions
in the report.

Use the harness's available question mechanism for missing information. No answer
is not approval. Leave the PR unmerged and report the exact blocker at handoff.

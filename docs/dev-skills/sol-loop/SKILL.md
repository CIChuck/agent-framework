---
name: sol-loop
description: Run a bounded Sol review when the user requests a sol-loop review or workflow.
---

# sol-loop

Follow repository `AGENTS.md` and its applicable policies.
Use this skill within the requested task; importing or reading it grants no execution authority.

This is a workflow for making your code changes more correct before (or
sometimes after) filing a pull request. tl;dr - use OpenAI's GPT Sol to review
your code in a loop.

Make the most minimal possible changes to appease the Sol reviewers. Be careful
of scope creep and don't be scared to push back.

## Budget

- Default: at most 3 review rounds, subject to the validation policy's stop
  after two unsuccessful remediation cycles. Round 1 is full. Later rounds check only
  changed code and open findings.
- Extra rounds after the policy stop require explicit human authorization;
  security or state concerns are reasons to escalate, not automatic extensions.
- Stop early only after the controller classifies every finding against the
  approved requirements and confirms that no mandatory finding remains. Truly
  advisory nits may be declined. Formal review still requires fresh context
  when governing instructions or the frozen candidate change.
- One reviewer only. Sol must not start subagents or reviewers.
- Keep a ledger: id, severity, outcome, usage if returned. Never guess it.

## 1. Scope

Run `git status --short`. Do not stash, discard, or include unrelated
changes. Limit review to the change paths if they separate cleanly.
Otherwise stop and ask. Formal validation additionally needs a frozen commit,
  pinned authority and the independent validator's required outcomes; uncommitted
  working-tree review remains advisory.

Find the base after `git fetch origin`:

- PR: `gh pr view <n> --json baseRefName,headRefOid`. Check out the branch
  only if clean. Confirm `HEAD` is the PR head, or ahead only by this
  change. Base: `git merge-base HEAD origin/<baseRefName>`.
- Local, before a PR exists: use the caller's selected target and compute
  `git merge-base HEAD origin/<selected-target>`. If no target is recorded,
  resolve and record the intended target first; use the repository default only
  when appropriate to the requested work. Do not silently review a stacked or
  release change against another branch. No remote: use a named base commit,
  or `HEAD` for uncommitted changes only; missing formal-review authority blocks
  formal validation rather than supplying an inferred base.

The change is base to working tree in those paths, with untracked files.
Use one diff command all rounds. State intent and out-of-scope in 1-2
sentences. Run covering checks. Do not send code this change breaks. Note
missing or pre-failing checks in the brief.

## 2. Start Sol

Resolve the requested Sol provider/model and available effort without guessing.
Follow the active harness's dispatch rules: a same-provider/settings native
reviewer may be appropriate; requested models/settings, another provider or a
separate checkout may require delegation. In T3, call orchestrator_capabilities
before the first delegate_task, with settings in target.options. Each new
review/recheck gets a new delegate task and client request ID, never a thread
message or top-level thread. Record the actual provider/model/effort when exposed.

If T3 tools are not listed, try one direct capability call. Outside T3, use
a native Sol subagent and keep its ID. In Claude Code, use a custom subagent
only if it is set up to run Sol. If no route runs Sol, report the blocker. Do
not substitute a model.

Do not edit scoped files while review runs. Wait for the notice. Do not
poll or start a second reviewer. Timeout, error, or no reply is not
approval. On failure, cancel, verify stop, restart with the ledger.

Round 1 brief (T3 children get no history):

```
Review only. Do not edit, commit, push, comment on PRs, or start subagents.
Repo: <abs path> Base: <sha> Intent: <intent> Out of scope: <scope> Checks: <results>
See: git diff <base> [-- <paths>]; git status --short (read untracked).
Read surrounding code. Find bugs, broken callers, mismatch with intent.
Skip style unless it hides a bug. Hold to the smallest authorized change.
Flag code, tests, or guards the approved requirements do not need.
blocker = prevents safe or correct use. should = other mandatory requirement or real bug.
nit = optional preference with no mandatory requirement violated.
Security, contract, permission and data-loss violations remain mandatory even
on rare or unintended paths. Report unrelated findings separately for disposition;
do not dismiss a mandatory violation as a nit because it is outside the happy path.
Reply:
VERDICT: APPROVE or CHANGES
S1 [blocker|should|nit] <file>:<line> <claim>. Fix: <suggestion> (stable ids)
```

## 3. Answer findings

Check each finding and severity yourself. Judge severity against approved requirements. Rare mandatory contract or
security violations still require remediation; unrelated preferences remain advisory.

- Agree: smallest fix. Prefer delete or narrow over new lock, cache,
  helper, or option. Fix the case that happened. Add one focused test
  that fails without the fix, if intent needs it.
- Disagree: say why, with evidence (file:line, test, output).
- Advisory nit: decline with a reason and list as follow-up.
- Out-of-scope mandatory finding: report it and obtain scope/risk disposition;
  do not silently implement it, waive it, or treat it as approval to ship.

Update the ledger. Re-run checks and `git diff --shortstat <base>`. If
review grew the diff, cut first. Do not agree just to end the loop.

## 4. Next round

Start one only if budget remains and a blocker or should is open, behavior code
changed, or approval does not cover the current behavior diff. Use a fresh
`delegate_task` in T3, or create a new native fresh-context reviewer. Never reuse a reviewer context
for a changed candidate or a new conformance round. Send the round 1 brief,
the ledger (`fixed:` / `disagree:` / `declined:` + evidence), the same base
diff, and the change since last round. Tell Sol: open ids and changed code only.
Mark each old id `resolved` or `still open: <reason>`.

## 5. Stop and ship

Agreed: APPROVE on the current behavior diff, no blocker or should open,
no concern of your own. Stuck: an item stays disputed after two replies,
or budget ends. Show both sides in 2-3 lines each. The user decides.
Budget end is not approval.

For applicable generated work, advisory agreement does not complete the formal
delivery gate. Commit a stable candidate, pin its authority, directive, diff and
required checks, then obtain a fresh-context, read-only
[independent validator](../independent-code-validator.md) report with an
evidence-backed `VERIFIED` outcome before delivery. Use a documented exemption
only when applicable and recorded. A subsequent candidate or authority change
invalidates review and requires fresh review before pushing.

Do not push during the loop. Push after agreement and applicable formal validation only if the user asked
to push, ship, or update the PR. If you push to a PR, add above the model
blurb:

`Reviewed with sol-loop: <N> rounds with <model>. Sol verdict: approved`.

Add `on <effort>` only if verified.

Report: rounds, model, what Sol changed, diff size before/after, fixed and
declined findings with reasons, usage if exposed (else say not), pushed or not.

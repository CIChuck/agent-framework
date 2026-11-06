---
name: council
description: Obtain a three-provider independent review when the user explicitly requests a council review or workflow.
---

# Council

Follow repository `AGENTS.md` and its applicable policies.
Use this skill within the requested task; importing or reading it grants no execution authority.

Establish whether the user requested read-only review or implementation plus
review. Perform known fixes only within authorized implementation scope, then
freeze the candidate. A read-only council reports known issues without edits.
If the user wants new ideas, review the proposal rather than fixing discarded code.

Bring in three delegates to help with the user's request, usually for review
or feedback. Use one strong model from each of three different providers, at
high reasoning effort. If the user's instructions name council members, use
those. Otherwise pick the latest flagship model from each provider, for
example Claude Opus, GPT Sol, and Gemini Pro.

In T3 Code, use `orchestrator_capabilities` to resolve the models, then
`delegate_task` to start one delegate per model in parallel. Elsewhere, use
the harness's subagent tools. If you cannot reach three providers, or a named
member is unavailable, report it instead of substituting.

Give each delegate the request and relevant context. For review or feedback,
keep their work read-only. Collect their responses and summarize the useful
findings, disagreements, and recommended next steps.

For a code review, ask each delegate for a score out of 10.
Count each full review pass as one round.
A fresh review after fixes starts a new round.

If the work ends in a pull request, put the results in the PR description.
Put this section before the model and harness line at the end:

```markdown
## Council review

Rounds: 2

| Delegate | Round 1 | Round 2 |
| --- | --- | --- |
| Claude Opus | 7/10 | 9/10 |
| GPT Sol | 8/10 | 10/10 |
| Gemini Pro | 7/10 | 9/10 |
```

If a delegate gives no score, write `no score`. Do not invent one.
If the PR is open and editing its description is within the authorized scope,
edit the description. Do not post a comment for this. Otherwise put the same
results in the final reply only. A read-only review does not authorize PR edits.

Remediate agreed findings only within the approved scope, then request fresh
review contexts against the revised frozen candidate. Use one full council pass
per round, within the declared budget and two-unsuccessful-cycle escalation rule.
Scores are advisory; formal GenDev validation still requires its policy outcome.
Return unresolved mandatory findings to the human rather than looping indefinitely.

Do not let repeated reviews result in scope creep. It is your job to fight to
keep scope limited.

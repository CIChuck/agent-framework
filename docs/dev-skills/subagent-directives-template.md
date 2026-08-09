Approve and execute
docs/planning/build-plans/construction-directives/friday-chat-command-remediation-1-construction-directive.md

First, commit only the construction directive and push the current branch as the pre-implementation
checkpoint.

Then spawn one fresh-context sub-agent using fork_turns="none" as the primary implementer. Instruct it to read AGENTS.md, the repository engineering policy, the remediation plan, the construction directive, and every required referenced document before editing.

Remain the supervising agent: independently inspect changes and gate evidence, enforce scope, preserve unrelated state, and never use active .friday data.

Execute the directive in order. Require documented PASS, FAIL, or BLOCKED evidence at every gate. Continue through ALL Gates but only after each passes. Stop on any directive stop condition. At the final Gate  pause and request my explicit approval before removing containment or enabling any execution path.

I delegate approval authority for all Gates to the primary supervising agent. The implementation sub-agent may not approve its own work. After independently reviewing each gate’s changes, tests, and required evidence, the supervising agent may record PASS, close the gate, and direct work to continue without waiting for me—including Gate D. Consult me only if a gate is FAIL or BLOCKED, a directive stop ondition occurs, or additional scope or authority is required.

Do not create a PR, merge, or make additional commits or pushes unless I separately authorize them.

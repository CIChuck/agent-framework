# Builder And Independent Validator Handoff Template

Use this template to dispatch a bounded implementation and its independent
post-generation review. Replace every bracketed value before use.

Follow:

1. `AGENTS.md`;
2. `docs/reference/policies/repository-engineering-policy.md`;
3. `docs/reference/policies/development-task-lifecycle.md`;
4. `docs/reference/policies/independent-validation-policy.md`; and
5. the initiative authority manifest and construction directive.

## Controller Preparation

- Initiative: `[INITIATIVE-ID]`
- Work unit: `[WORK-UNIT-ID]`
- Branch: `[FEATURE-BRANCH]`
- Base revision: `[BASE-COMMIT]`
- Construction directive: `[DIRECTIVE-PATH]`
- Authority manifest: `[AUTHORITY-MANIFEST-PATH]`
- Required validation profile: `[FULL|DELTA|AGGREGATE]`
- Authorized external effects: `[NONE OR EXACT AUTHORITY]`

Confirm the work is `started`, implementation authority is granted, the branch
matches the board, and the directive is approved. Preserve unrelated worktree
state.

## Builder Dispatch

Spawn a bounded implementation agent and instruct it to:

1. read the authority manifest and every required document completely;
2. implement only the construction directive;
3. stop on conflicts, missing authority, scope expansion, or a directive stop
   condition;
4. add and run the required tests and verification;
5. record skipped checks and known failures honestly;
6. produce an implementation report mapped to tactical tasks and acceptance
   criteria;
7. commit a stable candidate without unrelated files; and
8. return the candidate commit and exact diff range without claiming independent
   verification or acceptance.

The builder may not approve its own candidate, widen scope, push, merge,
release, deploy, expose credentials, or affect external systems without separate
authority.

## Candidate Freeze

After independently checking that the candidate identity and scope are stable,
the controller creates `validation/VAL-[ID]-request.yaml` containing:

- initiative and work-unit IDs;
- base and candidate commits and exact diff range;
- review mode;
- authority paths, revisions, and hashes;
- construction directive;
- acceptance criteria and tactical task IDs;
- required commands;
- known baseline failures and exclusions;
- authorized credentials, costs, and external effects; and
- report and evidence locations.

## Validator Dispatch

Spawn one fresh-context validator that does not inherit the builder session.
Provide only the validation request and access to its explicitly named
repository inputs. Instruct it to use
`docs/dev-skills/independent-code-validator.md`.
When the agent interface supports context forking, use its no-history option
such as `fork_turns="none"`.

The validator is read-only and returns exactly:

- `VERIFIED` with cited evidence;
- `CHANGES_REQUESTED` with numbered findings and mitigation requirements; or
- `BLOCKED` with the blocking condition and exit gate.

The validator may not edit, remediate, mutate the board, accept, push, merge,
release, deploy, disclose credentials, or create external effects.

## Controller Disposition

The controller verifies report completeness and stores the durable request,
report, and evidence.

- For `VERIFIED`, record validation evidence and propose `completed` for
  maintainer acceptance.
- For `CHANGES_REQUESTED`, create a bounded remediation directive containing
  every finding exactly once, dispatch authorized remediation, commit a new
  candidate, and start a fresh validator context.
- For `BLOCKED`, record the blocker and stop at its exact exit gate.

After two unsuccessful remediation cycles, stop and return unresolved findings
to the maintainer. Never translate `VERIFIED` into `accepted`; only the
maintainer controls final acceptance.

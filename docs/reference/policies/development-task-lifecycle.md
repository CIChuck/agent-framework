# Development Task Lifecycle Policy

## Purpose

This policy defines the repository-visible development board used by maintainers
and agents to select, authorize, execute, review, and close Friday engineering
work. It supplements the repository engineering policy; it does not replace it.

The canonical current-state registry is
[`docs/planning/board.yaml`](../../planning/board.yaml). The rendered
[`docs/planning/README.md`](../../planning/README.md) is its human-readable view.
When they disagree, the YAML board controls and validation must fail until the
view is regenerated.

## Work States

Every tracked initiative uses exactly one progressive work state:

1. `queued`: identified and documented, but not authorized for execution;
2. `approved`: the current scope is explicitly approved, but execution has not
   started;
3. `started`: execution is underway on a named branch;
4. `completed`: implementation and required validation are finished, but the
   maintainer has not accepted the result; and
5. `accepted`: the maintainer has accepted the completed result.

Only the repository maintainer may move work into `approved` or `accepted`.
An agent may record `started` after creating the authorized branch and may move
work to `completed` after recording validation evidence. An agent must never
infer approval or acceptance from silence, a push, a merge, or a release.

## Conditions

Conditions are orthogonal to work state:

- `normal`: no exceptional scheduling condition;
- `blocked`: a named condition prevents the next transition;
- `deferred`: the maintainer deliberately postponed the work; and
- `backlog`: the item is retained as an idea or inventory rather than scheduled
  work.

A condition does not grant authority or erase prior work. Its reason and exit
gate belong in the initiative packet and board `next_gate` field.

## Delivery States

Delivery is tracked separately from work acceptance:

`not_started -> local -> pushed -> merged -> released`

Delivery events are observable facts, not work-state approvals. A completed
change may be pushed but unaccepted, or accepted before it is merged. Every
merged or released transition must record evidence such as a pull request,
merge commit, tag, or release record.

## Planning Locations

Packet location is derived from work state and condition:

| State or condition | Packet location |
| --- | --- |
| `queued` or `approved`, normal | `docs/planning/queued/<initiative>/` |
| `started`, normal | `docs/planning/active/<initiative>/` |
| `completed`, normal | `docs/planning/review/<initiative>/` |
| `blocked` | `docs/planning/blocked/<initiative>/` |
| `deferred` | `docs/planning/deferred/<initiative>/` |
| `backlog` | `docs/planning/backlog/<initiative>/` |
| `accepted` | `docs/archive/completed/<year>/<initiative>/` |

Moving a packet does not itself change its state. Repair backlinks, update the
board, render the dashboard, and run validation in the same commit.

## Initiative Packet

Every current task has one packet `README.md`. Add supporting artifacts only
when the work requires them:

- `build-plan.md`: approved scope, requirements, boundaries, and acceptance
  criteria;
- `tactical-plan.md`: implementation ordering and validation strategy;
- `directives/`: bounded execution instructions;
- `execution-log.md`: append-only checkpoints, decisions, evidence, and stops;
- `closeout.md`: completed validation and maintainer acceptance evidence.

The board owns current state, priority, authority, delivery state, and next
gate. Packet documents own the detailed rationale and evidence. Historical text
inside an imported packet does not override the board.

## Transition Gates

### Queue to approved

Requires an explicit maintainer decision, a bounded current scope, acceptance
criteria, and identification of affected package boundaries.

### Approved to started

Requires a dedicated branch, recorded baseline, satisfied dependencies, and a
tactical plan or explicit waiver.

### Started to completed

Requires implementation to be finished, focused validation evidence, broader
validation proportional to risk, updated documentation, and no hidden known
blocker. Completion is a proposal for review, not self-acceptance.

### Completed to accepted

Requires explicit maintainer acceptance. Record the accepting maintainer, date,
and closeout evidence. Move the packet to the completed archive.

## Operating Commands

Use `uv run python scripts/friday-dev-board.py`:

```text
list
next
show <initiative>
validate
render
transition <initiative> <state> ...
set-condition <initiative> <condition> ...
set-delivery <initiative> <delivery-state> ...
```

Mutation commands require an actor, role, note, and the new next gate where the
work state or condition changes. Maintainer-controlled transitions reject an
agent role. Imported historical approvals must return to `queued` and receive
current approval before implementation can start. Commands update both the YAML
registry and rendered dashboard only after the proposed state validates.

## Imported Work

The initial board imports older packets with `legacy_import: true` when complete
historical transition evidence is unavailable. This marker permits missing old
approval fields; it does not grant present implementation authority. New tasks
and all future transitions must satisfy the full gate contract.

# MAINT-001 — human UAT and acceptance handoff

Status: independently VERIFIED; human UAT NOT RUN; acceptance NOT GRANTED.
The wider command-refactor initiative remains started, delivery local.

[Reconciled result](verified-report.md): Astra9.5 and Sol9.6, both VERIFIED with
no mandatory findings. Reviewed candidate `b15ee091a1bfae07b61de521d6478b39ca4b48d2`.
Product/artifact source `ae15a5374350807bd909bc823078087a53a47ce4`.
The later reconciliation commit changes documentation only.

The change puts complete reorganization sequencing in Friday Memory. Full runs
verify pending sources before synthesis, then verify exactly the newly created
insights. Chat delegates once inside its existing admission/snapshot/rollback
transaction. Explicit `--full`, distinct stage/count output and durable scope
evidence are included. Configuration, models, budgets, dependencies and the
shared Commands source are unchanged.

## Launch the verified installed build

This exact installed launcher was exercised by the normal/optimized probes:

```text
/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/friday-maint-build._innqy6m/artifact-bundle/installed-chat/bin/friday-chat
```

It is in temporary build storage. If it disappears, rebuild from the pinned
source and rerun installed proof; copying the virtualenv to another path does
not preserve absolute launcher shebangs. Do not substitute an unverified build.

The following commands are for the human operator. They create private copies
of the committed examples, then start Chat from the disposable directory.
They have not been executed as a UAT session by the controller.

```sh
cd /Users/chuckrussell/Dev/gendev/agent-framework
MAINT_UAT="$(mktemp -d /tmp/friday-maint-uat.XXXXXX)"
git show ae15a5374350807bd909bc823078087a53a47ce4:packages/friday-chat/config.example.yaml > "$MAINT_UAT/config.yaml"
git show ae15a5374350807bd909bc823078087a53a47ce4:packages/friday-chat/models-config.example.yaml > "$MAINT_UAT/models-config.example.yaml"
MAINT_CHAT='/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/friday-maint-build._innqy6m/artifact-bundle/installed-chat/bin/friday-chat'
```

Before launch, review those private configuration copies. Select your intended
primary, embedding, synthesis and classifier/researcher/judge providers there;
supply credentials through your normal local environment. Keep all vector, graph,
transcript, recovery, log, export and WAL paths inside `$MAINT_UAT`, and keep
`session.reorganize_on_exit: false` for individual cases. The committed example
uses relative `.friday` paths; launching from the private directory isolates
those defaults. Do not point this first run at personal stores or `.friday-old`.
Review any other configured absolute paths before starting.

When ready to make live provider calls:

```sh
cd "$MAINT_UAT"
"$MAINT_CHAT" --config "$MAINT_UAT/config.yaml" --runtime real
```

`--runtime fake` is suitable for limited UI/admission smoke checks, but cannot
establish real maintenance/provider behavior. Empty disposable stores likewise
cannot prove same-run synthesis or populated verdict counts. Use a populated
disposable dataset with known starting records/statuses for those cases; mark
a case BLOCKED if its prerequisite is absent. Do not infer a pass from emptiness.

## Test and record

Use the individually numbered [UAT checklist](../../../uat/maintenance-reorganization-uat.md).
Capture the build/source, configuration choice (no credentials), run ID, stage
order, counts, elapsed time and output. In particular, confirm a newly verified
source can contribute immediately, generated verification does not retry the
old pending batch, and uncertain/rejected outcomes remain distinct from an error.

The automated installed proof already exercises deterministic cancellation and
rollback. Fault-injection cases are developer-assisted; there is no new public
slash-command fault-injection flag. Do not improvise destructive filesystem
failures to manufacture one. Ordinary Ctrl-C behavior is a separate usability
observation and may reach a different lifecycle boundary.

If a provider response fails validation, retain the run ID and sanitized role,
model, finish reason and validation-field lines. `failed_rolled_back` is a failed
operation with restored state; `recovery_required` is unresolved recovery.
A successfully completed verification stage can still report rejected/uncertain
records. Do not mark populated synthesis tests passed unless their inputs were
actually eligible.

## Acceptance boundary

The proposed human acceptance is only MAINT-001 as reviewed. No UAT result is
filled in automatically. Human acceptance, personal-store migration, delivery,
later command families and TUI/full-refactor completion remain separate.

Known failed/unwaived checks and platform limits are listed in the verification
report. They are not waived by this handoff. No repository or personal-state
cleanup is requested; retain UAT files and run evidence until your decision.

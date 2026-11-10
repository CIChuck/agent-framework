# MEMQ-001 — human UAT and bounded acceptance handoff

Status: **ready for manual UAT; human acceptance pending**. All20 cases remain
NOT RUN. Maintainer: Chuck Russell. No approval is needed to start this UAT.

The [20-case plan](../../../../uat/memq-user-acceptance-plan.md) is in the same
folder as the earlier Chat roadmap. Record actual PASS/FAIL/BLOCKED/NOT RUN
results there, separately from this [verification](verified-report.md).
Sol9.5, Astra9.4 and Claude9.5 unanimously VERIFIED, with no mandatory findings.

Reviewed candidate: `bab167579a0c6fcae8765f263ec754f1d4700d93`.
Installed source: `e4c0b9a2c5e80569829cc56af9addc8b3e358714`.
Package version0.1.0a4 is shared with earlier builds; use the commit and hashes
in [builder evidence](evidence.json) to identify this retained local artifact.

## Start the disposable interface run

This prepared launcher uses the verified installed binary, a separate fake
configuration, private working directory, temp/cache/export destinations and
telemetry disabled. It preserves both edited repository examples and existing
stores/exports. Run in a terminal:

```sh
sh /private/tmp/memq-closeout-78maeo5m/uat/launch-fake.sh
```

Configuration: `/private/tmp/memq-closeout-78maeo5m/uat/fake-config.yaml`.
Working folder: `/private/tmp/memq-closeout-78maeo5m/uat`.
Fake maintenance roots are fresh per process below that folder's `tmp/`.
The wrapper invokes:

```sh
FRIDAY_CHAT_RUNTIME=fake LITELLM_LOCAL_MODEL_COST_MAP=True   /private/tmp/friday-memq-d3-build-dp54_fru/candidate-bundle/installed-chat/bin/friday-chat   --config /private/tmp/memq-closeout-78maeo5m/uat/fake-config.yaml --runtime fake
```

Begin with `/help memory`, then `/memory`, `/insights`, `/summaries`, `/meta`,
`/entities`, `/list-ingested`; `/q` exits. The automated launch smoke executed
that sequence successfully, with an expected piped-input terminal warning and
legacy-LLM configuration warning. This is launch verification, not human UAT.

## Real persistence and populated fixtures

Fake mode covers interface/control-flow checks. Persisted listing cases10–14
require the real FrameworkMemoryAdapter, a fresh disposable real configuration,
and the plan's independently inventoried populated/promotion/partial fixtures.
The fake starter is not a real-provider configuration; do not simply change its
runtime flag. Copy a working real configuration to a disposable location,
redirect memory/transcript/export/maintenance/log destinations into that test
folder, retain valid model-library/provider settings, and disable telemetry and
exit maintenance. Then run from that private folder, with its private TMPDIR:

```sh
MEMQ_CHAT='/private/tmp/friday-memq-d3-build-dp54_fru/candidate-bundle/installed-chat/bin/friday-chat'
UAT_CONFIG='/absolute/path/to/disposable-real-config.yaml'
FRIDAY_CHAT_RUNTIME=real PYTHONDONTWRITEBYTECODE=1 LITELLM_LOCAL_MODEL_COST_MAP=True   "$MEMQ_CHAT" --config "$UAT_CONFIG" --runtime real
```

Use an explicit non-empty description, for example
`/ingest /absolute/path/document.txt project notes`. Omitting it still triggers
the pre-existing Chroma TypeError, tracked in FU-009; it is neither fixed nor
waived. Use prepared persisted metadata for missing-description listing cases.
Do not manufacture populated fixtures through maintenance/synthesis commands.
If a required fixture is unavailable, record BLOCKED and cite automated coverage;
do not count empty or fake output as a persistence/populated-rendering pass.
The installed proof already exercised real disposable storage with local
embeddings, but it does not execute the human checklist.

## Acceptance scope and limits

After recording UAT results, Chuck Russell decides whether to accept the bounded
six-query extraction and approved option R listing. No acceptance is recorded
here. Root Ruff534, the test_display collection conflict, four old formatting
failures and no-description ingest remain failed/unwaived. Only the recorded
macOS/Python3.13.10 environment is proven. Local temporary artifacts must remain
available; if removed, reproduce the pinned build rather than substituting a
same-version binary. No next unit, TUI construction or delivery starts here.

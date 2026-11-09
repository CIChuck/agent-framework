# MEMQ D3 artifact and installed-proof work record

Status: implementation in progress; independent D3 validation not ready.
The [D2 reconciliation](../d2/verified-report.md) is VERIFIED at `ccf5471b`.
Existing exact option R approval and the approved directive govern D3/D4–D5.
No product-source, test, dependency, configuration or ingestion change is part
of this stage. The new installed probe is validation code.

## Declared installed-probe CLI

The exact CLI grammar is recorded before installed execution. Each concrete
argv, revision, source/probe/helper/profile hash, environment, exit and output
will be recorded before/after its own execution in private raw receipts.

```text
<bundle>/installed-<lane>/bin/python -I -B [-O] <probe>
  --lane <neutral|chat>
  --prepared <own-prepared-harness>
  --source <clean-export-of-artifact-source-commit>
  --dist <bundle>/g5-dist
  --profile <bundle>/<neutral-profile.txt|default-profile.txt>
  --accepted-profile <pinned-accepted-DIAG-default-profile>
  --pilot-probe <hash-exact-read-only-pilot-helper-copy>
  --session-probe <hash-exact-read-only-SESSION-helper-copy>
  --diagnostics-probe <hash-exact-read-only-DIAG-helper-copy>
  --revision <artifact-source-commit>
  --report <unique-report-under-own-scratch>
```

`<probe>` is the new `validation/memory-queries/installed_probe.py` whose bytes
must equal the committed source export. Every report is new and private. The
interpreter is isolated with bytecode disabled; optimized runs add `-O`.
The pinned guard is explicitly loaded. Source exports supply inventory/fixture
oracles; runtime Commands/Chat imports must come from inventoried installed
distribution roots. The accepted SESSION helpers enforce complete member,
directory, type, byte, executable and module-origin checks through their
hash-verified pilot helper. No old exact38/24 API gate is spoofed or claimed.

The new probe includes the four directive-named retained checks: SESSION neutral
uses the DIAG probe's38-name list plus the exact16 MEMQ exports; SESSION Chat and
both DIAG bodies are otherwise unchanged. AST reversal evidence recovers all
four pinned functions. New neutral checks cover strict models, immutable lazy
factories, six awaited capabilities, availability/validation order, pending,
error/cancel identity, kind and nodes refusals. New Chat checks cover exact
metadata/help, six canonical dispatches, real and injected outcome consumption,
per-dispatch counts, custom/renamed handlers, errors/cancellation and real
persisted `/ingest` then `/list-ingested` with deterministic local embeddings.
Persisted absent and empty descriptions are asserted as separate groups.

## Current source checks and debt

Fresh current owning lanes pass: neutral/cohort599, Chat1390, CLI155; named52
and fast616/source117 also pass, with passive canonical-origin witnesses.
Ruff on all named paths and the new probe passes; mypy15 passes. New-format5
passes; the raw whole-change format gate still fails on four old Chat files,
while the pinned no-new-debt check passes. These failures remain unwaived.
Root Ruff still fails with534 findings. Root pytest and collect-only still fail
on the existing `test_display` name collision; collection now reports7082,
exactly6929+101 neutral+52 Chat new cases. No missing collection is concealed.

Source-only dry runs exercise the new neutral/Chat functions, including a real
disposable persisted listing. An early dry-run assertion incorrectly demanded
identity after CommandRequest's defensive snapshot; it was corrected to check
the original parsed tuple at construction and snapshot equality afterward.
An attempted retained source dry run was correctly refused by the installed
origin boundary and receives no passing or mutation credit. The retained
checks will run only against actual installations. Earlier development lint
and setup failures remain separate from the final passing checks.

Pending: committed-candidate closed build/replay, all actual installed normal/
optimized and unchanged pilot proofs, complete installed/archive/source and
semantic refusal controls, restored clean-copy probes, final preservation,
metadata/lock/admin checks and fresh three-seat D3 plus bounded aggregate council.
No installed result is claimed yet. Human UAT20 remains NOT RUN; baseline
nullable-ingest debt stays documented in FU-009 with explicit-description
workaround. No acceptance, later-family or external delivery is granted.

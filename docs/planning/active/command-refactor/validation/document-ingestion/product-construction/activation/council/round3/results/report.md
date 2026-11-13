# INGEST activation council — final outcome and maintainer handoff

2026-11-13. **CHANGES_REQUESTED; 9.5-per-seat gate unmet.** All three authorized
rounds are complete. Stop for Chuck's guidance; no further correction, replacement
seat or fourth round is authorized. Product construction has not started.

Reviewed candidate: `fd7d9f5d429857906d53da8fc053dc85b901a635` on
`feature/cmd-ingest-001`. [Reviewed activation package](../../../README.md)
remains byte-identical to that candidate. This record adds outcome/navigation
metadata only; it is not a changed design or an approval.

## Final independent assessments

| Seat | Verdict | Overall | Areas complete | Mandatory findings |
| --- | --- | ---: | ---: | ---: |
| [GPT-6.1 Sol](sol/report.md) | VERIFIED | 9.53 | 8/8 | 0 |
| [GPT-6 Astra](astra/report.md) | VERIFIED | 9.595 | 8/8 | 0 |
| [Claude Opus 5.5](opus/report.md) | CHANGES_REQUESTED | 9.27 | 8/8 | 1 |

Scores are the exact reported overall values, without averaging, inflation or
rounding up. Opus reported weighted total 9.2775 and a truncated score of 9.27.
All seats agree D1–D3 are satisfied. Their difference is a remaining converter-
deployment binding omission, identified by Opus. No seat was procedurally blocked
or incomplete in this final round.

## Remaining mandatory issue — Opus M1

The converter requires `assets_root`, `profile_id`, `asset_manifest_sha256` and
`scratch_root`, but the real Chat/Runtime/headless composition has no specified
source/discovery for these values. The embedding manifest has defined discovery,
while /read explicitly does not resolve it. No separate document binding exists.
Runtime document YAML and implicit scratch/store fallbacks are also excluded.
This leaves a builder inventing operator configuration or stopping at I3.

Controller assessment: this is a concrete gap in the exact composition design.
The bounded recommendation is one explicit document-settings resolver/binding
usable without Memory or embeddings, with strict fields and precedence. Missing
or invalid settings should refuse only document-format conversion, before worker
spawn, while plain-text /read remains usable. Assign it to existing Tools and
frontend composition seams, the headless recipe, the I3 case/file maps, installed
probe and operator guides. This recommendation is **not applied or authorized**
by this handoff; Chuck decides the next bounded action.

Required future acceptance, if approved: positive resolution from provisioned
local assets; no-worker/no-store refusal on missing/invalid binding; unaffected
text /read; installed normal/-O composition using the same public binding.
No new vendor or serving/parity campaign is recommended.

## Optional implementation clarifications retained

- Counter-factory capability snapshot/hash drift and a mutation-between-parent/
  child control (Sol and Astra).
- Nested worker parent-package imports must be quiet/offline; their startup cost
  belongs to the cold deadline. Redirection in worker main cannot precede Python's
  parent-package initialization (Sol and Opus).
- A small versioned IPC message/state table (Astra).
- Named I1-C2 resolver-schema/containment controls and the unchanged I1
  test_simple_vector regression selector (Opus).
- Chat's currently frozen lifecycle dataclass needs a mutable owned holder for
  its planned binding; clarify optional versus required YAML keys (Opus).

These are retained advisories, not silently promoted to new pre-coding gates.
No technical edits follow this final round without maintainer direction.

## Evidence and current authority

[Original report hashes and outcome](index.json), [frozen request](request.json),
and [controller closing boundary](controller-closing.json) retain the exact review
basis. All required pins, the logical index before status, HEAD/branch/staging,
16,690 protected nonplanning file hashes, 26 symlinks and eight preserved records
matched before outcome recording. Reviewer originals remain byte-exact.

No product imports/tests/builds/installs, Docling reruns, provider/model calls,
store operations, configuration changes or publication occurred. The metadata
closeout checks are planning checks, not product conformance. All Gate A1–A5
remain incomplete. The initiative remains started/local; construction, effects,
human UAT/acceptance and delivery are not granted. The council is inactive and the
three-round authorization is exhausted.

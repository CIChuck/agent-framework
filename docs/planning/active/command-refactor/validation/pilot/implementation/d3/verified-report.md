# PILOT-001 — reconciled independent verification

**VERIFIED** for the bounded help, exit and clear-screen pilot, including D1,
D2 and D3 G1–G5. Maintainer acceptance is pending.

Reviewed candidate: `eb216421e533b98d5d025f74a5bc0ea177d2f5ec` on `feature/command-retirement`.
Aggregate base: `65151670a832b9e1d0b7882a0b72d2371b3cc19c`.
Clean artifact source: `70ebef3a1bafc8b6269abd0fd4dbb7d4a7bac7a3`.
Reconciled: 2026-11-08T03:11:57+00:00. Subsequent closeout edits contain status/reports only.

The [two-member authorization](../../../../approval/pilot-two-member-council.md)
governs D3 after Gemini's quota failure. Both current reviewers used fresh
read-only contexts, separate private scratch, pinned authority and unchanged
candidate inputs. Their exact reports and frozen request are preserved in
[the council record](council-round2.json).

| Reviewer | D3 round1 | D3 round2 |
| --- | --- | --- |
| Claude Opus 5.5 | VERIFIED, 9.5/10 | VERIFIED, 9.6/10 |
| GPT-6.1 Sol | CHANGES_REQUESTED, 8.8/10 | VERIFIED, 9.6/10 |

Gemini produced no review or score; no retry or replacement was started.
Both current reviewers found **no mandatory findings** and independently closed:

- **D3-SOL-001:** complete actual installed file/directory sets and bytes agree
  with Git/wheel. Extra source, data, empty directories, bytecode and symlinks
  are refused in normal and optimized modes.
- **D3-SOL-002:** file origin and every package search path are checked together.
  Mixed valid/escaped origins are refused, including entry-point child checks.

Each reviewer reproduced **1,228 Chat, 217 Commands/cohort and 155 CLI tests**,
all **196** frozen source observations, one clean offline artifact bundle and
four installed normal/optimized lanes. Thirteen workspace builds, 125 locked
inputs and all 154 artifact/profile hashes agree with the supplied replay.
Neutral closure is one dependency-free distribution; default Chat closure is
138 distributions. Finance/tools imports, shared outcome ownership, aliases,
metadata/help/dispatch compatibility and entry-point help pass. All 784
preservation entries remain unchanged; the authorized neutral README status
sentence is the only package change during the proof correction.

Controller end checks matched all 17,145 protected contents, authority,
deliverable, product and prepared-input pins, logical index and exact dirty
status before any closeout edits. The two original dirty examples remain
untouched. Full raw receipts remain in [current evidence](remediation-evidence.json).

Known failures remain **failed and unwaived**: root Ruff's 534 findings, the root
Chat/CLI `test_display` collection conflict, and legacy registry formatting.
No candidate regression was identified; this is bounded verification.

Optional advisories remain deferred as mapped. Claude's additional in-prefix
shadow/.pth hardening suggestion is outside the current proof threat model;
the actual reviewed installations load their Git-equal site-packages trees.
The frozen request's one old `32fc8ced` narrative reference is reconciled to
its explicit current artifact revision `70ebef3a`, used by both reviewers.
Only macOS/arm64/CPython 3.13.10 is proven; live providers/stores were excluded,
and Python audit containment is not an OS sandbox.

**Next gate:** Chuck Russell's acceptance of PILOT-001. The entire command
refactor remains started. Later command families, P0/P1, TUI, full-refactor
acceptance and push/PR/merge/release remain separately gated. This report records
independent verification and does not record maintainer acceptance.

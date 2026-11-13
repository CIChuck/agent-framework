# INGEST compatibility cycle — pass1/4, global round6

Outcome: **CHANGES_REQUESTED** for `8d25d53a`; no score gate met.

| Seat | Reported outcome | Controller disposition | Coverage | Overall |
| --- | --- | --- | --- | --- |
| Sol | CHANGES_REQUESTED | CHANGES_REQUESTED | 9.1 | 8.8 |
| Astra | CHANGES_REQUESTED | CHANGES_REQUESTED | 9.0 | 8.7 |
| Opus | CHANGES_REQUESTED | BLOCKED: protected dirty-YAML read | 7.7 provisional | 8.0 provisional |

Opus disclosed an accidental search displaying three protected dirty-YAML lines;
the frozen request forbids that read. No write occurred and integrity matched,
but this is not valid formal signoff. Its source-backed technical findings were
independently checked without personal configuration. No reissue or replacement
was launched; this full pass consumes one of four allowed passes.

Six correction themes: public backup compatibility; actual background-task
ownership; Chat MCP failure adaptation; owned rejection logging; injectable-only
graph scoring; and maintained extraction failure/acknowledgement. Ten additional
Opus advisory dispositions refine isolation, read errors, public wrappers,
minimal imports, callable qualification, probe order and status/limitations.
Document corrections are proposed for fresh pass2, not independently closed here.

The [reconciliation](reconciliation.json) records exact requirement IDs, raw
hashes and bounded next steps. Readable [Sol](sol-report.md), [Astra](astra-report.md)
and [Opus](opus-report.md) reports normalize whitespace only; adjacent `.md.gz`
archives preserve their exact original bytes, with both hashes recorded.
All opening/closing identities and five administrative checks passed per seat;
these are design/source and administrative checks, not runtime/model evidence.

Next: fresh pass2/4 (round7), correction delta first then full bounded design.
Stop early only for every seat VERIFIED, zero mandatory findings, coverage and
overall >=9.5. At latest after pass4 stop for maintainer guidance. No Gate A,
construction, personal-store action, MAINT acceptance or delivery follows.

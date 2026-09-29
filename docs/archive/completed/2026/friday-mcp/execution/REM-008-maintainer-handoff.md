# REM-008 Candidate Handoff For Maintainer Validation

Date: 2026-09-29
Status: Implemented and frozen; maintainer validation pending
Initiative/work unit: `friday-mcp` / `MCP-WS-06`
Branch: `feature/friday-mcp-ws06-memory`
Final candidate: `820e252c496712264ebf767404c1e054f025d53a`
Remediation base: `486f3cf585799cc46bc8a6c4f6cf4925734f7188`
Original WS-06 base: `99bde5148ee21f47d4734d2a026fb198a3d19cbd`
Source/test commit: `adf59d11d1704355f84ec30e1d7a8959f226c355`
Finding: VAL014-F01 from the original [independent report](../validation/VAL-014-report.md)

The [implementation report](REM-008-implementation-report.md) records the exact
four sources, four tests and one report changed, with five REM-008 and ten original
WS-06 criterion mappings. A retry of the same checked completed interaction now
reuses its owned Chroma record and exact immutable SQLite receipt. A matching
retry does not create another memory record, embedding or transcript append.
Conflicting retries fail closed; false/ambiguous append, failed readback or
publication, cancellation and concurrent retries retain truthful pending state.

The pinned [maintainer validation request](../validation/REM-008-maintainer-validation-request.yaml)
and [frozen-input manifest](../validation/REM-008-maintainer-frozen-inputs.json)
provide the exact remediation delta `486f3cf..820e252`, complete original WS-06
aggregate `99bde514..820e252`, 41 authority hashes, eight report hashes,
24 historical evidence hashes, five builder evidence hashes, all 985 tracked
product byte hashes, five unrelated fingerprints, seven tactical tasks, ten
original criteria, five remediation criteria and all 16 required commands.
The [lossless builder evidence](REM-008-builder-evidence.yaml) archives 1,983
verified original members, including source scripts, full command logs and exits,
local Chroma/SQLite observations, initial failures, final checkout and isolated
built-distribution probes, 16 offline wheels and dependency proofs. The archive
SHA256 is `bac6f7861e0302ec3598fc702b44614ee85b5f25869e06b2dbfb6efeac207389`.

The original VAL-014 checkout and isolated-distribution retry reproducers each
exit 0 on the corrected candidate with one committed record, one SQLite entry,
no retry error and no pending task. The 16 required command exits were
`0,0,0,1,0,0,0,1,0,2,0,0,0,0,0,0`. Focused coverage is 170 passing tests;
Ruff and meaningful Python-3.13 typing across all nine original affected
sources pass. Full Chat PTY/localhost fixture errors, integration board-count
assertion and default mypy NumPy target-syntax failure reproduce against the
immutable approved base. Offline clean resolver installation still lacks cached
`litellm`; isolated declared-distribution wheel imports and production probes
were separately completed. The complete logs and baseline reproduction remain
available in the archive.

Controller scope/freeze checks confirm the exact nine implementation paths, 68
original frozen inputs, 977 outside-scope product files and all five unrelated
fingerprints unchanged. The original VAL-014 request, report and evidence bytes
remain unchanged. The implementation report's phrase that the VAL-014 **status**
file remained byte-exact is imprecise: that status is mutable controller metadata,
updated at approval/start and now marked superseded for decisions on this changed
candidate. This status edit changes none of the original independent review
artifacts or its historical `CHANGES_REQUESTED` outcome.

The remediator and controller checks are implementation evidence. The maintainer
explicitly reserved validation with “i will Validate afterwards.” No validator
was dispatched, and no VERIFIED result, WS-06 acceptance, later workstream or
delivery is claimed. Board phase is validation/state pending; the wider
initiative remains started/granted/normal/local.

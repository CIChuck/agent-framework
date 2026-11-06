# Foundation readiness decisions — RD-01

Date: 2026-11-06
Maintainer: Chuck Russell
RD-01 status: **APPROVED** by direct instruction: “ok i approve rd-01”
CD-CMD-FND-001 status: **APPROVED** by direct instruction: “i approve cd-cmd-fnd-001”
Applies to: CMD-FND-001 only

## Approved sequencing amendment

Build only the isolated, standard-library command foundation before full
family-contract/P1 closure. Its scope is the already approved API-01–API-06:
typed metadata/requests/results, registry, parsing and injected-handler dispatch.
No production handler, client wiring, command migration or retirement is
approved by RD-01.

The approved definition is RD-01 in the frozen readiness candidate
`d003c4db31cc9b1e3d143fd8c0d8b930db50ab30`, with API SHA-256
`e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74`.
The [readiness summary](../readiness-review.md) and
[draft directive](../directives/CD-CMD-FND-001-neutral-foundation.md) retain their
reviewed bytes; this record supersedes their unapproved-RD-01 labels only.

Do not defer any foundation API/invariant test, neutral import boundary,
standalone wheel proof or fresh independent implementation review. Full
command behavior signoff, family capabilities/service ownership, host progress/
cancellation, supported-client/platform and scenario obligations stay required
before their affected later units. Full P0/P1 and feature acceptance remain open.

## Packaging resolution and remaining approval

RD-02 records two independently VERIFIED, separately authorized corrections:
legacy launcher retirement at `06285ae4` and required finance at `d003c4db`.
See [finance validation](../validation/required-finance/report.md). These need
no deferred defect waiver; this evidence establishes packaging/import behavior,
not complete client/runtime health.

The maintainer subsequently approved CD-CMD-FND-001 by name, using the exact
directive and proposed reviewed execution base
`d003c4db31cc9b1e3d143fd8c0d8b930db50ab30` presented in this handoff. Record its
SHA-256 and unchanged API input in authority.json before implementation. This
approval accepts the supplied architecture/readiness evidence for the pinned
API and permits only the directive's API-01–API-06 foundation, paths, required
cohort integration and verification. Earlier draft/unapproved labels in frozen
review inputs are superseded only by these recorded human decisions.

Approval/evidence/status records necessarily follow the reviewed source base.
Before construction verify that those preparation commits change only the
named administrative records, with all product bytes and approved API/directive
identical to `d003c4db`. Keep that SHA as the implementation source/diff baseline
and record the actual administrative starting HEAD. This does not permit any
unreviewed product or directive change before construction.

No command migration/retirement, client wiring, later unit, full P0/P1 closure,
feature acceptance, merge, publication or release is authorized. A stable
foundation candidate must receive fresh independent implementation validation.

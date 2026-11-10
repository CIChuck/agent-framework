# MAINT-001 — reconciled implementation verification

**VERIFIED**, full bounded implementation and aggregate at
`b15ee091a1bfae07b61de521d6478b39ca4b48d2`. No mandatory findings.

| Reviewer | Outcome | Score | Formal report |
| --- | --- | --- | --- |
| GPT-6 Astra/high | VERIFIED | 9.5/10 | [Astra](council-round1/astra-report.md) |
| GPT-6.1 Sol/high | VERIFIED | 9.6/10 | [Sol](council-round1/sol-report.md) |

Both independently satisfy the maintainer's threshold. All MI-01–12 pass.
[Reconciliation](council-round1/reconciliation.json) retains exact identities and
report hashes (Astra raw bytes are also retained in a deterministic compressed
archive; its readable copy removes only a blank EOF line); [controller integrity](council-round1/controller-integrity.json)
confirms the frozen inputs and protected state before this docs-only closeout.
Product/artifact source is `ae15a5374350807bd909bc823078087a53a47ce4`; runtime
source is `6318959eeb4bed55ded0f22d66519645317b97de`.

Each reviewer freshly reproduced Memory802+one existing skip, Commands621,
CLI155, Chat1413/15,46 named cases, static/admin checks, an independent closed
build and four actual installed normal/optimized probes. Each own build matches
all154 artifact hashes in both supplied trials and the1/138 closure profiles.
Representative source/copy-install/semantic refusals were reproduced; larger
matrices and replay were inspected/hash-verified as each report specifies.
These are distinct evidence classes, not claims that every control was rerun.

The15 Chat failures remain failed:14 immutable expectations reject only the
approved reorganize help/metadata cells, and one reflects preserved dirty YAML.
The bounded exception comparison and clean committed-default check pass. Root
Ruff534, test_display collection conflict7196 and seven legacy whole-file format
failures remain failed/unwaived. No whole-repository-green claim.

No product mitigation is requested. Astra's advisory retains macOS arm64 /
Python3.13.10, deterministic-provider and operational limits; Sol independently
records the same limits. Human stage progress, responsiveness and live-provider
behavior still require the [targeted UAT](../../../uat/maintenance-reorganization-uat.md).

**Next gate:** human UAT and separate bounded MAINT acceptance. Neither is
completed or implied. No push, merge, release or broader refactor authority.
[Handoff](acceptance-handoff.md) gives the verified build and launch procedure.

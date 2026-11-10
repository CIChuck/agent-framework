# PILOT-001 round-four council reconciliation

Candidate: `f7035bbdd1b18c6301848b4214398d8adfbe18ed`.
Scope: proposed contract/directive and diagnostic harness readiness only.

**CHANGES_REQUESTED.** OpenAI 9.0/10, Claude 9.0/10, Gemini 9.5/10.
All scores meet the requested threshold; all three formal verdicts require changes.
[Full independent reports](council-round4.json) remain exact historical text.
No score, majority vote or prior result closes an unresolved mandatory finding.

Before these closeout records, controller end verification matched the frozen
request, HEAD, status, index, 36 authority/deliverable pins and all 17,094
protected hashes. The source inventory/private Git archive correction is
independently verified closed by all three reviewers. The exact contract,
directive and harness bytes reviewed at the candidate remain unchanged.

## Proposed bounded correction scope — awaiting maintainer direction

| Finding IDs | Required fix | Acceptance evidence |
| --- | --- | --- |
| SOL-R4-PILOT-001; ARGON-R4-ADV-002 describes the same issue as advisory | Parse long `--option=value` separately from attached short `-oPATH`/`-o=PATH`, preserving embedded `=` inside PATH. | Fresh scratch-only argparse writer controls for both forms with `=` in filename and parent directory, including Darwin case variants. Each attempt must refuse before child execution and preserve victim SHA-256. Existing positional/long-option/short-option/case/repeated-label controls still pass. |
| SOL-R4-PILOT-002, CLD-R4-01, ARGON-R4-001 are duplicate reports of one defect | Replace the directive's embedded revision-3 contract digest with the unchanged current contract SHA-256 `e625123b8222262fb02b32aeadb2cae5c91d18ff573f04763b0af7ea3f22eb8c`; preserve revision 4 in history and refresh the directive's current authority pin. | Programmatically assert equality of embedded directive contract pin, live contract SHA-256 and current authority contract pin; also verify current directive SHA-256 against authority. Freeze these cross-document assertions with the next review request. |

The second defect was missed when the builder updated the contract. It needs
correction before either document is approved. The contract itself needs no
further change for these two fixes.

Documentation impact: align the directive's receipt-path description with its
existing attached-option and Darwin case-fold requirements (CLD-R4-A1 and
ARGON-R4-ADV-001), append execution evidence and proposal history, and reconcile
current board/dashboard/status. Preserve historical reports, capture program,
golden 196 observations, product/test/package/lock bytes and both dirty examples.
A changed candidate requires fresh independent delta and aggregate validation
under repository policy. Review scope and number of providers must be part of
the maintainer's next instruction; this plan launches no new review itself.

## Other advisories — recorded, outside the proposed mandatory fix

- CLD-R4-A2: clustered short options fall outside the documented single-option
  forms; do not broaden the parser/guarantee in this bounded pass.
- CLD-R4-A3: optionally revalidate the prepared build wheelhouse/guards and
  record guard and uv executable hashes at bundle entry. Preparation presently
  performs the initial verification; recorded as future hardening.
- CLD-R4-A4: deterministic Git calls could clear ambient `GIT_*` and pin `-C`
  and `--full-tree`; current subdirectory behavior fails closed. Deferred.

## Stop point

The maintainer authorized one additional correction pass and council after the
previous cycle-limit escalation. That pass is complete, with mandatory findings
still open. Under the [independent-validation policy](../../../../../reference/policies/independent-validation-policy.md),
return the findings for maintainer disposition. No further automated remediation,
new council round, pilot construction, acceptance or external delivery is
inferred. Initiative remains started/local; only its diagnostic readiness is
under review. Foundation and RET-001 acceptance remain separate history.

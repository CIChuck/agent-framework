# Foundation design approval-readiness review

Initiative: friday-command-refactor
Work unit: CMD-ARCH-REVIEW-001
Mode: full scoped planning review; not implementation verification
Deliverable basis: e083116a27556a93f1e9ac9df14f514927f8fee6
Base: 25d2dcb6
Selected deliverable diff: `25d2dcb6..e083116a`
Review candidate: the commit containing this request; controller supplies full SHA
Authority: [manifest](architecture-review-manifest.json), with exact content hashes
Documentation exemption: [planning authority](../authority/planning-review-2026-11-04.md)

Review the complete foundation API draft, its architecture context and draft
foundation directive for readiness to present the foundation DESIGN to the
maintainer. Do not require future family schemas to be complete if explicitly
excluded from this limited approval; do require their remaining gates to stay
intact. This review is not API approval, construction approval or P0/P1 closure.

## Mandatory criteria

- AP-01: Matches the recorded nine removals, tools retention, shared ownership,
  generic CLI preservation and retained-quirk policy.
- AP-02: Foundation public types, parsing, registration atomicity and execution
  behavior are precise enough to approve without implementer-invented semantics.
- AP-03: Neutral imports, typed outcomes, ownership and error/cancellation/security
  boundaries are coherent and do not silently change protected behavior.
- AP-04: Draft directive matches API-01–API-06 with exact allowed files, independent
  positive/negative/install proof and concrete stop conditions.
- AP-05: Existing evidence is represented faithfully; future behavior, installed
  proof and incomplete P0/P1 are not claimed complete or bypassed.
- AP-06: The proposed first approval is design-only. There is no automatic source
  authority from this review, the design approval, or a green result.

## Required checks and boundaries

Read AGENTS, policies, manifest authorities and the selected diff. Verify every
manifest hash and HEAD at start/end. Existing dirty paths are excluded and must
remain untouched: backlog/friday-tui-command-followups/README.md under planning,
and Chat config.example.yaml / models-config.example.yaml.

Run board validate, documentation lifecycle and git diff --check. Inspect source/
tests as needed to check design claims. Do not run effectful tests or providers,
edit any repository file, commit, push, mutate board, delegate or perform external
actions. No credentials or costs authorized. Existing baseline/probe evidence is
input to inspect, not builder conclusions to trust. Reports return to controller
in the final response; controller stores them afterward.

Return VERIFIED, CHANGES_REQUESTED or BLOCKED for AP-01–AP-06 only, with reviewer
identity/fresh-context provenance, full candidate and manifest identity, findings
with stable IDs/severity/paths/requirements/evidence/required fix and verification,
criterion-evidence matrix, actual commands/results and scope limits. A successful
result means scoped design approval-readiness, not formal implementation validation.

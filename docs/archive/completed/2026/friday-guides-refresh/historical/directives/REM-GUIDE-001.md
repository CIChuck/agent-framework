# REM-GUIDE-001 — Required tools and screenshot status

Status: authorized by the maintainer's all-guide correction instruction and
CD-GUIDE-001's explicit bounded factual-remediation clause. No new product work.

Controlling authority: authority.json and CD-GUIDE-001 remain unchanged.
Frozen reviewed candidate:6691aa2428b81ed96fd8d404f6b3f5a0f1e82f13.
Independent report: validation/initial-review/report.md, CHANGES_REQUESTED,
findings GUIDE-001 and GUIDE-002 only.

Allowed guide changes:
- docs/guides/05-tools.md
- docs/guides/09-cli-reference.md
- docs/guides/13-troubleshooting.md
- docs/guides/14-appendices.md

GUIDE-001: clarify all four affected descriptions that manual tool injection
retains tools.context.required_tools. Manual mode suppresses optional automatic
choices; required plus manual names remain subject to admission/schema/count
budgets. Distinguish Chat context settings from agent-profile required_tools.
Do not modify tool selection or registry source/metadata.

GUIDE-002: mark web_screenshot as a stub; its handler returns an unimplemented
error without fetching a page. Clarify the catalog legend to include explicit
unimplemented return values as well as raised exceptions. Do not implement
screenshots or suggest dependency installation alone activates the stub.

Required verification: independently supplied guarded contract probes for
required/manual union and screenshot outcome, changed-guide render/link/metadata
checks, aggregate docs/board/whitespace, stable candidate freeze and fresh-context
read-only review. Existing examples, versions, authority and other21 guides
remain byte-identical. Governance/evidence updates for this remediation are
allowed. Stop on unrelated guide/source/API/dependency/runtime changes.

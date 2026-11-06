# Development skill maintenance — SKILL-MAINT-001

Date: 2026-11-06
Maintainer: Chuck Russell
Authorization: “Proceed with the improvements,” following the scoped skill review.
Status: Approved bounded maintenance scope; independent validation pending

The approved scope is the imported development skills and their index. Follow
repository AGENTS.md and engineering/independent-validation policies. This
directive records the exact helper change authorized by the maintainer; it does
not authorize command-refactor construction or change its design/directive gates.

## Changes and acceptance

1. The fallback `scripts/pr-wait` must stop with exit 1 and an explicit unknown
   required-check configuration message if either protection query fails. Never
   use partial results or treat HTTP 404 as proof of absent protection. Successful
   queries still combine and deduplicate names; successful empty queries retain
   existing behavior. Test permission, not-found, rate-limit and server failures,
   partial discovery, and both green/ready modes with passing visible checks.
2. Align full-send/babysit waiting: register the T3 watcher and yield the turn;
   preserve the watch while awaiting continuation; unwatch at actual handoff or
   blocker. Follow active harness rules for all tools.
3. Add an explicit frozen-candidate, fresh-context independent validator step
   before delivery of applicable generated work. Advisory Sol outcomes do not
   replace VERIFIED. Any subsequent candidate/authority change requires review.
4. Update the skills index to distinguish authoring/review skills, execution
   workflows and reference-only templates. Include the nine imported workflows.
5. Exclude copied Python bytecode using the existing Git ignore rules; do not
   deploy or stage it. Preserve unrelated work and historical evidence.

Allowed paths: `docs/dev-skills/README.md`, the nine imported workflow bundles,
and this bundle's `tests/` and `references/` for regression tests and maintenance
evidence. Existing authoring skills and product packages remain unchanged.

Run the bundled offline unittest suite, the skill metadata/link checks, board
validation, documentation lifecycle validation and whitespace checks. No live
GitHub, provider, PR, account, credential, push, merge or release effects.
Known baseline: documentation lifecycle has four broken links in imported TUI
evidence outside this scope. A passing skill check does not waive that failure.

Freeze only skill-related paths in a stable candidate commit for one fresh-context
read-only independent review. Report the candidate, required checks, excluded
dirty work, findings and remaining limits. Stop for scope expansion or mandatory
findings outside this directive; no automatic council or remediation loop.

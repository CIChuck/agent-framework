# CD-CMD-DEP-001 — require finance for the tools package

Date: 2026-11-06
Status: APPROVED for the exact dependency correction requested by Chuck Russell
Initiative: `friday-command-refactor`
Branch: `feature/command-refactor`
Execution base: `06285ae446f609f0546866b951dff611cbb447bf`

The maintainer requested making finance mandatory in pyproject.toml after the
default-install tools import failure was explained. This directive binds that
specific metadata repair before editing. The tools package unconditionally
imports finance today; its normal dependencies must provide that existing
import. The newly validated legacy CLI launcher retirement is retained.

## Exact scope

- `packages/friday-tools/pyproject.toml`: add
  `friday-framework-finance==0.1.0a4` to project.dependencies. Keep the existing
  finance extra/pin as a compatibility alias for consumers using `[finance]`.
  No other version, dependency, source, extra or build setting changes.
- `packages/friday-tools/README.md`: explain finance/SDK are installed by
  default; credentials/configuration remain required for provider use.
- `uv.lock`: add only the tools-to-finance unconditional dependency and its
  corresponding requirements metadata. Preserve all existing package versions,
  sources, artifact hashes, other graphs, extras and resolution options.
- Related command readiness/draft/map/authority and process records: record
  the deliberate dependency choice and fresh default profile. Preserve old
  raw probes/reviews and distinguish their historical failures. Finance and
  launcher baseline defects must not remain falsely described as current once
  verified; no full runtime-health or installed-client acceptance follows.
- `validation/required-finance/` proof/request/report and the pending legacy
  removal result; board task/event and generated dashboard for process only.

No product Python source/test, finance provider behavior, credentials, API/model/handler,
Chat script, developer-environment sync, foundation package or unrelated work
may change. No live provider/tool calls, uploads, push/merge/release are allowed.
Foundation Step 4 and full P0/P1 closure remain separate/unapproved.

## Verification and stop conditions

Use offline lock generation without upgrades. Compare parsed lock documents:
only the two expected additions within the existing tools record are allowed;
all other records/options must match. If cached resolution is unavailable,
report it and use no alternate registry or upgrade without disposition.

Controller disposition: the documented offline resolver hits the pre-existing
`litellm==1.100.1` cache gap. The user-authorized dependency correction permits
mechanically adding only the required tools-to-finance edge and corresponding
unmarked requires-dist entry to the existing lock record. Finance/SDK and all
their resolved dependencies already exist in that lock. Preserve every other
parsed value and run `uv lock --check --offline --no-python-downloads`; a fresh
default wheel resolution must independently prove the resulting dependency
closure. This is not a claim of successful full offline regeneration. No
registry access, package addition/version upgrade or broader workaround follows.

Build tools wheel/sdist offline. Assemble a disposable wheel set containing
the current retired-launcher CLI wheel and required-finance tools wheel plus
unchanged cohort wheels. Install default Chat/CLI with declared dependencies
only, without requesting finance/sandbox extras. Check dependency consistency,
unmarked finance Requires-Dist in tools metadata, installed finance/SDK and
successful isolated imports of tools and finance without API credentials.
Prove unchanged 50/3 registry metadata, Chat help and absence of retired `friday`.
Guard network before imports; do not construct provider clients or runtime/stores.

Use a separate remediator for the package-boundary metadata/lock change under
repository policy. Run relevant existing tools/cohort metadata tests and
artifact checks, offline lock check, board/docs/whitespace validation. Preserve
the four declared TUI-link baseline, the approved API and all 84 inventoried
Python source/test hashes. No new mirrored unit test is needed; the clean
installed-wheel import is the regression proof for this dependency defect.

Commit a stable candidate, then obtain fresh read-only independent validation
of this unit and affected readiness delta. Prior reports do not verify changed
bytes. Stop for scope drift, lock/version drift or unresolved validation
findings. No automatic council or remediation loop is authorized.

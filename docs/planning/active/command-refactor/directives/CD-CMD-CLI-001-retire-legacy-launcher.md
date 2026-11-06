# CD-CMD-CLI-001 — remove the legacy framework CLI launcher

Date: 2026-11-06
Status: APPROVED for this exact removal by Chuck Russell's direct instruction
Initiative: `friday-command-refactor`
Branch: `feature/command-refactor`
Execution base: `144378ac0d0cc4c9b1f9f85511264f6919e23997`

## Authority and exact change

The maintainer instructed: “That should be removed from the TOML file. That is
a legacy error.” This approves deletion of `[project.scripts]` and its sole
`friday = "friday_cli.main:app"` declaration from
`packages/friday-cli/pyproject.toml`. Record this bounded directive before
editing package metadata, under AGENTS.md and repository engineering/validation
policies. The package remains a reusable framework component library; no
replacement launcher or `app` implementation is authorized.

Allowed changes:

- `packages/friday-cli/pyproject.toml`: exactly the legacy script-table removal.
- `packages/friday-cli/README.md` and root `AGENTS.md`: correct descriptions of
  the retired executable; no unrelated policy or package rewrite.
- Current command-refactor readiness summary, draft foundation directive,
  unit/scenario map, authority JSON, main index/checkpoint and execution log:
  record the human disposition and remove obligations to restore/prove a
  standalone framework CLI launcher. Retain supported application entry-point
  acceptance and source-level framework CLI regression.
- New `validation/legacy-cli-removal/` evidence/request/report; board task/event
  and generated dashboard for this unit's process/evidence only.

No Python source/tests, dependencies, version, lock, finance loading, Chat
launcher, handlers, foundation package, installed developer environment or
historical review/probe evidence may change. Preserve unrelated dirty files.
This unit does not approve the foundation directive, RD-01/RD-02 or Step 4.

## Acceptance and checks

1. Parsed package TOML is identical to the execution base after removing only
   `project.scripts`; no replacement entry point appears.
2. Offline build produces a valid CLI wheel/sdist whose metadata declares no
   console script. Install the wheel without dependencies into a fresh
   disposable venv; inspect distribution metadata and verify no `friday`
   executable is installed. No application/runtime imports are required.
3. Run focused existing cohort metadata tests, package metadata validation,
   selected CLI artifact validation, offline lock consistency, board validation,
   documentation lifecycle and whitespace checks. No new test file is needed
   for this metadata removal. Preserve the four unrelated TUI-link baseline.
4. Record the CLI launcher as intentionally retired, not an unresolved feature
   to restore. Finance remains a separate unresolved default-profile defect.
   Historical wheels/logs/reviews keep their original observations and hashes.
5. The foundation API and all 84 inventoried Python source/test hashes remain
   unchanged. Freeze the updated candidate for fresh independent read-only
   validation of this exact metadata removal and affected readiness delta.
   Earlier full readiness validation remains historical for its exact candidate;
   aggregate feature-branch implementation review remains before later merge.

Build/install only offline with local cached tools; do not sync the repository
venv, access live providers/tools or construct runtime/stores. Direct outputs
to disposable paths and the named evidence directory. Commit only allowed
files and obtain required fresh validation. Stop for scope expansion, new
metadata/dependency needs or check failures outside the documented baseline.
No push, PR, merge, release or deployment is authorized.

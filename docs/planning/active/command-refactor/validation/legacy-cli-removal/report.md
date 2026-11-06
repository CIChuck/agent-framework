# Legacy framework CLI launcher removal — VERIFIED

Date: 2026-11-06
Candidate: `06285ae446f609f0546866b951dff611cbb447bf`
Base: `144378ac0d0cc4c9b1f9f85511264f6919e23997`
Outcome: **VERIFIED** for CD-CMD-CLI-001 and affected readiness delta

Fresh independent validator `/root/legacy_cli_removal_validation`, a GPT-6-based
Codex agent (exact served version unavailable), reviewed the complete 23-file
diff from `2026-11-06T21:13:08Z` through `21:15:27Z`. No builder transcript or
private reasoning was supplied; no delegation, repository writes or external
actions occurred. Shared dirty-checkout exceptions were explicitly pinned.

Request SHA-256 matched
`282bda1e6f244b723e185556099ce333c8b5be47c2c1d026db9a1ffd8f024b17`.
All 11 authority/23 deliverable pins, protected-manifest SHA-256
`3b6d0e4dc0d6056d9c10c19ac3a90f6c3a8977c7c5456bda9faa5e9d3c495329`
and 16,879 protected hashes matched at start/end. HEAD/status stayed identical.

No mandatory findings. All five criteria were VERIFIED:

- CLI-01: parsed TOML differs only by removing the exact legacy script table;
  no Python, dependency, version or lock change.
- CLI-02: artifact hashes/integrity match; wheel has no entry-point metadata,
  sdist TOML matches source, isolated install has zero entry points/no `friday`
  executable and retains 13 library files. Chat launcher metadata is unchanged.
- CLI-03: current docs/readiness/SC-08 explicitly retire the launcher; no
  restoration obligation. All 74 pre-existing validation files excluding the
  deliberately updated unit map remain identical. Finance remained unresolved
  in this candidate; its later repair is a separate unit.
- CLI-04: independent guarded offline CLI/cohort run passed 158 tests in 0.23s.
  Metadata (17 projects), artifact (one wheel/one sdist), lock (213 packages),
  board (36 tasks) and working/selected-diff whitespace checks passed.
- CLI-05: all 84 source/test hashes and approved API SHA-256 remain unchanged;
  Step 4/RD-01/RD-02 remain unapproved, with current candidate/base explicit.

All Python used `-B`/PYTHONDONTWRITEBYTECODE; uv was offline/no-sync/no-cache.
Before pytest/application imports, network audit hooks rejected connect, bind,
DNS and sendto. Tool versions: uv 0.11.3, Python 3.13.10. One initial `python`
invocation failed because the executable was absent; `python3` succeeded.

Documentation lifecycle reports exactly the four existing TUI links:
N01B-04:37, N01B-05:49, N01B-06:37 and VAL-N01B-07-prepush-a196e95a:35.
Build/install were not repeated: stored commands, archives/hashes and the
isolated installation were independently examined. No developer-venv sync,
live provider/tool execution, runtime/store construction, broad suite or
foundation build occurred. See [request](request.json) and [receipt](receipt.json).

This is the controller's durable transcription of the independent result.
It grants no foundation construction, acceptance or delivery authority. The
subsequent requested finance dependency change needs its own scope/review.

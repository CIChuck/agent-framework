# Required finance dependency — VERIFIED

Date: 2026-11-06
Candidate: `d003c4db31cc9b1e3d143fd8c0d8b930db50ab30`
Base: `06285ae446f609f0546866b951dff611cbb447bf`
Outcome: **VERIFIED** for CD-CMD-DEP-001 and affected readiness delta

Fresh independent Codex validator `/root/required_finance_validation`, GPT-6
family (exact served version unavailable), reviewed the complete 36-file diff.
Review timestamps: `2026-11-06T21:27:01.979289Z`–`21:30:18.360947Z`. No builder
transcript/private reasoning, delegation or repository writes occurred. Shared
dirty-board/dashboard exceptions were explicitly pinned.

All 11 authority/36 deliverable pins, request SHA-256
`543e70b3793b5955d42b0971d0df80f470eec6c409e85c2bcdbdba48fa661860`,
protected-manifest SHA-256
`6a0321993d613fd5fb162c9a2ab1bef80e66f8a292fc5a713838d14fc1e03f90`
and all 16,876 protected hashes matched at start/end. HEAD/status stayed identical.

No mandatory findings. All five criteria were VERIFIED:

- DEP-01: parsed tools TOML differs only by the exact required finance pin;
  compatibility extra and all other metadata remain intact. Existing imports
  justify the unconditional dependency.
- DEP-02: parsed lock equals its base after removing exactly the new dependency
  edge and unmarked requirements row. All 213 resolutions/options/graphs/extras/
  sources/artifacts remain unchanged. Mechanical disposition and failed full
  offline generation are accurately disclosed; consistency check passes.
- DEP-03: independent isolated replay matches the 129-version default profile
  without extras/credentials. Tools, finance, SDK and public tool import pass;
  50 names/three aliases, parser/dispatch fixtures and Chat help are preserved.
  Retired framework launcher remains absent; dependency check passes.
- DEP-04: all receipt/artifact hashes match; wheel CRC and sdist TOML checks
  pass; tools wheel includes required finance and compatibility extra. All 399
  inspected installed Python/metadata files match wheels. The 84 source/test
  hashes and approved API are unchanged. Focused tests and metadata/artifact/
  lock/probe lint/format checks pass.
- DEP-05: current descriptions/readiness/draft/map record both packaging
  resolutions and retain pending foundation approval. All 85 earlier validation
  paths except the deliberately changed unit map remain identical. No foundation
  package exists; CLI retirement remains unchanged.

Independent commands: guarded offline focused tools/cohort tests (12 passed
in 0.13s), 17-project metadata check, selected tools/CLI artifact checks (two
wheels/two sdists), offline lock consistency (213 packages), default dependency
check (129 compatible packages), probe Ruff lint/format, board (36 tasks) and
working/selected-diff whitespace checks all pass. Documentation lifecycle
returns only four existing TUI links: N01B-04:37, N01B-05:49, N01B-06:37 and
VAL-N01B-07-prepush-a196e95a:35.

Python used `-B`/PYTHONDONTWRITEBYTECODE; pytest/uv/Ruff caches were disabled.
Audit guards preceded application imports; credentials were removed without
disclosure. Replayed output differs only in cwd. Two events were blocked:
create_connection and socket.bind; LiteLLM used local fallback. No successful
application network request occurred. Tools: uv 0.11.3, Python 3.13.10.

Build/install commands and archives/installed bytes were inspected rather than
rerun. Full offline lock generation was not repeated; its known cache failure
and initial missing-sdist scratch check remain preserved. Two exploratory reads
used nonexistent filenames before corrected paths were inspected. No broad
suite, runtime/store/client construction, provider call, environment sync or
external mutation occurred. Packaging/import proof is not runtime/UAT acceptance.

This is the controller's durable transcription. See [request](request.json)
and [receipt](receipt.json). The next gate is Step 4's exact foundation directive/
base approval and RD-01 sequencing decision, with RD-02 resolution recorded.
The subsequent human RD-01 decision is tracked separately in the approval record.
No foundation, aggregate branch, acceptance or delivery authority is granted here.

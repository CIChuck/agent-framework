# Independent validation — CMD-FND-001

VERIFIED — CMD-FND-001 foundation only.

Candidate: `b4fc199eeef3c63a5cf9a8b960cf61c0116170ad`

Implementation diff: `1b4756b7bd5bc7fb9ec84c45550ec6cdf0389688..b4fc199eeef3c63a5cf9a8b960cf61c0116170ad`

Approved source base: `d003c4db31cc9b1e3d143fd8c0d8b930db50ab30`

Fresh-context Codex validator `/root/foundation_implementation_validation`, GPT-6 family; exact served model version unavailable. No builder transcript or private reasoning was supplied. The builder report was inspected as candidate documentation; its conclusions were independently checked. No delegation or repository writes occurred. The recorded preservation window was `2026-11-06T22:32:40Z`–`22:36:28Z`; exact context-creation time is unavailable.

The complete 21-file implementation diff and nine-file administrative preparation diff were inspected. All 16 authority, 21 deliverable, 33 external-input, committed shared-file and 16,876 protected-file hashes matched at start/end. HEAD, branch and working-tree status remained unchanged. [Request](CMD-FND-001-request.json) SHA-256 remained `84b1919399ba6ad66cdd4dd96d14f1527a33ccf06f2776f5d4f9ffac6c3d63a4`.

The current approval record explicitly approves RD-01 and the exact directive/API for this foundation. Preparatory changes are confined to the declared administrative paths; approved API/directive bytes remain unchanged.

No mandatory findings.

| Criterion | Result and independent evidence |
|---|---|
| API-01 | VERIFIED. Standard-library source/import closure; dependency-free distribution, typed marker, no entry point/default handlers; fresh outside-checkout wheel installation and guarded smoke pass. |
| API-02 | VERIFIED. Registry source reconstructs canonical immutable metadata before single-map publication. Tests and independent probes establish trimming, preserved arguments/detail, one-pass keys, collisions, failure atomicity and shared canonical identity. |
| API-03 | VERIFIED. Approved frozen grammar fixtures pass, including quoted fragments, `//HELP`, unknown `///HELP`, slash/space order and aliases. Independent Unicode-whitespace and unusual slash-key probes pass. No generic argument policy or CLI adapter introduced. |
| API-04 | VERIFIED. Contracts implement the runtime table, strict booleans, exact model/data membership, collection snapshots and relationships. Constructor negatives, optimized-Python checks and additional field-order/subclass probes pass. No source `Any`, casts, suppressions or assertion enforcement. |
| API-05 | VERIFIED. One injected call/await, custom awaitables, wrong-return rejection, exception identity and cancellation propagation pass. Additional synchronous-call and await-stage exception probes preserve registry state and invoke once. |
| API-06 | VERIFIED. Empty default registry; all 84 inventoried client source/test hashes unchanged. Guarded current Chat capture equals frozen JSON values: 50 canonical names, three aliases, zero drift. |
| FND-01 | VERIFIED. Approved package/root/cohort/inventory integration only. Exact parsed-lock comparison removes solely the permitted member, package and two root references; everything else equals the approved base. Artifact guards and all three independent refusal cases pass. |
| FND-02 | VERIFIED. Complete frozen typed surface and runtime table supported by source inspection, constructor tests, mypy and independent adversarial probes. |
| FND-03 | VERIFIED. Canonical registration, immutable snapshots, direct parsed-key lookup and atomic rejection satisfy the approved semantics. |
| FND-04 | VERIFIED. Execution, meaningful tests, approval/source-base provenance, reporting and scope controls are evidenced. Broader failures are reproducible and accurately distinguished from scoped results. |

All package/root checks used:

```text
uv run --offline --frozen --no-sync --no-python-downloads
  --with-editable packages/friday-commands …
```

Application probes installed a network audit guard before imports. Python bytecode writes and pytest/Ruff caches were disabled; mypy used reviewer scratch.

| Check | Actual result |
|---|---|
| Guarded source origin/version | Exit 0; current package source, `0.1.0a4`, established before pytest |
| Foundation + cohort pytest | Exit 0; 145 passed |
| Selected Chat registry/foundation pytest | Exit 0; 19 passed |
| CLI owning pytest | Exit 0; 155 passed |
| Focused Ruff | Exit 0 |
| Ruff format `--check --no-cache` | Exit 0; eight files formatted |
| Mypy source + artifact checker | Exit 0; four source files |
| Package metadata | Exit 0; 18 projects |
| Board validate/next/show | Exit 0; 36 tasks; selected initiative started/granted/current branch |
| Exact directive parsed-lock comparison | Exit 0; saved base lock equals approved Git source |
| `uv lock --check --offline --no-python-downloads` | Exit 0; 214 packages |
| Working, implementation-diff and approved-base-diff whitespace | Exit 0 |
| Fresh offline wheel/sdist build | Exit 0 |
| Valid artifact checker | Exit 0 |
| Missing typing/dependency/entry-point artifact probes | Each exits 1 with its required targeted refusal |
| Fresh offline no-deps venv install + outside-checkout `-I -B` smoke | Exit 0 |
| Wheel/source/installed module and metadata equality | Pass |
| Additional independent adversarial probes | Exit 0; 24 assertions |
| Guarded current Chat metadata comparison | Exit 0; 50/3, zero drift |

Exact check argv/exits and reproducible reviewer scripts are in reviewer scratch `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/cmd-fnd-independent-v263h57h`. Tools: uv `0.11.3`, Python `3.13.10`, pytest `9.0.2`, Ruff `0.14.10`, mypy `1.19.1`.

Freshly rebuilt artifact hashes exactly equal the frozen inputs:

- Wheel: `3d5d112ba05c0374a85c8263ac083290c0a48c8950ca2596648443e53b9a1cc8`
- Sdist: `3b68bae965eba0432165abfde639db79aca1645574ad41f2b564ed0c1a4eadf5`

Broader gates remain unsuccessful:

- Root Ruff exits 1: 534 findings across 13 files. Every affected file independently equals the approved source base.
- Root pytest exits 2: exactly the existing Chat/CLI `test_display.py` import-file mismatch during collection.
- Documentation lifecycle exits 1: exactly the four disclosed unrelated TUI links.

These results are baseline limitations, not green broad gates or new waivers. No candidate regression was identified.

One initial reviewer artifact-fixture attempt failed because reusing `ZipInfo` objects changed their in-memory offsets. The scratch harness was corrected to copy by filename; the complete artifact sequence then passed. No original artifact or repository file was changed. Guarded Chat import blocked LiteLLM's attempted remote price-map retrieval and used its local fallback.

Full Chat, providers/tools, runtime/stores, terminal/audio and Linux/Windows acceptance were not exercised. No lock regeneration, repository environment sync, delivery action or external mutation occurred.

The next gate is controller recording of this foundation-only result and the applicable maintainer handoff. Family contracts, wiring, migration, retirements, API-07–09, aggregate feature review and acceptance remain separate.

## Controller closeout

The controller transcribed the validator's returned report above, preserving its
findings, criteria, commands and limits. Source references are
`packages/friday-commands/src/friday_commands/{contracts,registry}.py` at the
candidate. Exact machine-readable command receipts, relevant logs and reviewer
scripts are retained in [the durable evidence receipt](CMD-FND-001-evidence.json),
copied without changing their original bytes or conclusions. The request and
builder report retain their frozen pre-review state. Subsequent index, board,
checkpoint and execution-log edits record this result only; they neither change
the governed implementation/API/directive nor extend approval. The initiative
remains started/local; the foundation unit awaits maintainer acceptance.

# REM-004 all-six generic compatibility diagnosis

Construction remains stopped. This is read-only source/private-probe evidence, not product verification, a waiver, or approval. Original generic files remain byte-identical to frozen `559ae9f`. All private probes ran through the guarded isolated `remediator-probe-01` snapshot; Python 3.13.10, mypy 1.19.1, Ruff 0.14.10 and Pydantic 2.12.5. No installs, synchronization, real network, original runtime state, authority changes or new product tests were used.

## Complete variance matrix

Each consumer independently imports the exact original module text and a second copy with only the selected class header changed to PEP 695. It probes both Parent-to-Child and Child-to-Parent return/assignment directions. Both directions must reject to preserve the existing invariant class contract. All six original `T` declarations are unbounded; Moltbook consumers use real Parent/Child Pydantic BaseModel subclasses. Existing source suppressions are retained exactly in these copied modules; none were introduced or broadened.

| Class and exact baseline UP046 site | Original Parent -> Child | Original Child -> Parent | PEP 695 Parent -> Child | PEP 695 Child -> Parent | Contract result |
| --- | --- | --- | --- | --- | --- |
| MemoryMetric, memory_views.py:34:20 | reject | reject | reject | reject | invariant preserved |
| CommandRegistry, commands.py:74:23 | reject | reject | accept | reject | changes invariant to contravariant |
| SessionContext, session.py:214:22 | reject | reject | reject | reject | invariant preserved |
| SessionManager, session.py:235:22 | reject | reject | reject | reject | invariant preserved |
| ToolAdapter, tools.py:127:29 | reject | reject | reject | reject | invariant preserved |
| MoltbookResponse, responses.py:14:35 | reject | reject | reject | reject | invariant preserved |

The static results reflect actual method contracts: MemoryMetric has its T input in `available`, SessionContext exposes mutable session state, SessionManager uses invariant SessionContext in its cleanup/context boundary, ToolAdapter accepts invariant `list[T]`, and MoltbookResponse exposes mutable Pydantic `data`. CommandRegistry uses T solely as `execute(context:T)` input; PEP 695 therefore infers contravariance.

`compatibility-matrix.json` pins each complete path, exact UP046 code/location/end-location/message, baseline file hash, directional results and minimal decision. `variance-matrix-raw.json` preserves full diagnostics, consumers and the exact one-site transformations. `variance-matrix-source/<Class>/{original,converted,consumer}.py` preserves all sources. Every original consumer rejection is a deliberate negative check; raw inner mypy exit1 is recorded, not represented as a mandatory candidate check failure or pass. The root runner exits zero because the probe records the results normally. All snapshots remain tracked-content unchanged.

## Runtime/public-model checks

The Moltbook runtime probe imports only private copies of its source with the same one-site header change and the installed Pydantic package. Parameterized Parent and Child models have identical JSON schemas, dumps, public subscript names and required-child-field rejection before and after. `pydantic-generic-raw.json` reports `schema_dump_contract_equal: true` and contains the complete schemas and results. This is a bounded compatibility probe; required owning-package tests and full changed-source typing remain pending.

In-repository searches found no generic `__parameters__`, `__orig_bases__`, `__type_params__`, covariance/contravariance attribute introspection or runtime type-argument consumer of these six public classes. New PEP 695 TypeVar objects still differ as runtime objects; the searches and directional/model probes do not claim arbitrary external consumer compatibility. Retained public names, full package checks and formal review remain required for the five eligible conversions.

## Legitimate annotation alternatives

For all six classes, original Generic[T] plus either explicit `TypeVar("T", covariant=False, contravariant=False)` or `TypeVar("T", infer_variance=False)` retains UP046 under the pinned Ruff. These meaningful declarations preserve old invariance but do not resolve the lint gate.

For CommandRegistry, PEP 695 with an equivalent `T: object` bound or explicit `self: CommandRegistry[T]` annotations at existing execute, command or __init__ sites still accepts Parent-to-Child and rejects Child-to-Parent. Therefore these legitimate same-interface annotations do not restore invariance. Exact sources and results are in `annotation-probes/` and `annotation-probes.json`. No artificial attributes/bases, renamed imports, casts, custom runtime hooks or suppressions were introduced. No legitimate invariant-preserving conversion was established under the permitted existing-site constraints.

## Exact conflict and minimal decision

Only `packages/friday-cli/src/friday_cli/commands.py` has demonstrated variance drift. The current finding remains:

- UP046, row 74 column 23, end row 74 column 33.
- Message: `Generic class CommandRegistry uses Generic subclass instead of type parameters` (the machine pin retains the exact backticks).
- Current and baseline whole-file SHA-256: `15992e7f38fe874f0104a164180679c7e76d7e09413d68152ef5cc77c0f99308`.
- Reviewed declaration/class/input snippet SHA-256: `a71121e6bc30ab8153a52c7e8b4da2bc06b156d2ada23c647b40e9391c90b5e5`.

`command-registry-conflict-pin.json` and `command-registry-reviewed-snippet.txt` contain exact paths, bytes, ranges and identities. No other permitted diagnostic edit belongs to this file. Keeping original Generic[T] means the line/location/hash can remain unchanged after the other authorized corrections.

The maintainer needs one precise decision: preserve the current invariant Generic[T] and approve an exact one-live-finding UP046 gate exception, or explicitly permit this class's contravariance change. Current R4-06 and WVR-002 permit neither. A live exception must separately reconcile WVR-002's zero-live requirement and must not expand the archival exception, Ruff exclusions, typing suppressions or any other live finding. The other five sites have no demonstrated variance-policy conflict and need no variance amendment based on this evidence.

## Partial regression preflight

`partial-regression-preflight.json` inventories the six retained partial files, 26 direct helper source hashes, exact imports, the dedented child-script hash, 13 precise existing regression function targets and all containing modules. It also lists the full-agent ordering prefix, the known registry precursor and all seven exact runtime nodes. No registry-preservation test has yet been added.

The only nested process is the literal synthetic Python PTY child. It inherits the pinned guard, isolated sources, credential-free allowlist and offline/no-sync settings. Bootstrap20s, child trigger10s, post-trigger acknowledgment0.8s, synthetic work1s, progress3s and wait/kill/reap5s are finite. Parent input PIPE and PTY descriptors close on normal and failure paths. Fake runtime construction defaults to fake=True and uses a UUID layout under the harness temporary directory; no original application state is accessed.

Reader writes are tmp_path-only synthetic containers. Exact optional imports are monkeypatched without unloading installed modules. Literal tests fail on any DNS or transport creation; domain answers are deterministic stubs and existing public WebReader tests use respx. The guard remains unchanged at `6f61ea4ca34c7abef9e0c709eb1e1feb0f3cf7733cbc59bc465d6b01182e9e81`.

The partial malformed-DOCX expected error may need an ordinary authorized R4-02 correction based on the installed library result; construction remains stopped, so no further edit was made. New test wrapping/lint and regression before/after proof are likewise incomplete. Root performs candidate checks and fresh full-suite preflight independently; no narrower probe closes any aggregate gate.

## Controller advisory verification of retained partial fixes

Root froze a new isolated HEAD1718ed2 snapshot with only the six retained allowed
edits and a fresh604-file safety inventory before selecting tests. Direct-helper
preflight is archived alongside it. Installed tools, offline/no-sync environment,
synthetic temporary data and unchanged network guard remained in force. These
uncommitted partial checks are advisory, not VERIFIED or aggregate closure.

- Whole Agent package followed by all seven Runtime DI tests:221 passed.
- Reader/Web validator/Web reader modules:105 passed,2 failed. Both failures
  are incomplete reader-test assertions: the malformed DOCX reports
  `Failed to read DOCX: File is not a zip file`; XLSX install guidance names
  `[spreadsheets]`, not `[documents]`. Production reader behavior is unchanged.
- PTY module:1 passed,1 failed. Early acknowledgment and bounded progress passed,
  then the child exited1 because its new cleanup assertion accessed nonexistent
  `runtime.maintenance_gate`; the existing owner is `app.maintenance_gate`.
- Exact literal child diagnostic reproduced that AttributeError under the same
  guard and allowlist. No repeated timing runs or expanded effects were used.

Raw logs and execution JSON preserve every exit, snapshot/overlay/guard/hash and
tracked-content comparison. Unfinished assertion fixes remain within original
R4-02/R4-04 authorization; no new failure waiver is proposed. Further construction
is paused solely for the actual R4-06 contract/lint authority conflict.

The proposed A06/WVR-003 chooses unchanged invariant CommandRegistry plus exactly
one current-code UP046 exception. They remain proposals pending maintainer
approval and fresh independent authority review. WVR-002 remains approved exactly
as originally recorded; its zero-live condition has not silently changed.

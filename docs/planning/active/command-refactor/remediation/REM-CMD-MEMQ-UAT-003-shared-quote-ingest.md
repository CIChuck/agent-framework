# REM-CMD-MEMQ-UAT-003 — shared entity quoting and ingestion metadata repairs

Status: authorized by Chuck Russell's current direction to attack the ingest and
node lookup issues, followed by “Proceed.” The approved technical scope is the
shared ownership discussed in this session. No new approval question is needed.
This directive records that instruction before implementation; it supersedes the
held/unapproved Chat-only REM-CMD-MEMQ-UAT-001 proposal only for these two repairs.

## Baseline and authority

Initiative friday-command-refactor remains started/granted/local on
feature/command-retirement. Base0e5c32371029af5fa4d0d5ddf76608ce9339fe6f.
The diagnostic implementation at3969e4d4 is independently VERIFIED, not a repair of
the actual verification response. This unit adds two functional repairs, then one
combined human retest. It grants no provider call, personal-store operation, model/
YAML/budget change, full reorganization execution, acceptance or delivery.
The maintainer's latest direction explicitly permits the small shared Memory and
Commands changes despite the ordinary framework parity freeze. Original MEMQ
contract/directive/approval and retained receipts remain unchanged; this amendment
supersedes only literal outer quotes for entity selection and absent-description
metadata. No new directive-readiness council or D0-D3 sequence is required.

## Exact behavior

Q: Shared friday-commands memory-query handling removes exactly one matching
ASCII single/double outer quote pair from the already-joined entity name, only
when the interior contains non-whitespace text. No shell parser or escape
interpretation; raw parser args and other commands stay unchanged. Internal
quotes/apostrophes, backslashes, Unicode and parentheses survive. Empty,
whitespace-only, unmatched or mismatched quote forms remain literal. Exact
lowercase unquoted first argument nodes retains its existing listing mode;
NODES remains a name; quoted nodes is a name and may include relationships.
Both graph reads receive the same normalized name. Exact label matching remains;
Peano Arithmetic is not an alias for Peano Arithmetic (PA). Empty quotes cannot
broaden into an unfiltered listing. Availability/cancellation/order/caps remain.

I: A public UI-neutral Friday Memory ingestion metadata builder owns the rule:
missing description (None) omits the description key; explicit empty/non-empty
strings are preserved. Chat calls that builder in its single and batch branches.
Source/type/chunk_index/chunk_count, controller metadata, protection, embedding,
chunking and promotion/grouping behavior remain unchanged. No broad ingestion
migration or generic metadata sanitizer; no existing-record rewrite.

## Exact allowlist

- packages/friday-commands/src/friday_commands/memory_queries.py: private name
  normalization helper and entities-handler use only; no exports/contracts/help.
- packages/friday-memory/src/friday_memory/ingestion/metadata.py (new): pure
  typed ingested-file base metadata builder; no Chat/Commands/TUI imports.
- packages/friday-chat/src/friday_chat/adapters.py: import the builder and replace
  only _ingest_document's two base-metadata constructions. Batch counters remain.
- New tests: friday-commands/tests_commands/test_memory_query_uat_repair.py,
  friday-memory/tests_memory/test_ingestion_metadata.py, and
  friday-chat/tests_chat/test_memq_uat_repair.py, under packages/.
- friday-commands/tests_commands/test_memory_queries.py: exactly the single
  quoted Ada Lovelace expected selection changes to its unquoted name. All other
  old test AST/assertions unchanged.
- friday-chat/tests_chat/test_command_memory_queries.py: only the frozen-case
  comparison permits the full entities:quoted row after exactly its two lookup
  event-name strings change; counts become67 exact/1 quote/2 kind/6 optionR.
  Baseline fixture bytes and every other field/order remain exact.
- Current packet README/authority/next-phase/tactical/execution-log; board and
  generated dashboard; this directive and exact approval; FU-009 only; new
  validation/memory-queries/uat-shared-repair/ evidence/probes/reviews/handoff.
  Preserve the dirty UAT plan and both YAML files exactly. The combined retest
  lives beside the existing UAT plan as uat/memq-repair-retest.md (new).

No other runtime/test path, dependency/lock/config, fuzzy lookup, uppercase alias,
command-wide tokenization, storage API, schema, maintenance diagnostic, quarantine,
ordering, budget, recovery or exception-policy change is authorized.

## Required criteria and checks

- QR-01: shared handler tests and real-graph registry dispatch prove quoted/
  unquoted names equal for Chuck and Peano Arithmetic (PA), both quote forms,
  internal apostrophes/Unicode/backslashes/parentheses; no missing-suffix match.
- QR-02: exact port/read events cover nodes/NODES/quoted nodes, malformed/empty/
  whitespace quotes and one-pair stripping, with unchanged parser/other-command
  behavior and failure/cancellation. Failed selections never list all nodes.
- IR-01: real FrameworkMemoryAdapter plus disposable Chroma, deterministic local
  embeddings, actual /ingest and /list-ingested prove absent descriptions work
  in single/multi branches. No user store/provider access.
- IR-02: exact absent/empty/non-empty metadata, chunk/protection fields, repeat
  counts and distinct listing groups in both branches. Pure metadata helper is
  usable headlessly without Chat/Commands/TUI; no duplicated policy in Chat.
- RR-01: immutable76-row fixture and complete exact changed-row accounting above;
  six existing query semantics otherwise retained. Only named old assertions may
  change. No broad skip, regenerated baseline or historical receipt rewrite.
- RR-02: unchanged mutation control passes. Removing quote normalization,
  reclassifying quoted nodes, or reintroducing description=None independently in
  either branch must fail named call-phase assertions. Setup/product exceptions
  alone earn no mutation credit; preserve failed attempts separately.
- RR-03: focused new tests; full Commands/cohort, controlled full Chat excluding
  live_lmstudio, CLI, relevant Memory ingestion and diagnostic regression tests.
  Explicit canonical origins at collection/finish/after; retained dirty-example
  baseline failures inspected separately, never converted to passing results.
  Changed-source Ruff/mypy, new-file format, pinned no-new-debt and affected-file
  baseline debt inventory; board/dashboard/docs/diff. Existing debt unwaived.
- RR-04: build3 affected wheels offline with pinned tools; private installed
  prefix, exact138 name/version closure, source/wheel members and origin checks.
  Fresh normal/-O installed real-graph/Chroma command checks and headless shared
  helper; repeat existing diagnostic installed probes. Historical full replay
  need not repeat; state precisely built/executed/inspected boundaries.
- RR-05: freeze one candidate, fresh-context independent read-only OpenAI review:
  named remediation delta first then full bounded interaction with current MEMQ
  and retained diagnostics. All writes/caches/temps/reports private external
  scratch; supplied evidence read-only; GIT_OPTIONAL_LOCKS=0 on every Git child;
  logical index before status at both boundaries and exact protected identities.
  Fresh reviewer cannot inherit builder conclusions or edit/delegate. At most2
  bounded low-risk correction cycles; escalate unresolved findings. After a
  usable VERIFIED result, publish one combined retest, keep human UAT/acceptance
  pending, and stop. No push/merge/release or automatic next-family work.

Reviewer/provider preference: no further Claude Opus council seats. Any future
council uses OpenAI GPT-6 Astra and GPT-6.1 Sol only, per maintainer direction.
This bounded unit requires a fresh independent validator under repository policy;
it does not automatically start a separate three-provider council workflow.

Stop for protected-input drift, missing offline inputs, unexplained regression,
or a repair needing another runtime path or semantic policy. Record commands,
module origins, metadata and installed artifacts honestly. No live UAT result or
acceptance is inferred from synthetic tests. Actual verification functional repair
remains dependent on the targeted diagnostic result.

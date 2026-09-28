# REM-005 Implementation Report

Date: 2026-09-28
Role: separate remediator `/root/mcp_ws03_rem005`; did not build or review VAL-008's candidate; no inherited parent session
Status: implementation candidate for fresh independent VAL-009; no self-verification or acceptance
Branch: `feature/friday-mcp-ws03-registry`
Stable approval/start baseline: `215e54de71eda08067d22695d0062f7bed35e9d0`
Original reviewed candidate: `397caa9898612cd989f6404951b3e1f5005dfac2`
WS-03 work-unit base: `2c0d6bd1fe481fff9bb180f9e6dfb4a9a2131641`
WS-03 approval/start revision: `b54069654bb3e21a6265fbabcd23f6991e286ab0`
Accepted predecessor: `a257f041d1d68f8aea2f5b9773df1b88acd82379`
Authority: [approved REM-005](../remediation/REM-005-directive.md), [WS-03 directive](../directives/ws-03-tool-naming-metadata-registry.md), repository engineering/development-lifecycle/independent-validation policies, build/tactical plans, complete [VAL-008 report](../validation/VAL-008-report.md) and [evidence](../validation/VAL-008-evidence.yaml).
Maintainer approval: "That's approved. Proceed." after the complete directive/separate-remediator request.

Approved REM-005 SHA-256 at baseline: `5bff5b4b043d504384219d85af958bfffc4da584e057d910d35da3cb0a4c3ecb`.
WS-03 directive SHA-256: `c723e899d0916012dc324836f8c2882d5c2362a40825cec377e19182f1749efd`.
The controller pins the new candidate/delta and authority manifest after this
scoped local commit; a candidate hash cannot refer to its own report content.
All 33 archived VAL-008 artifacts matched their exact compressed/original
hashes before implementation. Historical independent report/evidence are unchanged.

## Exact Eight-Path Manifest

1. `packages/friday-runtime/src/friday_runtime/mcp_registration.py`: additive frozen diagnostic types and bounded first/second collision source preflight.
2. `packages/friday-runtime/src/friday_runtime/mcp_loading.py`: public lifetime documentation and new-attempt diagnostic replacement.
3. `packages/friday-runtime/tests_runtime/test_mcp_registration.py`: provider/source distinction, cross-peer ambiguity, pre-filter controls, hostile original summaries, compatible decision defaults, unchanged admission bounds.
4. `packages/friday-runtime/tests_runtime/test_mcp_loading.py`: retained history/counters/native identity, repeated public stop, obstructed cleanup and subsequent discovery/registration replacement.
5. `tests/integration/test_mcp_registry.py`: production public-kernel collision/privacy/native identity and resource/retry regressions.
6. `tests/integration/mcp_fake_server.py`: four bounded collision catalog variants only; all existing noisy/lifecycle modes unchanged.
7. `docs/planning/active/friday-mcp/execution/REM-005-implementation-report.md`: this report.
8. `docs/planning/active/friday-mcp/execution/WS-03-implementation-report.md`: bounded API/criterion/history/remaining-gate correction.

No other product/test/config/authority/controller edits. Native mandatory
protocols, registry implementation, accepted normalizer, security/schema
sanitizer, adapter, DI/kernel/tool-loader, manager/transports, dependencies and
production budgets remain unchanged. No broad ignores or private cross-package
reach-through were added. Registration still uses public native list/get/register/
unregister contracts; native source identity needs only the canonical name.

## Public Additive Contract And Compatibility

Import from public `friday_runtime.mcp_registration`:

- `MCPOriginalNameSummary(length: str, shape: str, fingerprint: str)`.
- `MCPCollisionSource(provider: Literal["mcp", "native"], server_id: str | None = None, original_name_summary: MCPOriginalNameSummary | None = None)`.
- `MCPNameCollision(canonical_name: str, first: MCPCollisionSource, second: MCPCollisionSource)`.
- Existing `MCPRegistrationDecision` gains final field `collision: MCPNameCollision | None = None`.

All new values are frozen dataclasses. Explicit constructor checks enforce
summary string bounds, safe configured server shape, source-kind consistency
and canonical name bounds using static exceptions. Existing three/four-position
and keyword decision constructors remain valid, with unchanged ordinary
reason/code values and `MCPBindingContext.reason_for`. Successful decisions
have collision=None. Standard dataclass serialization now has an optional
nested field; strict older consumers need to allow it. No persistence format
or stored diagnostic migration is implemented, and no native required member
or public runtime/transport signature changes.

The shared canonical name (accepted ASCII grammar, at most 64 characters)
identifies the collision and native registry entry. Each MCP contender carries
its safe configured server ID (at most 64 characters), never peer-reported server
metadata. Native has explicit provider `native`, server_id=None and no original
summary. First is the already-present native entry or first discovered MCP
contender; second is the current discovered MCP contender. Only the first fatal
collision is recorded, without enumerating/backfilling the rest of the catalog.

Exact original summary representation:

| Field | Bound and meaning |
| --- | --- |
| length | Decimal Unicode character count 0..9999, then fixed `9999+`; at most 5 characters. |
| shape | First at most 24 characters only: ASCII alphabetic -> `a`, ASCII digit -> `0`, punctuation `-_.` preserved, everything else -> `?`. No source letters, controls, encoded text or raw original retained. |
| fingerprint | First 12 lowercase hexadecimal characters of SHA-256 over the complete original UTF-8 bytes using surrogatepass for JSON-escaped lone surrogates, not only its shape/prefix. |

Fingerprint generation occurs only after unchanged full handoff byte/JSON and
accepted normalization checks. This adds one bounded scan within the existing
configured input cap, no arbitrary/unbounded catalog scan and no weaker admission.
Over-256/control originals can be eligible for fatal preflight but still fail
the unchanged sanitizer if there is no collision. Over-byte-cap handoffs still
reject before summaries. Tested originals include 20,009 characters, encoded
`&#83;`, NUL and zero-width variants. Complete two-source decision repr remains
under 1000 characters in these probes; size follows fixed fields regardless of
original length. Fingerprints are diagnostic correlation, not secrecy,
cryptographic uniqueness or protection against offline guessing. Canonical
names/configured safe IDs are intentionally visible as before. No peer catalog,
exception detail, argument, environment value or raw original is copied to the
new public surface, exception text, repr or DEBUG logs.

## Exact Before/After And Retention

VAL-008's public runtime peer/peer and MCP/native probes both returned:

```text
MCP registration failed (name_collision); inspect mcp_provider.registration_decisions
(MCPRegistrationDecision(canonical_name='mcp_peer_read_file', server_id='peer', reason='rejected', code='name_collision'),)
```

Current error text is byte-identical. Current last rejected decision additionally
has `collision=MCPNameCollision(canonical_name='mcp_peer_read_file', first=..., second=...)`:

| Case | first | second |
| --- | --- | --- |
| Same optional peer, Read.File / Read-File | provider=mcp; server_id=peer; summary length=9, shape=aaaa.aaaa, fingerprint=965778ac841a | provider=mcp; server_id=peer; summary length=9, shape=aaaa-aaaa, fingerprint=ae6cb96ad30d |
| Native mcp_peer_read_file / optional MCP Read.File | provider=native; server_id=None; original_name_summary=None | provider=mcp; server_id=peer; summary length=9, shape=aaaa.aaaa, fingerprint=965778ac841a |

The two variants are now observably different without raw originals in returned
values. Cross-peer ambiguity also preserves IDs `peer_one` / `peer` and distinct
summaries for Read.File / one.Read-File (shared mcp_peer_one_read_file). Strict
config still rejects two server IDs with equal normalized server names earlier;
that config rule was neither bypassed nor altered.

Inspect after failed `RuntimeKernel.start()` using
`kernel.mcp_provider.registration_decisions[-1].collision`. Successful failure
cleanup and subsequent stops preserve the immutable tuple/record while clearing
prepared data, registry ownership/metadata and connected clients. No-op start
and repeated stop do not erase it. Obstructed prior cleanup retains history and
the same owner. A new discovery attempt clears registration history only after
prior-owner cleanup and workspace validation; a later registration result
replaces it, including success/non-collision results. A new optional discovery
failure therefore does not misreport a prior collision. Previously held frozen
snapshots remain valid history. This is in-memory last-attempt evidence, not a
persistent audit log or a background refresh capability.

Collision remains fatal before sanitation/filtering/insertion, regardless of
optional peers, default zero selection, explicit includes and name/category
exclusions. No registry overwrite, MCP insertion, rediscovery or suffix repair.
Fatal counters retain the existing meaning: same-peer discovered=2/rejected=1;
native discovered=1/rejected=1; selected/filtered/registered=0. Rejected counts
reached rejected/capped decisions, not both source descriptors or every later
catalog entry. Ordinary count regression remains four discovered, two rejected
(one discovery plus one registration), one filtered and one selected/registered.

## Six-Criterion Evidence Map

| Criterion | Implementation and local check evidence |
| --- | --- |
| REM-005-AC-01 | Unit same-peer summary/hash/shape and cross-peer unique-server concatenation ambiguity; real public same-peer and cross-peer kernels retain both descriptors after cleanup. |
| REM-005-AC-02 | Unit and public native source explicit/no MCP ID; both collision variants abort pre-insertion, native objects retain exact identities; public decisions distinguish provider kinds. |
| REM-005-AC-03 | Unit four filter states and public eight peer/native filter variants, optional/default-zero/selected/includes/exclusions; repeated failed public starts/stops, provider obstructed-cleanup retention and later discovery failure/success replacement. |
| REM-005-AC-04 | Exact enforced summary bounds; unit oversized/encoded/NUL/zero-width/escaped lone-surrogate names and handoff-cap rejection; real 20k/control/encoded catalogs with sentinel catalog/args/env/stderr, error/repr/DEBUG privacy, unchanged >256/control sanitizer limits. |
| REM-005-AC-05 | Old decision constructor/default/binding reasons, unchanged fatal counters and ordinary-count test; complete accepted contract/adapter/native registry/core/MCP/runtime/lifecycle suites preserve caps, exact routing/sidecars, insertion/rollback refusal, retained owner, noisy and cancellation regressions. |
| REM-005-AC-06 | Exact eight-path scoped delta, required Ruff and meaningful unfiltered Python 3.13 typing; explicit public contract/migration/lifetime/counter notes and all exact commands/baselines below; no authority/protocol/config/dependency/manager/transport edit. |

These are remediator implementation/check observations for independent review,
not PASS/VERIFIED rulings. Full ten-criterion WS-03 mapping remains in the amended
WS-03 report; independent VAL-009 must evaluate every criterion afresh.

## Public Cleanup Versus Defensive Settlement

New production public-kernel probes use real stdio clients/managers/transports
and native registry, with unrelated LLM/storage/telemetry factories stubbed.
Before defensive cleanup they assert: provider reachable; no prepared tools,
metadata, owned names or registry owner; manager has no connected servers;
every tracked child has returncode, stdout/stderr EOF and closing stdin; no new
live task; every native object is unchanged. Repeated stops retain evidence.

Each new asynchronous test uses finally to call public stop and settle synthetic
tasks; the existing tracked-transport/process fixture then defensively disconnects,
kills if necessary, drains both pipes in bounded 4096-byte reads and reaps every
child, including assertion failures. Unit doubles likewise release failure/
pause controls and disconnect in finally/fixture cleanup. These defensive steps
cannot satisfy earlier public cleanup assertions. No caller pipe intervention
or saved private client reference was needed for successful public assertions.
Unchanged production cleanup budgets and existing 13-second fixture bound remain;
no new shutdown SLA, process-tree sandbox or cancellation-resistant I/O claim.

## Exact Required Commands And Results

Every required command was independently run by this remediator, not adopted
from earlier builder/reviewer claims. T means the exact test prefix `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache`. Exact logs/exit/timing JSON are under
`/private/tmp/rem005-checks`. The first full run precedes three strengthened
raw-original DEBUG assertions and this report; it is retained unchanged under
`first-run/`. The subsequent privacy-assertion run is retained under `privacy-run/`. Final review also added one escaped lone-surrogate pure-preflight regression and deterministic surrogatepass hashing, avoiding a diagnostic encoding exception while preserving ordinary invalid-schema rejection. The final run uses the same exact commands after those final edits.
Required failures remain failures, without repair or waiver. Passing overlapping
test counts are not additive.

| # | Exact command/environment | Exit | Result |
| --- | --- | --- | --- |
| 1 | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run pytest packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp/tests_mcp/client/test_adapter.py packages/friday-runtime/tests_runtime/test_mcp_registration.py packages/friday-agent/tests_agent/test_registry.py tests/integration/test_mcp_registry.py -q` | 0 | 173 passed |
| 2 | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime packages/friday-agent/tests_agent/test_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/test_mcp_registry.py -q` | 0 | 459 passed |
| 3 | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run pytest packages/friday-tools/tests_tools -q` | 1 | 233 passed; 2 declared native invalid-zip failures; 1 unrelated warning |
| 4 | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run pytest packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py -q` | 0 | 46 passed |
| 5 | `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run pytest tests/integration -q --tb=short` | 1 | 69 passed; 1 declared board-count failure |
| 6 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run ruff check packages/friday-core/src/friday_core/mcp.py packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp packages/friday-runtime tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | 0 | All checks passed |
| 7 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run mypy packages/friday-core packages/friday-runtime packages/friday-mcp` | 2 | Installed NumPy default-target syntax baseline; project checking prevented |
| 8 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py` | 1 | Only four unchanged profiles.py no-any-return errors; 1 root file |
| 9 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run mypy --python-version 3.13 packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | 0 | No issues in 45 source files |
| 10 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py` | 1 | Only the same four profiles.py errors; 46 root files |
| 11 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run python scripts/friday-dev-board.py validate` | 0 | Board validates; 23 tasks |
| 12 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run python scripts/friday-dev-board.py render --check` | 0 | Dashboard current |
| 13 | `UV_CACHE_DIR=/private/tmp/friday-uv-cache uv run python scripts/check-documentation-lifecycle.py` | 0 | 342 Markdown files including this report |
| 14 | `git diff --check` | 0 | No whitespace errors |

Final fourteen-command run after the final source/tests and report additions: focused **173 passed** (5.85s pytest), aggregate **459 passed** (52.19s), Chat **46 passed** (1.43s), integration **69 passed / same board failure** (49.98s), tools **233 passed / same two failures** (11.80s); Ruff, 45-file typing and controller checks pass. No touched-file failure remains in these commands. All exact wall timings and logs are in `results.json`; final check #13 includes 342 Markdown files.

- Check 01: exit 0; wall 7.792s; `/private/tmp/rem005-checks/01.log`.
- Check 02: exit 0; wall 54.72s; `/private/tmp/rem005-checks/02.log`.
- Check 03: exit 1; wall 12.691s; `/private/tmp/rem005-checks/03.log`.
- Check 04: exit 0; wall 2.213s; `/private/tmp/rem005-checks/04.log`.
- Check 05: exit 1; wall 51.017s; `/private/tmp/rem005-checks/05.log`.
- Check 06: exit 0; wall 0.039s; `/private/tmp/rem005-checks/06.log`.
- Check 07: exit 2; wall 0.201s; `/private/tmp/rem005-checks/07.log`.
- Check 08: exit 1; wall 0.182s; `/private/tmp/rem005-checks/08.log`.
- Check 09: exit 0; wall 0.749s; `/private/tmp/rem005-checks/09.log`.
- Check 10: exit 1; wall 0.778s; `/private/tmp/rem005-checks/10.log`.
- Check 11: exit 0; wall 0.074s; `/private/tmp/rem005-checks/11.log`.
- Check 12: exit 0; wall 0.073s; `/private/tmp/rem005-checks/12.log`.
- Check 13: exit 0; wall 0.215s; `/private/tmp/rem005-checks/13.log`.
- Check 14: exit 0; wall 0.009s; `/private/tmp/rem005-checks/14.log`.

Only report closeout text changes after this run. Board/render/docs/whitespace are rerun after that text; exact committed delta/aggregate and product-stability checks are performed after freeze and handed to the controller.

## Declared Baselines And Independent Reproduction

Exact unchanged failures in the prescribed environment:

```text
.venv/lib/python3.13/site-packages/numpy/__init__.pyi:737: Type statement is only supported in Python 3.12 and greater [syntax]
packages/friday-core/src/friday_core/profiles.py:77: Returning Any from function declared to return "VectorStoreAdapter" [no-any-return]
packages/friday-core/src/friday_core/profiles.py:82: Returning Any from function declared to return "VectorStoreAdapter" [no-any-return]
packages/friday-core/src/friday_core/profiles.py:110: Returning Any from function declared to return "GraphStoreAdapter" [no-any-return]
packages/friday-core/src/friday_core/profiles.py:115: Returning Any from function declared to return "GraphStoreAdapter" [no-any-return]
tests/integration/test_development_board.py:75: assert "22 tasks" in "Development board validation passed: 23 tasks"
packages/friday-tools/tests_tools/test_filesystem_readers.py:286: test_docx_reader_missing_dependency rejects "Failed to read DOCX: File is not a zip file"
packages/friday-tools/tests_tools/test_filesystem_readers.py:306: test_xlsx_reader_missing_dependency rejects "Failed to read Excel file: File is not a zip file"
```

The default target remains Python 3.10; the NumPy failure prevents project
checking and cannot establish source correctness. Unfiltered required #9 gives
meaningful affected-scope typing (45 files). Core-including #8/#10 preserve the
four unrelated profiles errors; no changed-file error is classified as legacy.

Independently extracted accepted predecessor via exact command
`git archive a257f041d1d68f8aea2f5b9773df1b88acd82379 packages tests scripts docs pyproject.toml AGENTS.md`,
then `tar -x -C /private/tmp/rem005-predecessor`. Cwd for baseline commands is
that read-only archive, environment T plus PYTHONPATH equal to ordered sorted
`/private/tmp/rem005-predecessor/packages/*/src` paths. No installed import/dependency
change is substituted for the required checks.

- `/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -m pytest packages/friday-tools/tests_tools -q`: exit 1, 233 passed / the same two invalid-zip failures / one warning; 12.59s pytest, 13.538s wall; `baseline-3.log` proves archived memory source loaded.
- `/Users/chuckrussell/Dev/gendev/agent-framework/.venv/bin/python -m pytest tests/integration/test_development_board.py -q --tb=short`: exit 1, 10 passed / the same board-count failure; 1.85s pytest, 2.142s wall; `baseline-4.log`.
- `git diff --exit-code a257f041d1d68f8aea2f5b9773df1b88acd82379 -- packages/friday-tools packages/friday-core/src/friday_core/profiles.py tests/integration/test_development_board.py pyproject.toml uv.lock`: exit 0. Baseline source/tests/typing/dependencies are unchanged.

VAL-008's exact archived predecessor typing outputs independently establish the
NumPy/profiles baselines and their hashes were reconfirmed. No source repair,
waiver, dependency/import masking or favorable review result is promised here.

Initial focused command `T uv run pytest packages/friday-runtime/tests_runtime/test_mcp_registration.py packages/friday-runtime/tests_runtime/test_mcp_loading.py -q`
returned 106 passed / one test-setup failure (7.79s): strict config rejected two
server IDs normalizing identically. Corrected the cross-peer probe to distinct
server IDs with server/tool concatenation ambiguity. Then the combined command
adding `tests/integration/test_mcp_registry.py` returned 132 passed (13.35s).
Initial supplemental baseline commands mistakenly resolved the venv interpreter
symlink to base Python, which lacked pytest; both exit 1 (`No module named pytest`)
are retained as `baseline-1.log`/`baseline-2.log` and `baseline-results.json`,
not treated as product failures or baseline proof. Corrected exact venv commands
above supplied reproducible baseline results. All probe resources were settled.

## Preservation, Freeze And Remaining Gates

Unrelated state is preserved and excluded from explicit staging: modified
`.DS_Store`; deleted `family-tree.md`; untracked `docker-bench-security/`,
`packages/friday-chat/config.example.yaml.pre-typed-llm-20260828.bak`,
`packages/friday-sandbox/docker/Dockerfile.audit`. Start byte fingerprints are
`/private/tmp/rem005-preserved-start.json`; identical closeout fingerprints are `/private/tmp/rem005-preserved-closeout.json`. All twenty pinned original authority hashes, both approved directive hashes, the unchanged historical report and every archived evidence hash still match. Exact working source/test/report boundary contains only the eight allowed paths plus the preserved unrelated manifest. Equivalent precommit delta/aggregate whitespace checks and postcommit freeze evidence are handed to the controller. No cleanup, broad staging, controller board/index/log/queue/request/
evidence mutation, delegation, provider/network/live MCP/credential activity,
external effect, push/merge/release/deployment occurred.

Controller must freeze the candidate/authority request, mark VAL-008 superseded
for current decisions separately while retaining its original report/evidence,
and dispatch fresh read-only VAL-009 for REM-005 delta plus complete WS-03
aggregate review. This remediator cannot self-validate or dispatch a validator.
Only independent VERIFIED permits proposed closeout; maintainer WS-03 acceptance,
later workstream approval, whole-feature aggregate, live UAT and delivery remain
separate gates. Initiative remains started/granted/local.

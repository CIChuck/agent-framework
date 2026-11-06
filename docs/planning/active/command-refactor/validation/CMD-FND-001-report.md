# CMD-FND-001 — neutral foundation implementation report

Date: 2026-11-06
Status: implementation and builder checks complete; fresh independent review pending
Execution phase: validation
Validation state: in_review
Initiative: friday-command-refactor

## Authority and frozen starting identity

Chuck Russell approved CMD-DESIGN-001, then RD-01 and CD-CMD-FND-001.
The [human record](../approval/foundation-readiness.md) and
[authority](../authority.json) bind those exact decisions.

- Approved execution/source baseline: `d003c4db31cc9b1e3d143fd8c0d8b930db50ab30`.
- Actual builder starting HEAD: `1b4756b7bd5bc7fb9ec84c45550ec6cdf0389688`.
- The nine intervening paths were approval/evidence/status records only; product
  bytes and the exact approved API/directive were independently compared to
  the approved source baseline before construction.
- Approved directive SHA-256: `cf61cab1bc18af071b4b2b9a98f335cf1685592ee647d3c80f60493a80598806`.
- Approved API SHA-256: `e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74`.
- Branch remains `feature/command-refactor`; task started/granted, delivery local.
- Candidate full SHA and exact implementation/approved-base diffs are supplied
  by the controller's frozen validation request. This report is builder evidence,
  not an independent VERIFIED result or maintainer acceptance.

## Implemented scope

Created the dependency-free `friday-framework-commands` package (`friday_commands`)
with frozen validated models, closed foundation data/errors/UI effects, a typed
handler protocol and an injected-handler registry. Registration validates and
copies a complete candidate, then publishes one replacement mapping so failed
canonical/alias additions cannot partially mutate state. Public views are
immutable; resolved/dispatched specs share canonical identity. Text parsing
uses the approved one-pass normalization and whitespace grammar. Dispatch calls
and awaits a single injected handler, propagating exceptions/cancellation.

The package ships no default handlers, executable, frontend/domain imports or runtime
requirements. No client handler, parser, routing, renderer or lifecycle changed.
All current Chat commands, including future retirements, remain in Chat.

Minimal integration adds the new package to root `all`/workspace sources, the
18-project cohort, artifact inventory/guards and package lists. No existing
member gains a dependency on this foundation. The lock contains only the new
member/package and root `all` references; prior package resolutions and options
are semantically identical under the directive's exact comparison.

## API-01–API-06 evidence

| Criterion | Builder evidence |
| --- | --- |
| API-01 neutral closure | Source AST audit and fresh import guard permit only stdlib; built wheel Python equals all three source modules. Fresh no-deps venv contains only this Friday distribution; blocked other-Friday imports, no requirements/entry points, typed marker and isolated synthetic dispatch pass. |
| API-02 registry integrity | Canonical copying/trimming, raw argument/detail preservation, normalized collisions/blank rejection, full public-state preservation after failures, sorted specs, immutable old snapshots and request/spec identity tested. Single-map publication follows complete validation. |
| API-03 grammar | Independent frozen help/read fixtures cover ordinary/leading-space text, bare slash, uppercase, aliases, quotes, multi-slash and normalization order, with expected key/args/handler counts. Unusual nonempty slash keys remain valid. Required/choice/default argument policy stays with handlers. |
| API-04 typed models | Every constructor row has positive/negative scalar, bool/int, container/member, exact-model, code/effect and cross-field cases. Finite iterables, sequence protocol, copy/freeze/order/duplicates and iterator exception identity tested. Opaque/model-subclass data refused using actual type identity. Optimized Python keeps runtime checks. No source asserts, Any, casts or suppressions added. |
| API-05 one execution | Recording coroutine/custom-awaitable handlers invoked/awaited once; wrong result/nonawaitable returns TypeError, exceptions and external cancellation propagate without retry. UI/exit intents are returned only. |
| API-06 no early migration | All 84 inventoried client/source-test hashes match; guarded Chat capture matches frozen metadata after canonical JSON conversion: 50 names/three aliases, zero metadata drift. New registry has no defaults. Existing client source and all unrelated protected inputs remain unchanged. |

New tests are only `tests_commands/test_contracts.py`, `test_registry.py` and
`test_import_boundary.py`. Existing cohort tests gain package/complete-inventory
checks; the artifact checker gains only new-package guards. Its old checks remain.

## Actual verification

All scoped checks use the directive's frozen/no-sync editable overlay; its import
origin/version check passes before pytest. Python uses -B or
PYTHONDONTWRITEBYTECODE; test cache is disabled and application network is guarded.
Mypy cache is placed in the task scratch directory for the final run. The pre-existing default client version snapshot is frozen in approved base d003c4db (required-finance/installed.json); actual overlay/tool versions and installed metadata are additionally captured in validation-environment.json and tool-versions.json. No repository-venv sync was performed. Only the
named public PyPI/artifact hosts were permitted for package-manager resolution/
builds; no application provider/tool network access was enabled.

| Actual check | Result |
| --- | --- |
| Explicit `uv lock --default-index https://pypi.org/simple --no-python-downloads` | PASS: 214 records including the one new local member. |
| Approved embedded parsed-lock comparison plus offline `uv lock --check` | PASS: only new member/package and two root `all` references; no unrelated resolution change. |
| Editable package import/version/origin | PASS, current new-package source and version 0.1.0a4. |
| New package + cohort pytest | PASS: 145 tests. |
| Selected Chat registry/foundation suites | PASS: 19 tests. Full 826-count historical suite not rerun. |
| Framework CLI owning suite | PASS: 155 tests, matching its baseline. |
| Focused Ruff, format and mypy | PASS: eight files formatted; four source files typed without issues. |
| Package metadata | PASS: 18 projects. |
| Current foundation wheel/sdist artifact validation | PASS: one wheel and one sdist. |
| Isolated fresh no-deps install and exact approved smoke fixture | PASS outside checkout with -I -B, frontend/domain imports blocked, synthetic canonical/alias/unknown/plain dispatch. |
| Disposable malformed artifacts | PASS/refused: missing py.typed, injected Requires-Dist and injected entry_points each produce the expected targeted rejection. |
| Guarded Chat metadata capture | PASS: 50 names/three aliases; zero drift versus frozen baseline after JSON tuple/array normalization. |
| Board, lock consistency, whitespace | PASS; 36 tasks; no unrelated task transition. |

## Broad baselines and limits

Full `ruff check .` exits 1 with 534 findings in 13 pre-existing files. Every
finding's source bytes match the approved baseline (or pre-existing protected
input), and Ruff configuration is unchanged. No new/changed foundation or
integration file has a Ruff finding. The proof includes per-file hashes.

The required root pytest attempt exits 2 at the existing Chat/CLI duplicate
`test_display.py` import mismatch. No tests were omitted or renamed to force a
root pass. Narrow suites above pass and the new package is installed before the
root attempt. Documentation lifecycle exits 1 with exactly the four unrelated
TUI links: N01B-04:37, N01B-05:49, N01B-06:37 and VAL-N01B-07-prepush-a196e95a:35.
These are baseline limits, not passing broad gates or implicit policy waivers.

Initial metadata comparison used runtime tuples against JSON arrays; the capture
was corrected to canonical JSON value comparison without modifying client code.
No full owning Chat suite, provider/tool execution, runtime/store construction,
physical terminal/audio or Linux/Windows acceptance was performed. Existing
packaging repairs remain independent earlier units. Full family/P0/P1, API-07–09,
future migration/retirement, aggregate review and feature acceptance stay open.

## Artifact and receipt identity

- Wheel: `friday_framework_commands-0.1.0a4-py3-none-any.whl` SHA-256 `3d5d112ba05c0374a85c8263ac083290c0a48c8950ca2596648443e53b9a1cc8`.
- Sdist: `friday_framework_commands-0.1.0a4.tar.gz` SHA-256 `3b68bae965eba0432165abfde639db79aca1645574ad41f2b564ed0c1a4eadf5`.
- Exact approved smoke fixture SHA-256 `0a7ee690bf9f3b15da21d6ee4a6facc699729b72c4881dbb7c7f8084d5973af9`.
- Task scratch: `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/friday-command-foundation-nds1ov46`.
- Tool versions: uv 0.11.3 (Homebrew 2026-04-01 aarch64-apple-darwin); ruff 0.14.10; mypy 1.19.1 (compiled: yes). Python 3.13.10 on the recorded macOS environment.
- Raw check argv/exits: `core-results.json`, `chat-results.json`,
  `cli-results.json`, `broad-results.json`, `chat-metadata-command.json`.
- Packaging argv/artifact hashes/refusals: `packaging-results.json`.
- Lock proof/generation: `lock-semantic-proof.log`, `lock-generation.log`.
- Broad lint preservation: `ruff-baseline-proof.json`; all raw logs remain
  separate in that scratch directory for independent review.
- Protected manifest: `protected.json`, 16876 files,
  independently checked unchanged after implementation/checks. Its exact digest
  and all deliverables/authority pins are bound by the validation request.

No push, PR, merge, release, deployment, client wiring, later unit execution or
maintainer acceptance follows. Stop at a frozen implementation candidate for
fresh independent validation of this exact directive and API-01–API-06.

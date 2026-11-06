# Step 3 — foundation readiness review

Date: 2026-11-06
Status: COUNCIL REVIEW CANDIDATE — Step 4 approval pending
Scope: CMD-FND-001, API-01–API-06 only

This is the maintainer's single readiness summary. The
[next-phase checkpoint](next-phase.md) remains the main handoff. CMD-DESIGN-001
is approved, but product construction and the proposed prerequisite amendment
below are not. The requested Claude Opus / OpenAI Sol / Google Gemini council
will assess this frozen packet read-only before the Step 4 decision.

## Recommendation and decision boundary

Present the standard-library-only foundation for **conditional Step 4 approval**.
It creates types and a registry for synthetic injected handlers. It ships no
default handlers, migrates no PAR case, removes no name, wires no client and
does not change existing product source, tests or configuration.

The ordinary full P1 gate is not closed. Before foundation construction, the
maintainer must explicitly approve RD-01 in addition to the exact construction
directive. Without that amendment, the full existing P0/P1 entry conditions
continue to block construction. No current or later gate is silently waived.

| ID | Step 4 decision/disposition | Proposed treatment |
| --- | --- | --- |
| RD-01 | Permit a foundation-only unit before full family-contract/P1 closure. | Defer per-command all-class behavioral signoff, final family schemas/service relocation, host progress/cancellation, installed-client acceptance and final scenario/platform approval until before their affected migration directives. Do not defer any API-01–API-06 test, neutral-import proof, standalone foundation wheel proof or independent review for FND-001. No frontend/domain dependency, handler or compatibility shim may enter FND-001. |
| RD-02 | Disposition observed client packaging/entry-point limits for this isolated unit. | Record the failing default installation and generic CLI entry point as baseline defects, not passes. They do not require modifying clients to build a zero-dependency foundation with no client wiring. Before any affected client migration/delivery gate, repair through separate authorized work or obtain its explicit required disposition. This decision cannot qualify existing clients as installable or the refactor as accepted. |
| RD-03 | Review the proposed unit/order map as planning input. | Every baseline name and alias now has a proposed owner. Foundation first, separate retirement next, then a help/exit/cls pilot and dependency-ordered families. Only FND-001 is being prepared for construction; no future unit, retirement timing implementation or capability schema is approved by this map. |

## Evidence resolved in Step 3

- **Source identity:** all 84 source/test hashes in the historical inventory
  match the current checkout. The existing controlled 826-test Chat and
  155-test CLI receipts remain historical local evidence; those complete suites
  were not rerun. No new whole-suite or all-class PAR claim is made.
- **Packaging:** all 17 existing workspace wheels build offline from source
  baseline `bbbd90e05143137c5a1d49eacedb4125d254b8fb`. Wheel hashes and declared
  requirements are recorded in [the receipt](validation/step3/receipt.json).
- **Default install:** a new environment installed Chat/CLI and their declared
  dependencies (127 distributions), and dependency checking passed. Importing
  Chat failed with missing `friday_finance`: `friday_tools.__init__` imports
  finance unconditionally while finance is declared as an optional extra.
  Sandbox is also imported unconditionally; its default-profile failure was
  not reached independently in this first failing probe.
- **Augmented diagnostic install:** adding Chat's finance+sandbox extras yielded
  131 distributions. From outside the checkout, isolated Python loaded all
  checked Friday modules from the disposable environment. Installed metadata
  exactly matches the frozen 50 names/three aliases. Seven parser fixtures,
  plain/leading-space/unknown/help/exit/clear dispatch, generic quoted aliases
  and sync/async dispatch passed. Chat's declared Typer entry point loads and
  `--help` exits zero. This is not a default-install, full runtime or terminal-UAT
  pass. See [observations](validation/step3/installed-probe.json).
- **Generic CLI limitation:** its wheel declares `friday_cli.main:app`, but
  loading that entry point raises AttributeError because `app` is absent. Its
  registry imports and synthetic dispatch work in the augmented environment.
- **Containment:** probes used no runtime/store construction or live tool/model
  execution. The augmented probe recorded one LiteLLM cost-map download attempt;
  the socket guard blocked it and the library used its local backup. No request succeeded.
- **Environment limit:** attempting to install the entire 17-wheel cohort
  offline could not resolve optimization's dspy dependencies from the local
  cache. This is an offline-cache limitation, not evidence of a new product
  dependency conflict. The targeted augmented profile installed successfully.

The reproducible probe is [installed_probe.py](validation/step3/installed_probe.py).
Raw install/probe logs and exact dependency versions are supporting evidence;
the maintainer need not read them to make the scoped decision.

## Generic CLI reuse assessment

Keep the generic CLI registry/API separate as O-03 requires. Source
`friday_cli/commands.py` exposes decorators/programmatic registration,
mutable generic argument defaults, quote-preserving parsing, kwargs binding,
sync/async handlers and `(handled, str|None)` results with caught errors.
Chat uses whitespace fragments, explicit command metadata, async typed handlers
and UI/exit outcomes. The approved foundation adds strict immutable typed
metadata and exception propagation. Replacing either current parser/registry
with the other would change its contract. No proven compatible primitive with
a concrete benefit is selected for this unit; no adapter is forced into scope.
Chat's existing CLI display dependency is separate and remains unchanged.

This assessment is corroborated by the source exports, existing
`tests_cli/test_commands.py`, historical owning-suite receipt and new installed
sync/async/quoted-alias observations. It is not a claim about unknown external
consumers or a repair of the generic executable.

## Unit, ownership and scenario map

[unit-map.json](validation/step3/unit-map.json) assigns all 50 PAR cases and
three aliases exactly once, with source handlers, names/aliases, proposed
units, domain ownership constraints and explicit pending behavioral signoff.
Candidate test-node matches remain navigation aids, not assertion proof.

| Proposed unit | Names / purpose | Entry dependency |
| --- | --- | --- |
| FND-001 | Neutral contracts/registry only; no migrated cases. Preserve 50/3. | Step 4 directive + RD-01/RD-02 disposition + required review. |
| RET-001 | Nine selected removals, directly from current Chat; no migrate-then-delete. | FND-001; own approved directive, orphan-state/metric and negative-effect treatment. |
| PILOT-001 | help, exit, cls; includes quit/q/clearscreen aliases. | Retirement disposition/order; reviewed catalog ownership and host routing/rendering design. |
| SESSION-001 / DIAG-001 | history/clear and context/prompt/debug/budget/timing views. | Pilot and typed snapshot/session capabilities. |
| MEMQ-001 / FILE-001 | Memory/graph/ingested-source queries, read and ingest. | Public query/reader/ingestion contracts and exact error/effect fixtures. |
| MAINT-001 | reset, compact, lifecycle, migrate, reorganize. | Session/query capabilities; admission, stage/failure/cancellation/progress and recovery contracts. |
| TRANSCRIPT-001 / REPLAY-001 | sessions/transcript/export/export-prompts and replay. | Session identity/query/export contracts; replay also depends on maintenance/admission. |
| TOOLS-001 | tools, including aggregate inventory and MCP diagnostics. | Retirement/pilot; neutral inventory seam. |
| ORCH-001 / SEC-001 / SPEECH-001 | Agent orchestration, security and speech families. | Pilot and separately reviewed family contracts. |
| WORKFLOW-001 | workflow. | Orchestration/security and actual workflow approval authority. |

The map also defines eight future cross-family scenario obligations: memory and
maintenance; transcript/export/replay; tool/security/retirement; orchestration
and workflow; read/ingestion; speech/diagnostics; host help/clear/exit; and generic
CLI preservation. They have owners and dependencies, not new passing receipts.

## Environments and remaining gates

Current readiness observations are macOS arm64/Python 3.13.10; package metadata
requires Python >=3.13.4. Foundation construction must prove its own runtime
checks, neutral imports, zero-runtime-dependency wheel and isolated synthetic
dispatch on this recorded local environment. Linux/Windows and full installed
client/physical-terminal/audio evidence are not claimed; affected later units
must freeze their supported-environment obligations before construction.

The complete per-case effect/cancellation/error map, final family APIs and
service relocation are still open. No broad P0/P1 completion follows from this
assessment or CMD-DESIGN-001. Any security/contract violation found before a
family migration must receive its required mitigation/disposition first.

## Construction handoff for review

The [updated draft CD-CMD-FND-001](directives/CD-CMD-FND-001-neutral-foundation.md)
binds the unchanged approved API hash, the proposed RD-01/RD-02 amendment,
allowed paths, test/import/install proof and stop conditions. Its new-package
test command explicitly installs the package under test in an editable overlay;
workspace membership alone is not treated as an import/install guarantee.

The proposed execution base is the exact frozen council candidate supplied in
the dispatch request. It is a documentation-only successor of the source
baseline above; product-source equality must be rechecked at Step 4 and before
construction. No package under `packages/friday-commands/` has been generated.

Next gate: collect all three council reports against the same candidate, report
mandatory findings and disagreements, and present the exact Step 4 decision.
Council review is not human approval. No automatic remediation loop, product
construction, PR, push, merge or release is authorized by this readiness packet.

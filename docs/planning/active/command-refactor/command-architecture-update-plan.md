# INGEST-001 — command architecture and substantive documentation plan

Status: **required planning contract; implementation not authorized**, 2026-11-11.

Chuck requires a canonical command-architecture document plus substantive
updates to affected Friday guide chapters. This is authored/reviewed engineering
work: relevant sections may need replacement or restructuring, not merely a
documentation checker run or a list of future links. The final construction
directive must name these deliverables, allowed paths and acceptance criteria.

## Canonical architecture deliverable

Produce `docs/architecture/command-execution.md` as the single canonical account
of command execution in the implemented candidate, with an explicit source/
version baseline. Planning remains in this packet until a corresponding current
implementation or explicitly accepted target exists; do not place an unbuilt
proposal in the current-architecture folder as implemented fact.

The document must explain:

1. **Friday Chat:** raw input, command lookup/aliases/custom handlers, argument
   interpretation and validation, shared handler delegation, injected capabilities,
   structured outcomes, rendering and interface effects. Identify which command
   families actually delegate and which remain Chat-owned; do not claim the
   complete file-family/TUI migration has occurred.
2. **Friday CLI and Runtime:** terminal/display/session component responsibilities,
   compatibility-container delegation, headless composition, explicit configuration
   origin and ready/deferred/unavailable capability behavior. No standalone
   `friday` launcher or CLI-owned ingestion/reorganization policy is invented.
3. **Shared owners:** Commands owns reusable argument/command semantics; Core
   owns neutral typed boundaries; Tools owns conversion/audit/adaptation; Memory
   owns ingestion/chunk plans/admission/storage; LLM owns preparation/counting/
   limits and result validation. Show declared dependencies and injected seams,
   while disclosing retained legacy lazy/undeclared edges.
4. **Execution and effects:** a real request-flow diagram from Chat/headless
   caller to conversion, common plan, embeddings and storage; the ownership of
   workers/tasks/resources; whole-request admission, cancellation/quiescence,
   partial-failure reporting and the absence of a new transaction guarantee.
5. **Configuration and deployment:** optional versus default package stacks,
   asset provisioning, exact qualified model/counter capabilities, YAML/command
   precedence, and identity-bound persistent/ephemeral store lifecycles. Explain
   the upgrade/first-run consequences using coherent synthetic path examples.
6. **Reuse and limits:** how another frontend consumes the shared capability
   without importing Chat, the separate TOOLS-DOC adoption obligation, active
   versus public-unwired/absent routes and intentional compatibility exceptions.
   Maintenance ordering, future TUI implementation and unrelated command features
   remain outside the unit.

Use compact ownership and request/lifecycle diagrams where they clarify these
boundaries. The architecture must describe actual callable interfaces and effects
from the candidate, not a desired diagram contradicted by source or tests.

## Guide and reference rewrites

The [guide update handoff](guide-update-handoff.md) owns the exact guide-file
coverage: installation/quick start, core concepts, adaptive Memory/maintenance,
Tools, multi-agent compatibility, Chat CLI, configuration, troubleshooting and
affected index/appendix entries. The final directive may authorize rewriting or
reorganizing those affected sections to produce a coherent current narrative.

- Rebuild affected command/ownership tables from the actual registry/package
  interfaces. Explain the current Chat/CLI/Runtime boundary, shared command
  families, 17-package map, and actual launcher declarations; do not retain old
  alpha3 statements that conflict with the implemented command architecture.
- Update package READMEs, configuration/schema examples, dependency/extra and
  provisioning instructions and source references with the same facts. Preserve
  the user's dirty example files; change the named packaged templates only.
- Show the new ingestion options/defaults, legacy-key changes, model limits,
  fresh-store requirements and operator-visible refusal/cancellation effects.
  Product requirements and acceptance IDs must agree with the final directive
  and implemented behavior, rather than silently redefine the scope in prose.
- Keep version/provenance explicit. Current guides describe released alpha3;
  identify what the candidate supports and what remains a release/companion
  obligation. A version-label edit alone is not a substantive documentation
  update, and old accepted guide evidence stays immutable.

This is a focused command/ingestion architecture refresh, not permission to
rewrite unrelated workflow, speech, security, MCP transport or financial behavior.
Cross-references may need repair to keep affected chapters coherent.

## Documentation acceptance — DI-36

Documentation completion requires all of the following:

| Evidence | Required acceptance |
| --- | --- |
| Authored content/diff review | Canonical architecture exists for the verified candidate; affected guide sections/tables are substantively rewritten where necessary. Review the actual changed content, not only a list of filenames. |
| Architecture-to-source map | Each material ownership, command sequence, configuration field, package/dependency claim and side-effect statement points to the actual source/schema/metadata and relevant test or probe. Resolve contradictions between architecture, requirements, guides and the final directive. |
| Verified examples | Check representative commands/help, typed YAML precedence, package/extra installation, asset paths, fresh layout, positive ingestion and safe failure examples against source and clean installed candidate evidence. Use synthetic/disposable inputs. Offline examples must not call providers or download assets; live/operator examples have explicit prerequisites and no fabricated execution claim. |
| Cross-document consistency | Chat/CLI/package terminology, command catalogue, declared entry points, defaults/limits, profile capabilities, data consequences and version baselines agree across architecture, guides, package READMEs and packaged templates. Preserve separate INGEST/TOOLS-DOC completion claims. |
| Structural checks | Documentation lifecycle, relative links/anchors, generated tables/views and applicable snippet/schema checks pass. These checks are necessary structural evidence and do not by themselves establish technical correctness or completion of rewrites. |
| Independent review | A fresh reviewer assesses the architecture, rewritten sections and evidence against the actual candidate and changed contracts. Report uncovered contradictions, unsupported examples and operator-only steps separately; no self-acceptance or claim that old guide review covers new bytes. |

The implementation report must include a requirement/change → document section →
source/configuration authority → example/test/probe matrix, rewritten/retained
section inventory and explicit remaining limits. Missing required content or
contradictory instructions fails documentation acceptance even if the link checker
passes. Publication and release remain separate from local documentation work.

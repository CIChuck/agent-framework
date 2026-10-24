# Shared command refactor — regression and validation strategy

**Status:** approved regression expectations; exact commands and fixtures must be pinned
in approved work-unit directives before implementation

## Baselines before the first source edit

Freeze a fresh inventory of Friday Chat's canonical names, aliases, metadata,
argument grammar, generated help and the separate `friday-framework-cli`
registry/API. Capture installed entry points, imports and dependency closure
for both current terminal clients. Record the 50/3 Chat snapshot and the six
selected retirements as different evidence classes: retained behavior must
match; intentionally retired behavior must match its approved retirement
contract. Existing defects and later improvements receive separate backlog
decisions rather than being silently normalized in the refactor.

Use the [phase plan's PAR coverage ledger](phase-plan.md#gate-rules-and-evidence-trail)
to connect each baseline case and alias to its handler/effect path, disposable
fixture, exact baseline receipt, owning unit, after-change receipt and approved
exception. An inapplicable case needs a reason. P0 may record an unresolved
disposition; P1 must assign every case before construction.

For each retained command family, record positive, invalid-argument,
unavailable-service, cancellation and error cases as applicable. Compare
normalized request, semantic outcome, error type/meaning, progress order,
session/runtime state, tool/file effects and UI-effect intent on disposable
fixtures. Preserve Friday Chat's established terminal output and help through
its adapter. Test TUI rendering separately when the TUI project integrates.

## Gates per migration unit

| Gate | Required evidence |
| --- | --- |
| Contract and import boundary | Shared owner imports only public neutral services; no Chat/TUI/CLI or renderer imports, cycles, private Runtime reach-through or parallel active handler. |
| Registry and syntax | Names, aliases, tokenization, defaults, help, unknown command, invalid argument and old-name retirement behavior; compare source snapshot and approved exception list. |
| Effects and safety | Disposable session, memory, transcript, file, tool, security, agent, workflow, speech and maintenance fixtures as relevant; compare ordered effects, rollback/failure and guardrails. |
| Friday Chat regression | Focused command-family suites, legacy command-surface compatibility, application/rendering checks and broader Chat suite at each family boundary. |
| `friday-framework-cli` regression | Full owning test suite, registry/completion/API checks, entry point and installed wheel behavior with and without the shared package; add direct shared-adapter tests if that role is approved. |
| Packaging and integration | Build/install shared owner and both terminal clients outside the checkout; check isolated imports, dependency closure and equivalent service effects through real adapters. |
| Independent validation | Freeze each candidate commit; fresh-context read-only review of the exact directive, diff, positive/negative evidence and baseline exceptions. Run a final aggregate review across all families. |

At each P2–P3 unit gate, rerun the affected earlier cases as well as the new
family's cases so the evidence stays cumulative. At P4, use the P1 scenario map
for cross-family state and effect interactions through installed adapters.
The retirement unit is separately authorized and tested at the order decided
in P1; its negative checks do not count as retained-command parity.

The selected retirements receive separate negative tests: old names must never
execute their former effects; help/completion and user guides must match the
approved response, and non-retired names/aliases must remain intact. Security
and workflow commands require current-behavior probes on their actual paths;
the later security/workflow capability reviews cannot be treated as completed
by a passing command test. High-impact commands such as reset, maintenance,
ingestion, migration and tool execution use disposable stores and explicit
effect assertions.

Before acceptance, run the complete Friday Chat and `friday-framework-cli`
owning suites, selected Runtime/domain suites touched by command adapters,
static/type checks for changed packages, package build and installed smoke
tests, and an aggregate command matrix comparison in the supported environments
fixed at P1. Pin the exact command and environment manifest before the P5
candidate is frozen. Record exact test counts,
skips, baseline failures and platform limits rather than calling a narrow
green subset a full regression. TUI integration reruns both terminal-client
regressions plus command-by-command Chat/TUI semantic parity, TUI interaction
tests and physical macOS/Linux terminal UAT under the separate TUI plan.

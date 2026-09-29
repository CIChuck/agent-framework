# Draft Build Plan: Runtime-Configured Skills

**Status:** Backlog definition; not approved for implementation

**Date:** 2026-09-27

**Target:** Friday runtime, Friday Chat, agent profiles, and context engineering

**Source:** Maintainer discussion of configurable skills, startup loading, prompt
placement, and large-context budgeting

## 1. Outcome And User Intent

Friday should accept a skills directory and an explicit list of selected skills
in runtime configuration, including the Friday Chat example configuration. On
startup it should find, validate, and load those skills. On applicable agent
turns, the selected skill instructions should appear in a labeled static block
directly after the configured base system prompt. Context engineering should
account for skill tokens before allocating space to tools, conversation history,
retrieved memory, and the current request.

The first useful version should support a small, ordered set of skills that are
always active. This directly implements the requested behavior and makes prompt
contents deterministic. Explicit per-turn invocation and automatic relevance
selection are valuable follow-on modes, but require separate activation and
evaluation contracts.

Large model windows, including hypothetical 250,000- to 1,000,000-token
windows, make an always-active set practical when the set is bounded. They do
not remove the need to validate the effective model limit, reserve output and
tool capacity, protect useful memory context, and expose a per-turn budget
ledger. The current Friday Chat example configures a 50,000-token context
window; a larger provider window alone does not change that setting.

## 2. Current Baseline And Architectural Gap

- `packages/friday-chat/config.example.yaml` has `chat.system_prompt` and
  `memory.context_window: 50000`, but no `skills` section.
- `FridayChatConfig` and `load_friday_py_config()` do not declare a top-level
  `skills` section. Unknown top-level sections are diagnosed and removed before
  model validation, so adding YAML alone cannot enable the feature.
- `friday-agent.skills.SkillCatalog` stores references in
  `skill_id@version` form. Agent profiles and the registry use these as
  capability/routing declarations; they do not read `SKILL.md` instructions.
- The headless agent path uses `friday-memory.ContextAssembler` and
  `PromptArchitect`. Friday Chat currently composes messages directly in
  `friday_chat.turns.processor` after tool selection and memory retrieval.
  Supporting only one prompt path would leave the other without skills.
- `PromptArchitect.calculate_fixed_costs()` counts the system prompt, tool
  schemas, and output buffer. Friday Chat calculates its own budget from
  `memory.context_window` and `memory.output_buffer`. Neither reserves skill
  tokens before retrieval.
- The queued [`friday.md` startup-context proposal](../../queued/friday-startup-context/README.md)
  also wants an instruction block after the system prompt. The two proposals
  require one precedence, placement, and budget contract before either is built.

## 3. Terminology And Format

- **Skill root:** Configured directory containing one subdirectory per skill.
- **Skill artifact:** `<root>/<name>/SKILL.md` with YAML frontmatter and a
  Markdown instruction body. Optional `references/`, `scripts/`, and
  `assets/` remain within that skill directory.
- **Discovered skill:** A valid artifact found under the root.
- **Selected skill:** A discovered skill named in configuration and permitted
  for the current runtime or agent.
- **Loaded skill snapshot:** Validated name, description, body, location,
  content digest, and measured token cost frozen at startup.
- **Active skill:** A selected skill whose body is included in a particular
  model invocation.
- **Skill context:** The ordered, labeled prompt block formed from active
  skills; it is instruction context, not retrieved memory or an executable
  tool grant.

The external compatibility baseline is the
[Agent Skills specification](https://agentskills.io/specification): a skill
directory has `SKILL.md`; `name` and `description` are required, and the
name matches its directory. Optional resources are loaded when needed.
Friday-specific configuration and governance should live outside the portable
`SKILL.md` format. The existing `skill_id@version` registry references
must be kept distinct or mapped explicitly; a standards-format skill has no
required version field.

## 4. Proposed Configuration Contract

The following is an illustrative target for
`packages/friday-chat/config.example.yaml`, not currently accepted syntax or
a committed numeric default:

```yaml
skills:
  enabled: true
  directory: ./skills
  selected:
    - name: research-method
      activation: always
    - name: writing-style
      activation: always
  budget:
    max_tokens: 20000
    max_context_ratio: 0.10
    overflow: fail
```

Configuration semantics to make exact before approval:

1. Resolve a relative `directory` against the captured startup workspace
   root, not the location of the YAML file. Define explicit absolute-path
   policy and do not search parent directories implicitly.
2. `selected` is an ordered allowlist, not a glob. Prompt order follows this
   list. Missing, duplicated, invalid, or ambiguous selected names fail
   startup with paths and safe diagnostic detail.
3. `enabled: false` preserves current startup and prompt behavior and does
   not require the directory to exist.
4. The initial supported activation value is `always`. Reject unknown values;
   do not silently treat an unsupported automatic mode as always active.
5. Parse and validate selected `SKILL.md` files once at startup. Freeze a
   snapshot for the session. Edits require restart in the first version.
6. The budget cap is the smaller of the absolute token cap and configured
   fraction of usable input capacity. Final defaults must be selected against
   the actual initial skill inventory and model profiles; the numbers above
   are examples only. A disabled feature uses zero skill budget.
7. Friday Chat and headless `RuntimeConfig` should normalize into one
   typed skills policy. Unknown keys in the skills section must fail validation,
   and the example configuration must reflect only implemented behavior.
8. The configured model context window must be explicit or derived from a
   verified model capability. A provider's advertised large window must not
   silently override Friday's smaller configured window.

## 5. Package Ownership And Data Flow

```text
config -> runtime skill loader -> immutable selected-skill snapshot
       -> turn prompt composer/context budget -> model messages
```

- `friday-core`: Own small, typed, package-neutral skill descriptor and
  selected-skill context contracts if both `friday-memory` and
  `friday-agent` consume them. This avoids a memory-to-agent dependency cycle.
- `friday-agent` or `friday-runtime`: Own filesystem discovery, validation,
  the startup snapshot, and selection policy. Reuse the present catalog only
  after its reference semantics are reconciled with portable skill names.
- `friday-runtime`: Bind the configured snapshot to headless agents and their
  sessions. A skill is not inferred from an agent's declared routing tag.
- `friday-memory`: Own prompt placement, token measurement, fixed-cost
  reservation, and prompt budget reporting. It consumes typed skill content;
  it does not scan directories or execute scripts.
- `friday-chat`: Parse the same logical skills policy, load or receive the
  startup snapshot, and use the shared placement/budget contract for normal,
  streaming, and tool-continuation turns. A full migration to
  `ContextAssembler` is optional; one shared skill composition contract is
  mandatory.

The contract must support both fake and real runtime assembly. Background
maintenance, extraction, compaction, and embedding calls do not inherit
interactive skills unless a later work unit explicitly scopes them in.

## 6. Prompt Placement, Precedence, And Context Budget

Proposed logical order:

1. Configured base system prompt and runtime safety policy.
2. Ordered, labeled active-skill block.
3. Optional workspace startup instructions such as `friday.md`, once its
   separate plan is reconciled.
4. Conversation history and selected supporting memory/tool context.
5. Current user request and in-progress tool results.

The skill block is a distinct instruction-context component. It must not
implicitly inherit system authority from a filesystem file or grant tools.
The provider-facing role mapping should preserve this logical order and be
tested with all supported model adapters. Do not invent a synthetic assistant
acknowledgment merely to force message alternation. Record the final role and
precedence decision before implementation.

Budget calculation must occur before retrieval or prompt formatting:

```text
usable_input = effective_context_window - output_reserve
fixed_input = system + active_skills + selected_tool_schemas
              + current_request + message_overhead + safety_margin
dynamic_input = max(0, usable_input - fixed_input)
```

The final budget contract must also:

- charge the measured, model-bound skill text once per model invocation,
  including wrappers and message overhead;
- use one token-estimation policy for Friday Chat and the memory prompt
  composer, with a final rendered-prompt check;
- preserve an explicit minimum useful memory/history allocation when possible;
- include tool-result growth and repeated model calls in the turn accounting;
- handle normal and cache-optimized prompt layouts identically for ordering
  and limits while keeping stable skills eligible for prefix caching;
- expose per-turn counts for system, skills by name, tool schemas, history,
  retrieved memory, current request, output reserve, and total utilization;
- distinguish the configured window from the verified provider/model limit;
- retain required always-active skill bodies intact. If they cannot fit,
  fail with an actionable budget error instead of silently truncating one.

The plan should validate at least the existing 50,000-token configuration and
representative 250,000- and 1,000,000-token configured profiles. These are
budget scenarios, not claims that a particular model or provider supports
those limits.

## 7. Loading, Safety, And Data Handling

- Validate file type, frontmatter, directory/name match, size, UTF-8 decoding,
  and duplicate names. Define behavior for symlinks and paths escaping the
  configured root before implementing discovery.
- Treat skill contents as local, potentially untrusted instructions below
  runtime policy and the base system prompt. Review skills before enabling
  them. A skill's optional `allowed-tools` field is descriptive and must not
  expand Friday tool permissions by itself.
- Do not execute skill scripts, fetch URLs, open references, or load assets
  merely because the skill is configured. Those are later, separately gated
  capabilities.
- Do not ingest skill bodies into long-term memory, extraction, or compaction
  pipelines by default. The prompt snapshot is separate from memory records.
- Make startup errors and operational diagnostics content-safe: report skill
  name, safe path, digest, status, and token cost without logging full bodies.
- Decide how `/prompt`, `/debug`, transcript capture, and exports display
  skill contents. Current raw-prompt capture may persist exact instructions;
  this must be documented and tested rather than assumed safe.
- Record skill names and content digests used for a turn so a prompt can be
  reproduced after skill files change, without making raw bodies default
  telemetry payloads.

## 8. Bounded Candidate Work Units

These are planning slices, not authorization to edit product code.

### SK-00: Contract And Reconciliation

Choose the shared DTO owner, skill-name versus legacy reference mapping,
startup-root resolution, role/precedence, budget defaults, and the interaction
with `friday.md`. Freeze exact first-pass package scope, non-goals, tests,
and a construction directive.

### SK-01: Typed Config And Startup Loader

Add strict config parsing in Friday Chat and headless runtime, discover and
validate explicitly selected `SKILL.md` artifacts, freeze the snapshot,
and test missing/duplicate/malformed/oversized/path-escape cases. No prompt
change is complete in this slice.

### SK-02: Shared Prompt And Budget Contract

Pass selected skill content to `friday-memory` through typed contracts.
Place it after the base system prompt in both attention and cached layouts.
Reserve skill costs before memory allocation, and report a complete budget
ledger. Prove over-budget handling without silent skill truncation.

### SK-03: Consumer Integration

Apply the same contract to headless agents and Friday Chat, including fake and
real startup, normal and streaming turns, tool continuation, prompt inspection,
and transcript behavior. Do not claim parity from one consumer's tests.

### SK-04: Documentation And Acceptance

Update the example config and user/developer guidance with supported syntax,
path resolution, trust and capture behavior, budget diagnostics, and examples.
Run focused package and cross-package checks, then seek independent validation
under repository policy.

## 9. Acceptance Criteria For A Promoted First Version

- AC-SK-01: A configured skill directory and ordered selection list load
  deterministically at startup in both runtime entry paths.
- AC-SK-02: Invalid, missing, duplicate, unsafe, or over-budget selected skills
  fail clearly; disabled skills preserve current behavior.
- AC-SK-03: Each configured always-active skill appears once, in config order,
  immediately after the base system prompt in every applicable model call.
- AC-SK-04: Prompt placement is equivalent across headless, Friday Chat,
  streaming, tool-continuation, attention, and cached paths.
- AC-SK-05: Model-bound skill tokens reduce the retrieval/history budget
  before retrieval begins; final rendered prompts fit the effective limit.
- AC-SK-06: A useful memory allocation is protected or a clear budget failure
  explains why it cannot be protected.
- AC-SK-07: Budget diagnostics identify per-skill and per-component token
  costs, omissions, and failures without leaking skill bodies by default.
- AC-SK-08: Skill contents never grant tools, execute bundled scripts, or enter
  long-term memory merely because they were loaded.
- AC-SK-09: Prompt inspection, transcript capture, and export behavior are
  explicit, tested, and documented.
- AC-SK-10: Existing agent `skill_id@version` routing still works, and
  instruction-skill names have an unambiguous mapping or separation.
- AC-SK-11: No-skills configurations pass existing agent, memory, runtime,
  and Friday Chat regression suites.
- AC-SK-12: Tests cover 50,000-, 250,000-, and 1,000,000-token configured
  budget scenarios with representative small and oversized skill sets.

Required negative cases include unknown config keys and activation modes,
wrong frontmatter name, unreadable file, duplicate selected name, symlink
escape, excessive skill tokens, insufficient output reserve, insufficient
memory floor, and a skill attempting to expand tool permissions.

## 10. Follow-On Enhancements To Consider

1. **Selective activation:** Explicit user invocation and relevance-based
   activation from skill descriptions, with reasons and false-trigger evals.
   Keep an always-active mode for broad instructions.
2. **Scope and precedence:** Global, workspace, agent, and session skill
   selections with deterministic conflict handling; no implicit inheritance
   across unrelated workspaces.
3. **Live management:** A read-only `/skills` inventory and budget view,
   then an explicitly authorized reload command with atomic snapshots and
   rollback on validation failure.
4. **Versioning and provenance:** Pin a skill revision or content digest for
   reproducible sessions; report when configured skills drift on disk.
5. **Composition:** Declare optional dependencies and conflicts between
   skills, then validate ordering and budget as one atomic selection.
6. **Prompt-cache efficiency:** Keep stable skill blocks in a cacheable prefix,
   but measure cache hits separately from input-token use and prompt quality.
7. **Resources and scripts:** Add on-demand access to references, assets,
   and scripts only after tool permissions, sandbox, and audit behavior are
   designed and approved.
8. **Evaluation:** Curate representative tasks for each proposed skill and
   compare no-skill, always-active, and selective modes for adherence,
   retrieval quality, latency, cost, and tool safety.
9. **Portability:** Accept standards-format `SKILL.md` folders without
   requiring Friday-specific frontmatter; store Friday policy in config or
   a separate manifest.

## 11. Decisions And Promotion Gate

Before promotion from backlog, the maintainer should review:

- the initial skills and their real sizes, to choose defensible token caps;
- whether the first release targets both Friday Chat and headless agents
  together, as recommended here;
- the exact provider-facing role of the skill block and its precedence
  relative to `friday.md`;
- workspace-root and external-directory trust rules;
- how raw prompt capture and prompt exports handle skill contents;
- whether legacy `skill_id@version` references remain routing-only or gain
  an explicit mapping to instruction skills; and
- the authoritative model-context limit and minimum memory floor.

Promotion requires a current build plan with bounded first-pass scope, a
tactical plan, a named feature branch and baseline, and maintainer approval
under the development board. This backlog document grants no implementation,
push, merge, release, or publication authority.

# Agent Framework Tool Security and Workspace Review

**Date:** 2026-08-10
**Status:** As-built security review
**Scope:** Tool availability, tool authorization, filesystem scope, command execution, network egress, and related configuration in Friday Chat and the headless Agent Framework runtime.

## Executive Summary

Agent Framework does not currently provide an enforceable, configuration-defined workspace boundary for tool execution. Friday Chat's example configuration controls whether model tool calling is advertised and which tools are registered, but it does not define per-tool permissions, approval requirements, filesystem roots, network destinations, or a common execution policy. The headless runtime has a `workspace_root` and more capable tool-provider filters, but its workspace setting is not propagated into the tools that access the filesystem or execute commands.

The resulting effective security boundary is generally the operating-system account running Friday. The default filesystem sandbox narrows that boundary by blocking selected paths and patterns, but it permits the user's home directory and temporary directories. The registered command tool can execute a host shell from any existing directory, subject to its command blocklist, and inherits the process environment. HTTP upload can combine permitted local file reads with network egress.

Tool registration and schema selection are useful availability controls, but they are not a complete authorization system. Several execution paths can invoke registered capabilities outside the normal model tool-selection path, and there is no single policy enforcement point shared by Friday Chat, the headless agent runtime, commands, workflows, and MCP tools.

Until a unified policy is implemented, Friday should be treated as a high-privilege local agent. High-impact tools should be omitted from the registry unless they are explicitly required and the host environment itself supplies the intended containment.

## Review Method

This review treats current code and executable configuration models as authoritative. Older guides and planning documents were used for comparison, but not as evidence that a planned control is implemented. The review was read-only; it did not change application code or configuration.

The primary surfaces examined were:

- Friday Chat configuration, registry construction, tool selection, tool execution, direct commands, file commands, and shell service.
- `friday-tools` filesystem, HTTP, and shell implementations.
- Headless runtime configuration and tool-provider loading.
- `friday-agent` tool dispatch.
- `friday-sandbox` process and Docker execution behavior.
- Existing security guidance and the draft tool-governance plan.

## As-Built Control Matrix

| Control | Friday Chat | Headless Agent Framework |
| --- | --- | --- |
| Disable model tool calling | Yes, through `tools.enabled` | Yes, through provider enablement and tool exposure |
| Include or exclude tools | Explicit registry entries | Provider-level include/exclude filters for tools and categories |
| Per-tool permissions | No | No |
| Read/write/destructive classification enforcement | No | No |
| Per-call approval | No; workflow approvals are not tool-call approvals | No; workflow approvals are not tool-call approvals |
| Configured workspace root | No | Present in `RuntimeConfig`, but not enforced by tool construction or dispatch |
| Filesystem containment | Default home and temporary-directory sandbox for many tools; some command paths bypass it | Tool-dependent; runtime workspace is not a universal boundary |
| Central authorization checkpoint | No | No |
| Argument-sensitive authorization | No | No |
| Network destination policy | No unified policy | No unified policy |
| Execution audit decision record | No unified allow/deny audit | No unified allow/deny audit |

## Detailed Findings

### 1. Friday Chat has no enforceable workspace configuration

The Friday Chat example configuration contains a `tools` section with a global `enabled` flag, registry declarations, loop limits, and context-budget settings. Its default registry includes file listing, file reading, file writing, web access, HTTP mutation and transfer tools, command execution, and finance tools. It does not identify a workspace root or define read and write roots.

`ToolsConfig` in `packages/friday-chat/src/friday_chat/config.py` models tool enablement, loop settings, registry entries, and context limits only. `SecurityConfig` models sanitization only. Both derive from a flexible configuration model that permits unknown fields. A setting such as `tools.workspace` can therefore be accepted into extra model data without affecting runtime behavior. This is particularly risky for security-related configuration because an operator can believe a boundary is active when it is ignored.

The construction path in `packages/friday-chat/src/friday_chat/adapters.py` imports the configured tool class and passes its constructor arguments, but it does not inject a canonical workspace or shared filesystem policy. A registry entry with `enabled: false` is also not treated as disabled by the current registry parsing path; every mapping in the registry list is considered a configured tool specification.

**Assessment:** High risk. Friday Chat has no fail-closed workspace contract, and security-looking extra configuration can be silently ignored.

### 2. `tools.enabled` controls model exposure, not every execution path

When `tools.enabled` is false, Friday Chat's selection layer returns no tool definitions to the model. This prevents ordinary model-generated tool calls. The registry is still constructed, however, and direct command paths can access registered tools.

For example, `/run-tool` in `packages/friday-chat/src/friday_chat/commands/registry.py` finds a tool in the registry and invokes it without checking the global `tools.enabled` value. `/tools` likewise reports registry contents independently of model exposure.

This may be useful if the product intentionally supports tools that are disabled for the model but available to a human operator. The current name and configuration structure do not express that distinction. A complete model needs separate concepts such as:

- Capability enabled or disabled globally.
- Model access.
- Direct human-command access.
- Workflow or service access.

**Assessment:** High risk of operator misunderstanding. `tools.enabled: false` is not a universal tool prohibition.

### 3. Tool selection is not authorization

The Friday Chat tool loop correctly rejects a model-returned tool name that was not included in the definitions selected for that turn. This is a useful local control. The automatic selector can, however, fall back to all registered tools when relevance scoring finds no match. Schema count and context-budget limits are resource and relevance controls, not permissions.

The headless agent execution path has a similar separation. Active tool schemas influence what is sent to a provider, but `AgentBase._execute_tool_call` looks up the requested tool in the registry and executes it without independently verifying that the tool was active for that turn. Therefore, provider-facing schema restriction is not a durable authorization boundary.

An untrusted or malfunctioning provider response must not be able to authorize an operation merely by naming a registered tool. Authorization must be repeated at execution time over the validated tool name and exact arguments.

**Assessment:** High risk. Availability and prompt exposure are being asked to carry security responsibility that they do not consistently enforce.

### 4. The default filesystem boundary is the user's home directory, not a project workspace

`FilesystemSandbox` in `packages/friday-tools/src/friday_tools/sandbox.py` defaults to allowing the current user's home directory and temporary directories. It blocks selected system paths and sensitive filename patterns, including common SSH and environment-file locations. It canonicalizes paths, which helps with ordinary traversal and symlink resolution.

Under the observed local defaults, the effective allowed roots were the user's home directory and macOS temporary directories. The repository working directory and locations such as the user's Documents directory were allowed, while `/etc/passwd` was denied.

This boundary is broader than the application workspace expected by the user. File read, smart file read, file write, directory operations, HTTP upload sources, and HTTP download destinations generally receive this default sandbox because Friday Chat does not inject a narrower one.

Path pattern denial is also weaker than a default-deny root policy. New sensitive filenames, alternate credential locations, and valid-but-unintended user files remain exposed unless individually blocked.

**Assessment:** High risk for confidentiality and integrity. The effective root is substantially broader than the apparent application scope.

### 5. Some direct Friday Chat commands bypass the filesystem sandbox

The `/read` and `/ingest` command paths construct `SmartFileReader` directly. The reader expands and resolves the supplied path and then reads it without applying `FilesystemSandbox` or a workspace policy. Replay input similarly reads a supplied CSV path directly.

Transcript export code has its own configured-root validation, which is a positive path control, but it is local to that feature. The existence of several independent path-validation strategies creates policy drift and makes a global workspace claim impossible.

Human-entered commands may warrant a different approval policy from model-generated calls, but both should still use the same resource boundary unless configuration explicitly grants a different scope.

**Assessment:** High risk if the intended guarantee is "Friday can only access its workspace." Direct commands do not share one enforceable boundary.

### 6. Command execution is host execution, not workspace containment

`CommandExecuteTool` in `packages/friday-tools/src/friday_tools/shell/command.py` accepts an arbitrary existing directory as `cwd`; it does not require that directory to be within a configured workspace. It executes through the host shell, inherits the Friday process environment, and allows supplied environment additions. A command blocklist and parser reject some dangerous input, but they do not provide operating-system isolation and can be difficult to make complete in the presence of interpreters, wrappers, shell features, and newly installed programs.

Friday Chat also has a separate `!command` shell service that is disabled by default. Disabling that service does not disable the independently registered `command_execute` tool. These two command surfaces can lead an operator to believe shell access is disabled when model-accessible host command execution remains registered.

Changing only `cwd` to the workspace would reduce accidental access but would not securely contain a host shell. A command can still reference absolute paths, parent paths, mounted filesystems, environment secrets, subprocesses, and the network. Secure command execution requires an actual operating-system or container boundary, a minimal environment, an explicit mount set, and a network policy.

**Assessment:** Critical when untrusted content can influence tool calls; otherwise high risk. The tool has host-user authority subject to application-level filtering.

### 7. HTTP tools create a local-file egress path

The HTTP upload tool validates its source with the default filesystem sandbox. Because that sandbox permits most of the home directory, a permitted user file can be uploaded to a network destination allowed by the HTTP client. HTTP download can write into broadly permitted local destinations.

This is an argument-sensitive compound capability: local read plus network egress for upload, and network ingress plus local write for download. Treating it only as an "HTTP tool" or only as a "file tool" understates its effects. Authorization must evaluate both the local path and remote destination for the exact call.

**Assessment:** Critical for confidentiality when model tool use is enabled and sensitive user files exist under an allowed root.

### 8. `RuntimeConfig.workspace_root` is an assembly path, not a tool security boundary

The headless runtime defines `runtime_data_root` and `workspace_root` in `packages/friday-runtime/src/friday_runtime/config.py`. Local defaults use the current working directory as the workspace; container and cloud profiles use fixed workspace paths. The runtime uses these paths for topology, artifacts, transcripts, scratch data, and related assembly behavior.

The runtime tool-loading path does not inject `workspace_root` into filesystem or command tools. Tool-provider configuration can filter discovered tools and categories, but filtering registration does not constrain the resources an included tool may access.

The setting is valuable and should become the canonical source for a workspace policy, but current code does not support describing it as an enforced tool sandbox.

**Assessment:** Medium-to-high risk of documentation and operator assumptions exceeding implementation.

### 9. `friday-sandbox` does not currently solve general tool containment

The sandbox package supports temporary workspaces and a Docker execution backend with controls such as disabled networking, a read-only root filesystem, non-root execution, and explicit mounts. That design can provide meaningful containment when it is explicitly selected and correctly configured.

The Python execution tool currently creates a subprocess sandbox by default. That backend starts a host Python process, inherits the environment, and does not supply host-filesystem isolation merely because its type is named "sandbox." Friday Chat's current example registry does not include Python execution, but headless discovery can expose tools outside that example.

The sandbox workspace is also an execution-artifact workspace, not automatically the user's configured project workspace. These concepts need an explicit contract rather than a shared name.

**Assessment:** Medium risk today; high if subprocess execution is assumed to be secure containment.

### 10. Sanitization is not authorization

Friday Chat's `security.sanitization` settings and category risks describe how untrusted content should be labeled or sanitized. They do not authorize tool names, paths, commands, destinations, or side effects. Direct `/run-tool` result sanitization is also narrow and does not establish a general trust boundary.

Output sanitization, provenance, quarantine, and memory-ingestion safety remain important. They must operate alongside, not in place of:

- Tool availability policy.
- Exact-call authorization.
- Filesystem and network resource policy.
- Side-effect approval.
- Execution isolation.

**Assessment:** Medium risk of confusing adjacent security mechanisms.

### 11. Security documentation overstates implemented configuration

`docs/guides/10-configuration.md` describes extensive tool allowlists, permissions, context restrictions, and parameter restrictions that are not represented by the current Friday Chat or headless runtime configuration models. `docs/guides/security-configuration-guidelines.md` is clearer that portions of the architecture are planned, but it is not an as-built guarantee.

The draft `docs/planning/queued/tool-governance/build-plan.md` provides a strong starting model: default deny, effect classification, argument-sensitive policy, exact-argument approval, a single execution checkpoint, and auditability. It should be extended with explicit workspace, path, command, environment, and network policy and with the bypass inventory identified in this review.

**Assessment:** Medium operational risk. Documentation can cause unsafe deployment decisions even when the code behaves exactly as implemented.

## Required Security Model

A durable design should separate three questions that are currently conflated:

1. **Availability:** Is this capability registered and visible to this caller?
2. **Authorization:** May this actor execute this exact validated call now?
3. **Resource scope:** Are the referenced paths, commands, environment variables, and network destinations within policy?

The answer to one question must not imply the answers to the others.

### Shared typed policy contracts

Create typed, fail-closed contracts for at least:

- `WorkspacePolicy`: canonical workspace root, allowed read roots, allowed write roots, temporary-path policy, sensitive-pattern denials, and symlink behavior.
- `ToolPolicy`: default decision, actor-specific access, effect classification, approval mode, and tool-specific argument constraints.
- `CommandPolicy`: execution backend, allowed commands, workspace-only working directory, environment allowlist, timeout and resource limits, and network access.
- `NetworkPolicy`: destination allowlist, protocol restrictions, private-network rules, upload/download policy, and redirect behavior.

Security-critical configuration should reject unknown fields. A misspelled or unsupported security option must stop startup rather than survive as unused extra data.

### One execution authorization checkpoint

Every tool call should pass through one dispatcher after schema validation and before implementation execution. The dispatcher should:

1. Identify the actor and invocation surface.
2. Verify that the capability is available to that actor.
3. Classify effects from the exact arguments.
4. Resolve and canonicalize referenced resources.
5. Evaluate workspace, network, command, and environment policy.
6. Obtain a required approval bound to the exact immutable arguments.
7. Execute through the required isolation backend.
8. Record a structured allow, deny, approval, result, and error audit trail.

The same checkpoint must cover:

- Friday Chat model tool calls.
- `/run-tool` and other direct commands.
- `/read`, `/ingest`, `/replay`, and export paths.
- Bang-shell execution.
- Headless `AgentBase` dispatch.
- Workflows and scheduled work.
- MCP and future provider-loaded tools.

The implementation subcomponent must not be able to approve its own call. A tool schema, model response, or registry entry must never serve as proof of authorization.

### Filesystem rules

The workspace root should be captured as an absolute canonical path at startup. Relative policy roots should resolve against that captured root, not the process's later working directory. Default policy should deny paths outside the workspace and separately evaluate sources and destinations.

The path implementation must test and document:

- `..` traversal and absolute-path escape.
- Existing and newly created symlinks.
- Race-resistant file opening where meaningful, including no-follow or directory-relative operations.
- Read versus write roots.
- Source versus destination policy for copy, upload, download, archive, and extraction operations.
- Sensitive files inside an otherwise allowed workspace.
- Temporary-file creation and cleanup.

Home and global temporary directories should not be implicitly allowed in a workspace-contained profile.

### Shell and code execution rules

Host subprocess execution should remain disabled under secure profiles. A workspace-only `cwd` is not sufficient containment. If command or code execution is enabled, it should use a hardened container or equivalent OS isolation with:

- Only the approved workspace mounted, at the required access mode.
- A minimal allowlisted environment with no inherited provider keys or application secrets.
- Non-root execution.
- A read-only base filesystem.
- Disabled network by default.
- CPU, memory, process-count, output-size, and time limits.
- An explicit command or executable policy.

If the subprocess backend remains available for developer convenience, configuration and documentation should identify it as uncontained host execution.

## Proposed Configuration Shape

The following is illustrative target configuration, not a currently supported interface:

```yaml
runtime_paths:
  workspace_root: ${FRIDAY_WORKSPACE_ROOT}

tools:
  enabled: true
  mode: selected
  include_tools:
    - directory_list
    - file_read
    - file_write
  exclude_tools:
    - command_execute
    - http_upload

security:
  tool_policy:
    default: deny
    tools:
      directory_list:
        effects: [read]
        approval: never
      file_read:
        effects: [read]
        approval: never
      file_write:
        effects: [write]
        approval: per_call
      command_execute:
        effects: [destructive]
        approval: per_call
      http_upload:
        effects: [read, egress]
        approval: per_call

  filesystem:
    default: deny
    read_roots: ["."]
    write_roots: ["."]
    allow_home: false
    allow_temp: false
    symlinks: deny
    deny_patterns:
      - "**/.env*"
      - "**/.ssh/**"
      - "**/.git/**"
      - "**/*.key"

  shell:
    enabled: false
    cwd: workspace_only
    environment_allowlist: [PATH, LANG]
    allowed_commands: []

  network:
    default: deny
    allowed_hosts: []
```

The final schema should also distinguish model access from direct human-command access. An operator should be able to grant a tool to one actor without implicitly granting it to every execution surface.

## Recommended Built-In Profiles

Profiles can make the secure choice understandable while preserving explicit advanced use cases:

| Profile | Intended behavior |
| --- | --- |
| `chat_only` | No filesystem mutation, shell, code execution, or unrestricted network tools |
| `workspace_readonly` | Read and list only inside the configured workspace; no egress or shell |
| `workspace_standard` | Workspace reads without approval; writes require exact-call approval; shell and egress remain off unless separately granted |
| `unrestricted_dev` | Explicit high-risk opt-in with startup warning and full audit; never the default |

A profile should expand into ordinary typed policy so that its effective permissions can be printed, tested, and audited.

## Remediation Sequence

### Phase 0: Immediate operational mitigation

Until enforcement exists:

- Remove `file_write`, HTTP mutation/transfer tools, and `command_execute` from the Friday Chat registry unless they are needed for the session.
- Do not rely on `tools.enabled: false` as a universal prohibition while direct command execution paths remain available.
- Run Friday under a dedicated least-privilege operating-system account or an external container with only the intended workspace mounted.
- Do not expose credentials in the Friday process environment when host execution or upload tools are enabled.

### Phase 1: Ratify contracts and semantics

- Extend the draft tool-governance plan with workspace, path, shell, environment, network, and actor-surface policy.
- Define the precise meanings of global enablement, registration, model access, human-command access, and workflow access.
- Define effect classifications including `READ`, `WRITE`, `DESTRUCTIVE`, `EXECUTE`, `NETWORK`, and `EGRESS`.

### Phase 2: Add fail-closed configuration

- Add shared typed policy models through public package interfaces.
- Reject unknown security fields.
- Give Friday Chat an explicit workspace setting and bridge headless `RuntimeConfig.workspace_root` into the same policy contract.
- Provide a command that prints the resolved effective policy without secrets.

### Phase 3: Centralize dispatch authorization

- Introduce the single policy-enforcing dispatcher.
- Route Friday Chat, headless agents, workflows, commands, and MCP calls through it.
- Deny unclassified tools and callers by default.
- Treat selected tool schemas only as availability metadata.

### Phase 4: Enforce workspace scope everywhere

- Inject the shared workspace policy into file, directory, transfer, export, replay, and ingestion operations.
- Remove feature-local bypasses and duplicate path-policy implementations.
- Enforce source and destination policy independently.

### Phase 5: Add approvals, egress control, and audit

- Bind approvals to exact validated arguments and the resolved resources.
- Make approvals single-use and expiring.
- Add destination-aware network and upload policy.
- Record structured authorization decisions and outcomes with secret redaction.

### Phase 6: Harden command and code execution

- Require a genuinely isolated backend for secure profiles.
- Remove ambient credentials and broad mounts.
- Make network access an explicit grant.
- Clearly label or disallow the host subprocess backend in secured deployments.

### Phase 7: Align documentation and migration

- Correct guides that describe planned permissions as implemented.
- Document compatibility behavior and provide a migration path for existing registry configuration.
- Publish the exact guarantees and limitations of each built-in profile.

## Required Validation

At minimum, regression and integration coverage should prove:

- Reads, writes, listings, uploads, and downloads outside the workspace are denied.
- Absolute paths, parent traversal, and symlink escapes cannot bypass the workspace policy.
- Source and destination permissions are independently enforced.
- Sensitive files can be denied even when located inside an allowed root.
- `tools.enabled`, per-entry enablement, model access, and direct-command access have distinct documented behavior.
- A tool not active for the caller cannot execute merely because it exists in the registry.
- Unknown tools, unclassified tools, and unknown security configuration fail closed.
- Approval is bound to exact arguments, expires, is single-use, and becomes invalid if arguments change.
- Shell execution cannot select a host directory outside the workspace or inherit unapproved environment variables.
- Secure profiles cannot use uncontained subprocess execution.
- `/read`, `/ingest`, `/replay`, exports, `/run-tool`, workflows, and MCP calls use the same authorization path.
- Network redirects and resolved destinations remain within policy.
- Audit records contain the actor, policy decision, effects, resolved resources, approval identity, and outcome without leaking secrets.

## Positive Existing Foundations

Several current mechanisms can be retained as components of the stronger design:

- Friday Chat verifies that ordinary model-returned tool names were selected for the turn.
- The filesystem sandbox canonicalizes paths and blocks a set of known-sensitive locations.
- Transcript exports apply a configured-root check.
- Headless runtime configuration already has a workspace-root concept.
- Runtime provider loading already supports tool and category filters.
- The Docker sandbox has meaningful isolation-oriented defaults when it is explicitly used.
- The draft tool-governance plan already defines default deny, exact-argument approval, effect-aware policy, a central checkpoint, and auditability.

These are useful building blocks, but none alone establishes the intended security boundary.

## Conclusion

The user's observation is correct: the current application configuration does not identify or enforce a tool workspace. Agent Framework has partial controls for registration, provider exposure, path filtering, output sanitization, and isolated execution, but they are not composed into a single security model. The immediate need is not another isolated allowlist. It is a shared, fail-closed policy boundary that authorizes every exact tool call and constrains every referenced resource regardless of how the call entered the system.

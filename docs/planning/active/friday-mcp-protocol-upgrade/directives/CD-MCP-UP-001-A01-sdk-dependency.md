# CD-MCP-UP-001 A01: necessary SDK dependency version exception

Status: Approved by Chuck Russell on 2026-10-12.
Approval: [exact statement and frozen proposal](CD-MCP-UP-001-A01-approval.json).

## Decision

Permit exactly one existing workspace dependency version change:
`idna==3.11` to `idna==3.20`, required by the approved development interoperability
counterpart `mcp==2.3.0`. Retain every other existing package version and supported
resolution-context selection. This exception changes no protocol profile,
product path, capability, runtime configuration, or construction criterion.

The parent [directive](CD-MCP-UP-001-client-core.md) currently permits the exact
SDK and necessary new transitive dependencies but requires preservation of
unrelated existing versions and stopping on dependency churn. Because IDNA is
already shared by existing HTTP consumers, record this existing-version exception
explicitly before installing or committing the changed dependency set. This is
not permission for a general workspace upgrade or renewed telemetry waiver.

## Evidence and concrete proposed delta

The [original resolver failure](../execution/dependency-conflict/no-churn-resolution.stderr)
proves that all available `httpx2>=2.10.0` candidates require `idna>=3.18`, while
the workspace pins `idna==3.11`. Both the preferred resolution and the SDK's
minimum HTTP version therefore require an existing-version change. The SDK
cannot meet the old pin through a different compatible HTTP dependency.

The [machine-readable inventory](../execution/dependency-conflict/report.json)
compares complete existing version sets: IDNA is the only changed set. The
[proposed full lock](../execution/dependency-conflict/proposed-uv.lock.gz) has
SHA-256 `aab33ed773dcdb50a65dd86af84bd1e6e26dc3486da7b04588082d72a7b18ce2`.
The [proposed package metadata](../execution/dependency-conflict/proposed-mcp-pyproject.toml.gz)
adds only the already-approved direct JSON Schema/reference dependencies and
development SDK. The new SDK transitive packages are listed individually in the
inventory; existing `httpx`, Pydantic, OpenTelemetry, gRPC and other dependency
versions are preserved. Public release metadata is retained with the evidence.

Select IDNA 3.20 from the compatible resolution; freeze its artifact hashes from
the lock. IDNA performs Unicode hostname encoding/validation, so this shared
version change may affect existing HTTP clients even though Friday's custom
MCP client does not adopt the SDK at runtime. This is why broad regression gates
remain mandatory. No new live network test is authorized.

## Construction and verification after approval

The original twelve product paths and CD-AC-01 through CD-AC-08 remain unchanged.
No direct IDNA runtime dependency, root-project constraint, source suppression,
unrelated dependency upgrade, provider change, or remote MCP activation is added.

1. Record explicit maintainer approval and freeze this amendment with the original
   directive, approval receipt, active controls, and exact dependency proposal.
2. Reproduce the resolution in the isolated snapshot. Compare version sets and
   all supported resolution contexts to the original lock, permitting only IDNA
   3.11 to 3.20; fail on any other existing selection drift.
3. Install only the locked validation dependencies into the private environment,
   recording SDK, IDNA and necessary transitive artifact hashes. SDK remains a
   development fixture dependency; do not sync the user's shared environment.
4. Execute the original full focused/package/runtime/Chat/telemetry/root gates,
   byte/depth/deadline/schema/lifecycle/privacy tests and SDK wire interoperability.
   Original raw root lint debt stays separate, with no new waiver.
5. Freeze a committed exact-scope product candidate and require the original
   fresh-context, read-only independent review before proposing completion.

Stop if the concrete lock cannot be reproduced, another existing version or
resolution selection changes, effects exceed the fixture/dependency profile,
or any original mandatory check fails. No source construction, SDK installation,
interop execution or acceptance is claimed by this proposal.

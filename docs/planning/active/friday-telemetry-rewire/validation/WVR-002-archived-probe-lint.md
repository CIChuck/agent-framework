# Approved WVR-002: immutable historical MCP probe diagnostics

Status: Explicitly approved, 2026-10-05, by repository maintainer Chuck Russell.
Approval evidence: "I approve both REM-004 and WVR-002."
Date: 2026-10-05. Work unit: TELEM-01 / REM-004.
Owner: repository maintainer Chuck Russell; controller records exact evidence.
Follow-up: REM-004-HIST-01, described below. WVR-001 is separate and unapproved.

Approved A06/WVR-003 supplement, 2026-10-06: "I approve A06 and WVR-003".
Only the zero-live condition below is superseded by exactly one independently
matched live CommandRegistry UP046 under [WVR-003](WVR-003-command-registry-variance.md).
The archival scope remains326, its identities/hashes/config/tool/expiry unchanged.
All other live findings and mandatory gates remain failures.

The [exact scope inventory](../remediation/REM-004-scope.json) freezes 326 Ruff
diagnostics in four accepted MCP validation probe artifacts, their normalized
path/code/location/message identities and complete SHA-256 file hashes. They
account for 326 of the 337 preexisting findings and 326 of the current 459;
the Python target change added no findings in these archive files. The current
133 live findings are excluded from this proposal and must be fixed.

The exception preserves reproducible accepted evidence. Reformatting those probes
would change their recorded review artifacts; adding a global exclude or rule
suppression would hide future problems. This proposal changes only the explicit
gate disposition for the exact historical findings, leaving files and root Ruff
invocation untouched.

Under this explicit approval, the validator must independently run unchanged root Ruff,
retain its raw nonzero result, normalize paths and compare a sorted multiset of
path/code/location/end_location/message to the 326 archive entries in scope.json.
Verify all four SHA-256 file hashes, zero additional diagnostics, zero live
diagnostics, and all other mandatory checks passing. The report states
"root Ruff nonzero; exact 326 archival findings covered by approved WVR-002"
instead of claiming raw lint passed. No pytest, typing, security, localhost,
source/API, telemetry or future-phase failure is covered.

Cleanup point: REM-004-HIST-01 is a proposed archive-validation policy decision
owned by the maintainer, to be considered before aggregate acceptance beyond
TELEM-01. It must decide how archived executable evidence is validated without
rewriting prior proof. No automatic archive edits or implementation are authorized.
This exception expires after the TELEM-01 acceptance decision or immediately
if any archive content hash, covered diagnostic identity, Ruff version/target,
or lint configuration changes. Local evidence-closeout commits with unchanged
governed content do not extend its work-unit scope. Renewal requires explicit
maintainer approval and fresh independent review.

The separate WVR-002 approval is recorded above. Aggregate AC-06 remains
nonpassing until all other required checks pass and this exact disposition is
independently verified. Approval supplies no test or typing exception.

Approved tool baseline: Ruff 0.14.10, root target py313. Frozen lint configuration
SHA-256 inventory (a change expires this exception):

```json
{
  "packages/friday-agent/pyproject.toml": "155343ffc1affe151e5a8b13c898d28f2bb1c23978487a6371fa56c02368aa26",
  "packages/friday-chat/pyproject.toml": "4fa72a6497d637920558b4ebe2cddd13e99fb1191c8a432cb2c7d031a0926de5",
  "packages/friday-cli/pyproject.toml": "19a2898a4716ba4f481f8396c7605b7deefa077e536b5b7c6ebb85bb06ca8a00",
  "packages/friday-core/pyproject.toml": "001b4d83e69969664d38c91f007d618df82674cc379c2acfa12767703eafa594",
  "packages/friday-finance/pyproject.toml": "c410c9b183df854d6fb1be274cfafaf31d560b4b3faa4bb2c65052f78b711070",
  "packages/friday-llm/pyproject.toml": "672f623315a1113e459cd481f3de4324c7c29767cf31aeb71eab34fa078960a4",
  "packages/friday-mcp/pyproject.toml": "fa75cbf3de3ba00fb9f853419a6f9f7f1230c0435de8efbb247814224acdcef2",
  "packages/friday-memory/pyproject.toml": "0f0cfa552fdbd2127d5e186d8847db331a9aaef70175569e9cfe77098798c511",
  "packages/friday-moltbook/pyproject.toml": "136f6278e82471ebaae3a62bdb8379a6f8d7b6b4e4bef5cb78b196ff72886deb",
  "packages/friday-optimization/pyproject.toml": "b89bdecd833287a1628c17c84bc61cb03ec8a3c4b7ea27f1476d9a2d997c9bb2",
  "packages/friday-runtime/pyproject.toml": "cc426372026847a66dc8f8a43f135a498b1a2e3861b0b24ad14c639807eedbc1",
  "packages/friday-sandbox/pyproject.toml": "51c56051ccc351c58ef91aec0a325a643751d824697e0a9293040fe3624b7d25",
  "packages/friday-speech/pyproject.toml": "0bf80e8501cce2e6c3161ac5ef942855269cefc88da2ee598b875de674487ff4",
  "packages/friday-telemetry/pyproject.toml": "8b4a0abbbd8c2a76b81d2763176c934c9cf620b864e09e4e3b4663950218e5e9",
  "packages/friday-tools/pyproject.toml": "1db7f0c87c7197b5b264e2f4e7f2fbd84e8febbdd040665edba9cd898e715326",
  "packages/friday-transcript/pyproject.toml": "4a58596abafe3f7ca409084b1a0627f77164aabb48cefa2dcc217211b0ba1679",
  "pyproject.toml": "b85b708def24f4f2045a12388f7026ce361bdf6c13490f0f160fdfe3176e3a77"
}
```

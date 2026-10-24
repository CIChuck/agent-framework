# A01 IDNA regression assessment

Date: 2026-10-12. Approved target: **3.11 to 3.20**, not version 3.2.
Approval is recorded separately in
[the A01 receipt](../directives/CD-MCP-UP-001-A01-approval.json).

## Outcome

No Friday product regression has been demonstrated by this bounded comparison.
There are observable hostname-processing changes that consumers must tolerate.
This result is dependency preparation evidence, not full MCP construction
verification, independent VERIFIED, acceptance or delivery.

The approved SDK 2.3.0 requires httpx2>=2.10.0, whose available releases require
IDNA>=3.18. IDNA is shared with existing HTTP dependencies; the custom Friday
MCP client continues to use its own protocol core. The first approved modern
transport is stdio, which does not perform hostname resolution itself.
No direct IDNA imports or calls were found in Friday Python package sources.

## Concrete behavior changes and exposure

| Change | Evidence and practical implication |
| --- | --- |
| Restored strict ASCII rules in direct `uts46_remap()` calls | Probe confirms underscore, punctuation and space inputs now fail with `InvalidCodepoint`. Existing HTTPX, Requests and YARL URL construction did not change for those same synthetic ASCII cases. Do not generalize direct-helper changes into a claim that all HTTP underscore URLs break. |
| Stronger domain/input length enforcement | Probe confirms a 255-character domain fails decoding and incremental encoding where 3.11 accepted it; excessive inputs also fail earlier. Applications relying on permissive handling of invalid hostnames may observe new exceptions. |
| Unicode tables/mapping changes | Upstream moves from Unicode 16 to 18 and corrects U+A7F1. The synthetic YARL URL containing that rare character changes from `xn--z88a.example` to `s.example`; this is a real changed URL result, not an observed live routing failure. Common international-name cases were unchanged. |
| Canonical Punycode enforcement | Upstream documents rejection of noncanonical A-labels. This is a compatibility risk for malformed stored hostnames; this probe did not establish a concrete noncanonical-label example that changed. |
| Error details and deprecated arguments | Upstream changes some exception subclasses, adds structured error attributes and warnings. Probe includes exception-detail changes. Friday has no direct IDNA message parsing or transitional-argument calls in package sources. |

Upstream also reports fixing quadratic processing of excessive input. The
length rejections therefore include hardening, rather than evidence of a
failure on a legitimate endpoint. Friday's Python >=3.13.4 requirement already
exceeds IDNA's new Python 3.9 minimum.

Primary release evidence: [tagged upstream history](https://github.com/kjd/idna/blob/v3.20/HISTORY.md),
also captured byte-for-byte with SHA-256 in the probe receipt.

## Checks performed

- Reproduced the proposed lock from the original baseline using an empty,
  credential-free environment and cached public metadata. Result is exactly
  SHA-256 `aab33ed773dcdb50a65dd86af84bd1e6e26dc3486da7b04588082d72a7b18ce2`.
- Frozen lock check passes offline without mutation.
- Compared existing selections, sources and runtime/extra/development edges in
  24 Python/platform/architecture contexts. Only the approved IDNA version
  exception and approved new MCP JSON Schema/reference edges occur. Every
  other existing package's sdist/wheel artifact records are unchanged. These
  are static marker checks, not execution on 24 machines.
- Ran 352 synthetic offline operations per version with Python 3.13.10:
  encode, decode, UTS46 remapping, incremental encoding and URL preparation
  through unchanged HTTPX 0.28.1, Requests 2.32.5 and YARL 1.22.0.
  All 57 representative ASCII/common international-name consumer checks were
  unchanged. There were 12 semantic changes across other cases, plus changes
  in exception details; complete before/after results are retained.
- Used the exact approved IDNA wheel, SHA-256
  `ab7ae7122974553370f0bdb919e1a960b2cd1bc1ef0276416d896db81c14582c`,
  extracted only into a private temporary probe directory. Baseline remains
  installed IDNA 3.11. Network operations were prohibited during probes.

## Remaining authorized work

The full private locked validation environment, official SDK stdio execution,
new client-core implementation, original focused/package/cross-package/root
regression gates and fresh independent committed-candidate validation remain.
Proceed under the original CD-MCP-UP-001 plus approved A01; no further approval
is needed for that already-bounded work. No shared environment synchronization,
live DNS/HTTP request, telemetry exporter, credential access or publication
occurred during this assessment.

Raw commands, exit codes, hashes, full probe results and scripts are retained
under [idna-regression](idna-regression/manifest.json).

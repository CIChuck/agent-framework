# VAL-UP05-02 independent review

**CHANGES_REQUESTED**

Candidate `2b536516068f9e946572d165636211a24a93638d`. Reviewed2026-10-13 by fresh separate Codex validator `/root/rem006_fresh_full_validator`; concrete model deployment/version was not exposed. This validator did not build or remediate the product. Review mode: read-only REM-MCP-UP-006 delta, followed by complete original MCP-UP-05/CD-MCP-UP-005 work-unit review.

All four original findings are resolved within the independently exercised bounds. Full-unit review found **VAL-UP05-005**, a medium-severity violation of mandatory standard-header error grammar. Passing the construction profile does not override it. No source/control/board repair, completion, acceptance, commit, push, install/sync, provider access or publication occurred.

## Frozen authority and scope

Remediation range: `b57c25d9fc4933059f64ed836783291f5753b9a8..2b536516068f9e946572d165636211a24a93638d`; correction product commit `e284ebaf1ec4b596c8e3edb9511a7012c6dfa133`. Original full-unit range: `f876603c74d8a90639fb5dc90d287d17ab523705..2b536516068f9e946572d165636211a24a93638d`. Product diffs are retained in `remediation.diff` and `full-unit.diff`.

AGENTS and engineering/lifecycle/independent-validation policies, exact request/authority/profile, approved CD005, AMEND001/002 receipts/manifests, original contract/profile, REM006 directive and exact `approved continue` receipt were read and hash-verified. Proposed labels in immutable original controls do not override separately recorded exact approvals. Original controls/captures/reports were preserved.

All18 product paths and all12 criteria were reviewed. Exactly the six authorized remediation paths changed; the other12 original product files equal the original reviewed candidate byte-for-byte. All19 metadata,60 accepted product hashes, all current controls and19 complete primary captures match. The controlling modern schema is SHA256 `742750af0bb8c716e7030c4977c992b55d1adc4407e9e66997db5846baedc2cd`, upstream `271ecc9accafdd9b83a3c869fa67c22953b2af80`. The2025 schema is historical/other-role evidence.

`full-unit-field-clause-assessment.json` records current source/assertion references and assessment of155 declaration,337 field-reference and316 normative paragraph inventories. Builder mappings were input inventories, not conformance verdicts. Ten builder `_meta` field line references were one line early; the independent mapping preserves original offsets and exact corrected schema lines. Inactive/client/historical/OAuth duties remain separate. No blanket MCP/OAuth conformance is asserted.

## Original finding delta

| Original finding | Independent result and evidence |
| --- | --- |
| VAL-UP05-001 |32 limits1..4 × malformed/duplicate/admission/oversize × blocked drain/lock cases process cancellation before output release and settle EOF; no duplicate handler or unbounded output/dispatcher set. `test_independent_cancellation_and_eof`; required product saturation and serialized-writer cases also pass. |
| VAL-UP05-002 |16 limits1..4 × resistant drain/read/close/lock cases report incomplete shutdown, retain original generation, block start/serve, settle explicit retry and leave replacement untouched by captured old teardown. Native partial-start, resistant handler/send, stale signals/finalizers and writer serialization are covered by the full product profile. `test_independent_resistant_owner_retry_and_stale_generation`. |
| VAL-UP05-003 |4 limits1..4 cases distinguish idle from fragmented work; late fragments cannot invoke handlers and delivery cannot refresh first-byte budget. Product fragmentation/oversize/partialEOF/handler/send/parse deadline cases pass. `test_independent_idle_fragments_and_output_budget`. |
| VAL-UP05-004 |12 malformed custom parameter JSON/SSE cases plus equal/conflicting case-insensitive duplicates return fixed400/-32020 with0 handlers. Existing exact Host/Origin/Bearer/TLS/default access/privacy cases pass. `test_independent_custom_headers_exact_code`. |

Original454-entry reviewer archive (433 original reviewer entries, original manifest,20 controller closeout files) and434-entry separate-remediator archive were verified byte/hash/decoded-byte complete before and after. Original symptom probes remain unchanged and lossless. Corrected peer tests are separate new scripts; no original/candidate assertion was rewritten.

## New finding VAL-UP05-005: malformed standard header classification

Severity: **medium**. Affected: `http_policy.py:149–160,226–229`, HTTP dispatch at `http.py:225–226`. Requirements: contract lines110/120, CD005 SRV-AC-01/05/06; captured Streamable HTTP lines479–484,596–602,621–629; pinned HeaderMismatchError code at schema468.

For header/body pairs that agree but contain U+0001,DEL or literal UTF8 Unicode, Method returns404/MethodNotFound and Version returns400/UnsupportedProtocolVersion. Required malformed-header response is400/HeaderMismatch(-32020). Policy catches only CR/LF/NUL and duplicates; Method/Version are compared as bytes without the character validation already used for Name/custom values.

All six ASGI exact-code cases fail reproducibly in `test_standard_metadata_header_invalid_characters_exact_code`. Real named Friday TLS JSON and SSE both reproduce raw nonASCII wrong errors; handler starts0, terminal active0 and child exit0. Raw control/DEL requests rejected by h11 before ASGI return400/plaintext; retained evidence distinguishes this middleware behavior from application-level findings. See the `independent-live-standard-001` run and structured `findings.json` for complete observations and mitigation.

Risk is incorrect protocol classification at the HTTP security boundary. No auth bypass, handler side effect or replay was observed. Required correction is bounded full standard-value validation before RPC routing, with fixed safe400/-32020, preserved access-specific statuses, Name/custom Base64 rules and byte/duplicate/privacy limits. Add matching-body malformed standard tests and private live nonASCII tests while keeping valid unknown-method/version categories unchanged; repeat the complete profile and fresh separate review. Guide18's exact error claim must match behavior. No configuration/dependency/accepted-client change is needed or authorized by this report.

## Required profile and exact baseline comparisons

All20 EXACT requested argv ran sequentially on the unchanged frozen private candidate and fresh accepted baseline, with fresh `full-001-*` labels/HOME/TMP/checker caches. Wrapper exit0 is not treated as child success; every receipt exit is interpreted.

| Command ID | Child exit | Raw evidence |
| --- | ---: | --- |
| `board` | 0 | `checks/full-001-board/receipt.json` |
| `next` | 0 | `checks/full-001-next/receipt.json` |
| `show` | 0 | `checks/full-001-show/receipt.json` |
| `server-focused` | 0 | `checks/full-001-server-focused/receipt.json` |
| `server-http` | 0 | `checks/full-001-server-http/receipt.json` |
| `original-clients` | 0 | `checks/full-001-original-clients/receipt.json` |
| `mcp` | 0 | `checks/full-001-mcp/receipt.json` |
| `core-runtime-chat-telemetry` | 0 | `checks/full-001-core-runtime-chat-telemetry/receipt.json` |
| `root` | 0 | `checks/full-001-root/receipt.json` |
| `baseline-root` | 0 | `checks/full-001-baseline-root/receipt.json` |
| `ruff` | 0 | `checks/full-001-ruff/receipt.json` |
| `root-ruff` | 1 | `checks/full-001-root-ruff/receipt.json` |
| `baseline-root-ruff` | 1 | `checks/full-001-baseline-root-ruff/receipt.json` |
| `narrow-mypy` | 0 | `checks/full-001-narrow-mypy/receipt.json` |
| `mcp-mypy` | 0 | `checks/full-001-mcp-mypy/receipt.json` |
| `full-mypy` | 1 | `checks/full-001-full-mypy/receipt.json` |
| `baseline-full-mypy` | 1 | `checks/full-001-baseline-full-mypy/receipt.json` |
| `docs` | 0 | `checks/full-001-docs/receipt.json` |
| `render` | 0 | `checks/full-001-render/receipt.json` |
| `whitespace` | 0 | `checks/full-001-whitespace/receipt.json` |

Candidate root: **5326 passed, 14 skipped, 15 warnings in 136.49s (0:02:16)**. Fresh accepted baseline: **4744 passed, 14 skipped, 15 warnings in 117.86s (0:01:57)**. Root skip location/reason objects are exactly equal (9 grouped rows representing14 skipped tests), as are complete15-warning sections. Counts alone are not the comparison.

Changed-file Ruff and narrow/MCP Mypy pass. Root Ruff retains rawexit1 and exactly equal327 complete normalized diagnostic/fix objects. Full/base Mypy retain rawexit1 and equal4 path/line/column/severity/code/message objects, from fresh supplemental `--show-column-numbers --no-pretty` commands. `exact-profile-comparison.json`, paired normalized-object files and raw stdout/stderr retain the full comparison.

Independent ASGI probes:64 pass,6 mandatory standard-header negatives fail. Independent verifiedTLS standard-header probe:2 failing parameterized tests, complete raw observations,0 handlers and child exit0. The raw original ASGI and live probe runs are retained. These semantic failures are the finding, not inherited checker debt.

## All12 criteria

| Criterion | Assessment | Evidence groups |
| --- | --- | --- |
| SRV-AC-01 | CHANGES_REQUESTED | envelope, metadata, version, unsupported, notification |
| SRV-AC-02 | supported by current source and fresh evidence | catalog, tooldefinition |
| SRV-AC-03 | supported by current source and fresh evidence | tooldefinition, toolcall |
| SRV-AC-04 | supported by current source and fresh evidence | stdio, notification |
| SRV-AC-05 | CHANGES_REQUESTED | version, http, headers |
| SRV-AC-06 | CHANGES_REQUESTED | headers, access |
| SRV-AC-07 | supported by current source and fresh evidence | stdio, ownership |
| SRV-AC-08 | supported by current source and fresh evidence | registry |
| SRV-AC-09 | supported by current source and fresh evidence | unsupported, compatibility |
| SRV-AC-10 | supported by current source and fresh evidence | metadata, observation |
| SRV-AC-11 | supported by current source and fresh evidence | version, interop |
| SRV-AC-12 | independent gate not passed; other checks/docs/scope supported | scope/checks/guide/integrity |

## Integrity, isolation and context exceptions

Complete library snapshots bracket the FIRST and LAST decisive required/supplemental commands: before `2026-10-13T20:57:39.484453+00:00`, first `2026-10-13T20:57:58.035617+00:00`, last `2026-10-13T21:17:07.011969+00:00`, after `2026-10-13T21:19:37.092420+00:00`. Both actual-hash inventories retain **22,009 inventory references /21,992 unique paths /192 distributions**, including17 overlap references; every expected hash matches and before/after inventories are identical. Inputs are copied reused-library-manifest.json plus additional-validation-libraries.json. This is count representation, not missing libraries or changed dependencies. Python3.13.10 and SDK/mcp-types2.3.0 were reused without installation.

Original runner UP05 SHA `e302adaef56d824be9ee962ee6c648624330f0d0d6aa1c992f5b0dbeced8e017`, original run_check.py SHA `ceec1b2316f4be3bce36fb778eb80b5d472561920d6d6fe35b8b30735e1776f0` and guard SHA `38f6a7483d66a066336d63c14980f1acfe307ec38848f0761c6928a66989a7a8` remain unchanged. The private runner diff changes only output/HOME/TMP/cache destinations; source scope/guard/allowlisted environment/checker defaults remain unchanged.

The initial borrowed private-checkout root profile wrote two ignored relative fixture artifacts (`.friday/chroma/chroma.sqlite3` and an experiment audit JSON) outside the reviewer's directory. These are explicitly retained approved synthetic private broad/root regression effects under the frozen profile and unchanged guard, not shared user stores or governed tracked changes. They were disclosed, preserved and not cleaned. All-runtime equality is not required; governed tracked source/control/product equality is the candidate-stability boundary. Extra private no-checkout clones were prepared with protected sparse omissions installed BEFORE checkout, and a duplicate profile began before this authority interpretation was clarified. The controller instructed stopping that unnecessary extra run; its8 completed receipts and interrupted root output are retained as contextual evidence, never substituted for the completed required20 or represented as candidate failures. No duplicate full-profile conclusion is claimed. Original candidate HEAD/status and governed tracked products/controls/metadata remain unchanged; generated runtime stores/keys are excluded from the archive.

Preflight unique/reference count, grouped skip-row count and builder field-line-offset checks initially raised reviewer-script assertions. Raw observations/initial artifacts are retained and explained in `review-setup-observations.json`; they are not candidate findings, and no test/checker was weakened. Initial policy/memory lookup used the shared root read-only; product/control review used the frozen private candidate. No inherited user credential/cache/store destination, provider, public DNS/network or live deployment was used. Only approved guarded synthetic stdio/ASGI and literal127 ephemeral verifiedTLS fixtures ran.

Residual risk: cooperative Python cancellation remains required; resistant work stays honestly owned and restart is blocked in the exercised limits. Excluded optional/OAuth roles and other workloads were not validated as implemented features. Original proposed closeout labels remain historical. A corrected candidate must receive a new independent result. This report establishes neither VERIFIED, completion, acceptance nor publication.

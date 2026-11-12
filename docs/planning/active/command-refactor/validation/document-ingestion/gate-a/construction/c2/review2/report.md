VERIFIED

Fresh read-only corrected implementation validation — INGEST-C2-VAL-001 delta FIRST, followed by FULL bounded C0/C1/C2 aggregate, CD-01–08.

Reviewer: OpenAI Codex fresh task-only subagent /root/ingest_c2_corrected_validation. Exact model/version is not exposed in this agent context. Review date UTC: 2026-11-12T15:27:24.311817+00:00. Repository: /Users/chuckrussell/Dev/gendev/agent-framework. Private evidence root: /private/tmp/ingest-c2-corrected-review-bAnS5rvE. No nested agents, repairs, repository writes, staging, commits, delivery or new profile activation.

Candidate3985edc21474a86fce0bb29794ff52315c12ad5c; base73fbda9b7f4e90da9912be442e1eb05b494a13b5; exact range 73fbda9b7f4e90da9912be442e1eb05b494a13b5..3985edc21474a86fce0bb29794ff52315c12ad5c. Correction range 120def192117d6ed53fe10fa2ec3728c0e56ea7b..3985edc21474a86fce0bb29794ff52315c12ad5c. Actual unfixed source120def192117d6ed53fe10fa2ec3728c0e56ea7b. Approved selected source8cb32e314860825f6d521e97306e7c8e1a100f70, tree0bd4734795a12c375ab1646f131f305cb713cb40. Every29 selected candidate blob/hash equals that source manifest; own manifest SHA256f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843. Actual-unfixed export manifest SHA256c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a.

The external request was SHA256-verified before its first read:077a99965833e7225077fbb46090a946fd9a576d8e996087086bfce8f56e3ac2. Boundary SHA256112fa2bebc354dc22ffec7a2e50b2f427d44701004143a9c37affe14367d160d verified before its read. AGENTS.md and all three policies, the exact directive, current C0/C1/C2 scopes, continuation, private-tool approvals/profiles and named remediation were inspected. Current authority is validation/in_review on feature/cmd-ingest-001; board remains started/normal, implementation_authority granted, delivery local. The pinned C1 continuation supplies offline test-only construction authority despite older unactivated wording retained in the parent draft directive; actual stage effects remain unactivated.

**Numbered findings and named correction**

No new mandatory or advisory finding. INGEST-C2-VAL-001 is closed for this candidate: both reported malformed declarations (py3--any and py3-none-) return CONSISTENT_CANDIDATE_DECLARATIONS from actual unfixed source, producing two genuine unittest.assertRaises call-assertion failures per mode. The four delta commands run first: unfixed normal/-O each exit1 with setup_succeeded=true and2 Refusal-not-raised witnesses; corrected normal/-O each exit0 with2 actual Refusals. The corrected source validates target syntax before optional imports and checks every expanded wheel tag. Independent wheel-only cases retain a valid target and refuse all12 malformed wheel tags at Malformed selected wheel tag. Valid universal/native and compressed interpreter/ABI/platform groups still succeed. No setup/import/collection error is counted as a negative witness.

**CD-01–08 matrix**

| Criterion | Outcome | Current evidence |
| --- | --- | --- |
| CD-01 | PASS | setup.json; candidate-paths.json; correction-source.diff; aggregate-source.diff; opening.json/closing.json. All20 authority pins match. Exact82 changed paths match request; executable delta is only manifests.py and its existing test module, plus README. C1 evidence unchanged; all55 prior and54 base test bodies identical. |
| CD-02 | PASS | manifests.py:139-181; minimal-normal/optimized and independent-normal/optimized. Exact schema/environment fields, count/type checks and nonempty tag component/member grammar. The minimal test_empty_target_tag_components_refuse_before_parser_import executes with no optional parser import. |
| CD-03 | PASS | selector-normal/optimized:6 positives each; independent-normal/optimized:9 positives each. Verified packaging24.2 origins only; versions, specifiers, normalized identities, base+extras, inactive platform marker, cycles, late extras, universal/native/compressed tags and prerelease behavior. |
| CD-04 | PASS | selector-normal/optimized:39 actual Refusal cases each. Independent43 actual Refusal cases each, including24 malformed target/wheel variants; all12 malformed-wheel-only cases reach Malformed selected wheel tag. Missing/conflicting/unreachable dependencies, unknown extras, bad Python/platform/host/direct-reference/yanked/size controls also exercised. |
| CD-05 | PASS | manifests.py:147-170,209-213,277-304,319-339; independent count/byte/requirement limits and retained selector. Explicit64 roots/512 wheels/2048 tags/256 requires-dist per wheel/8192 declarations and expansion/32 requested extras/64 provided extras/4GiB selected bytes. Checker performs declaration checks only; all qualification/execution flags false. No actual resolver/download/install adapter is called. |
| CD-06 | PASS | setup.json AST retention54base/55prior/56current; minimal-normal/optimized stdout+stderr:56 executed,0 failures,0 skipped; selector-normal/optimized:6positive39refusal with exact parser inventory and all imported packaging origins private. |
| CD-07 | PASS | ruff-check-corrected-command exit0; ruff-format exit0; mypy exit0 with Success: no issues found in25 source files. Exact root config hash; no suppression/cast matches in harness; private copied typing1177/parser23 files and RECORD audit. Packaging exposed only as private PEP561 package_path; fresh cache, no ambient site or upstream/root-rule/source edits. |
| CD-08 | PASS | Stable candidate3985edc2; correction delta completed before aggregate execution. Manual two-mode frozen flow, required repository administration and whitespace checks;292 indexed gzip/raw digest pairs pass. opening/closing identical; no candidate/supplied writes. All actual A0-A4, full HR,9.5 advancement, acceptance and delivery remain open. |

**Full bounded retained C0 matrix**

| Criterion | Outcome | Current evidence |
| --- | --- | --- |
| CC-01 | PASS | All20pins and full boundary preserved; test-only82-path exact range; setup.json and integrity.json. |
| CC-02 | PASS | Pinned base CPython3.13.10 bootstrap identity and mandatory -I/-S/-B flags;56 tests per mode include dirty/extra/pyc/swap and private armed site-canary controls. test_startup.py. |
| CC-03 | PASS | Strict JSON/config/path tests, empty owned selftest scratch, no-write preflight and new-only init; test_manifests.py,test_paths.py,test_cli.py and two manual flows. |
| CC-04 | PASS | Current test_ledger.py exercises immutable identities, canonical chain/order/tamper/stale tips, candidate/promotion ordering, concurrent writer, cumulative reservations and terminal stop; both modes pass. |
| CC-05 | PASS | test_export.py actual private fixture repository commit/blob export excludes poisoned dirty/untracked input and retains private source index. Both modes pass. Reviewer export independently verifies every selected candidate/unfixed blob. |
| CC-06 | PASS | test_protection.py and test_startup.py execute guarded discovery, owned positive and read/probe/write/descriptor/dir-fd/thread/socket refusals, separate fake native metadata-detection failure, missing/truncated coverage. Both modes pass; OS containment is not claimed. |
| CC-07 | PASS | test_environment.py and child positive/negative in test_startup.py: explicit allowlisted settings, fake credentials/proxies/Python discovery dropped, startup inventory. No real SDK/profile is qualified. |
| CC-08 | PASS | test_window.py fake loaded-state/route/expiry/revocation/model/input/vector/token/request controls; callbacks changing stop/expiry before handoff refuse with conservative charges; accepted fake in-flight boundary remains documented. Both modes pass; no HTTP transport. |
| CC-09 | PASS | Two public manual flows and retained CLI/report/fixture cases. PREPARED_INPUTS is input preparation only; all/allA0-A4/prepare-model exit3, reports INCOMPLETE exit3, terminal stop prevents resumed effects. Structural seeds/ZIP controls pass. |
| CC-10 | PASS | Focused private root-rule lint/format/type checks pass;56 current control tests normal/-O. Fresh current-source aggregate assessed independently, with the context exception disclosed below. |

**Full bounded retained C1 matrix**

| Criterion | Outcome | Current evidence |
| --- | --- | --- |
| CI-01 | PASS | Exact directive/continuation pins, no C1 evidence changes and complete opening/closing boundary. All candidate inputs frozen. |
| CI-02 | PASS | test_fixtures.py checks deterministic unique6PDF/6DOCX/10XLSX/8PPTX containers; PDF offsets/pages/image/encryption and Office structures. Independently hashed manual30files in each mode;50583bytes,0444 inputs, identical manifest/oracles. |
| CI-03 | PASS | Current fixtures/expectations.json contains30 literal marker/exclusion/unit/outcome oracles. publish_matrix binds that file; no converter output or real extraction is used to derive it. Independent oracle hash85f6bffd0b2f9d79c2c62b60e6b3a150c7d0fde7cec3adfa8a842e220a367a23. |
| CI-04 | PASS | Current audit_office and test_fixtures.py: hidden units/rows/columns/shapes, formula cache and external relation distinctions; ZIP/XML/coordinate/merged bounds and UTF16 entity refusal. Output remains structural facts, text_extracted false. |
| CI-05 | PASS | Current publish_matrix/verify_matrix and retained actual-call tests: new physical destination, complete oracle before writes, exclusive/read-only publication, wrong hashes/extra or alias refusal and stopped partial publication without ready manifest. |
| CI-06 | PASS | test_operation_append_requires_live_same_instance_writer_lease executes same-instance/process token, stale/foreign/released token and competing writer checks; current append_held validates token and PID. |
| CI-07 | PASS | Public frozen entry preflight/init/prepare-fixtures/report/stop exercised in normal/-O; independent hashes and read-only mode checked. Reports label receipts ledger witnesses, not current-byte/conversion proof; no promotion or upstream execution. |
| CI-08 | PASS | All54base and55prior test bodies unchanged, including original controls;56 current cases execute per mode without skips under verified-buffer loader. |
| CI-09 | PASS | Ruff/format/25-source mypy and board/dashboard/docs/metadata/owned whitespace pass using required private tools/admin exception. Existing working-tree YAML whitespace failure remains unwaived. |
| CI-10 | PASS | Stable candidate, exact29-blob source export and fresh read-only aggregate. This report distinguishes fresh execution, source inspection and integrity-only supplied receipts; no old review result is adopted. |

**Executed evidence, tools and administration**

Fresh execution:56 minimal cases per normal/-O lane (no failures/skips); explicit current selector6 positives/39 Refusals per lane; reviewer-authored9 positives/43 Refusals per lane. The latter independently covers additive base/extras, an inactive marker, a cycle, late extra expansion, version conflicts, missing/unreachable closure, unknown extras, direct references, Python/platform constraints, count/requirement/size/host/yanked/schema controls and no qualification overclaim. The source-inspected8192 graph limits and remaining parser semantics are assessed with the current retained selector; this review does not claim exhaustive parsing or resource-stress proof.

Every typing1177 and parser23 file was copied by verified inventory into this review root and rehashed, with no symlinks or startup hooks. Fresh RECORD verification covers all1172 hashed typing members plus each of5 RECORD self entries, and22 hashed parser members plus its RECORD self entry; license files and packaging/py.typed are present. Ruff executable SHA2563844f53974c6e6d52dcfccdc02e9b34188c5003f0060ad2f3a96b9d550eea6f5, exact root config SHA256d1e8ff05afbe8f1a06d3ddaa07db520ff0a1378f6fae23baf3ee525b9619e9d7, interpreter SHA256e2adf1814122d8b26166917ef7d294d7426963e0f59e28d0d5aef773f67c4bb0. Source/static/runtime lanes use only the pinned base interpreter with -I -S -B, plus -O where stated; all imported packaging modules originate in the private copied parser target.

The inspected supplied mypy launcher was copied into private scratch; its private paths derive from __file__. It leaves upstream source/root rules unchanged, removes ambient mypy library search and explicitly binds the private parser as a PEP561 package_path. MYPYPATH names the private static-source root. All25 exact Python source files are checked using a newly created private cache. Mypy logged denied optional CPython setup/locale probes and the one private PEP561 path; these are disclosed guarded refusals, not semantic rejection credit or a fallback. Final mypy exit0: Success: no issues found in25 source files. No source/library suppression, root-rule alteration or ambient site is used.

Separate administration uses only existing uv selectors with --offline --frozen --no-sync --no-python-downloads --no-env-file python -B, unchanged HOME, bytecode off, GIT_OPTIONAL_LOCKS=0 and owned UV/XDG/TMP/config/credentials paths. This is the explicit request exception for repository maintenance, including its yaml dependency; it is not a harness/static .venv fallback. Source inspection of the three maintenance scripts shows no Friday application imports. Board validate passes36 tasks; render --check is current; documentation lifecycle passes1097 Markdown files; package metadata passes18 pyproject.toml files. Owned/cached/range whitespace checks exit0. Full working-tree diff --check retains exit2 solely from the preserved dirty chat YAML whitespace; no waiver or whole-repository-green claim follows.

Reviewer command-setup mistakes were corrected only in owned scratch: snapshot enumeration initially met a Gitlink directory (IsADirectoryError, exit1), then excluded that Gitlink from the regular-file boundary as the supplied boundary does; the logical index binds it. The first export setup compared the subtree ID against a manifest containing the approved source commit root-tree ID (exit1), then verified the correct source-root tree and identical candidate blobs. Initial Ruff argv combined --isolated and --config and was refused by Ruff (exit2); the corrected explicit --config/no-cache invocation passes without changing root rules. The first evidence audit also assumed readable historical siblings must equal their gzip originals (exit1); the final audit separates exact indexed raw/gzip identity from distinct readable wrappers and verifies the current C2 trailing-blank normalization. None of these infrastructure failures supplies product rejection credit. All runtime/assertion/static/admin invocations and any unexpected initial exit are retained in commands.jsonl with exact argv, cwd, allowlisted environment (HOME preserved without its value), stdout/stderr paths, digests and exits.

**Inspected receipts and integrity**

Supplied approval/profile/inventory documents and operational launchers were inspected as inputs; previous build/review success claims were not reused. Embedded receipts are integrity-only:292 indexed compressed/raw SHA256 pairs all match across C0/C1/C2, including historical evidence. The three readable historical report siblings are distinct representations; no report content/verdict was read for correctness. The current C2 readable normalization hashes match its normalization receipt and differ from original gzip raw bytes only by trailing blank lines. The two C0 readable wrappers already differ in the unchanged baseline; their archived gzip originals match their declared raw hashes. This is not a claim that every readable sibling equals its raw archive.

opening.json and closing.json are byte-identical, SHA2565d52f0b6a00b0503ea8351c771f5f5e8bbfb5f3aaec769f371138aba50301bd9. HEAD, branch, logical index before status, exact dirty status,18391 regular tracked-file hashes,26 symlink targets, all20 pins,9 protected metadata records and1210 supplied file hash/metadata records are unchanged. Logical index SHA256902349b6d0628c9ad97cf54fbf3d2cfc2758d6bf0904b5491d5c5d9f50c0ac5c. Protected .friday/.friday-old/.venv metadata was checked without traversal; dirty YAMLs were hashed without payload inspection; live .friday_test remains absent. Candidate/unfixed exports, private tool copies and root config rehash correctly. The terminal integrity check runs again after this report is written, producing terminal-integrity.json with this report SHA256.

**Independence and shared-context disclosure**

No memory files, C2 review1 report/verdict, peer test logic or private builder reasoning were read or used. One attempted shallow current-authority extraction inadvertently printed unrelated historical pilot/foundation authority fields, including unrelated historical result labels, before truncation. The controller was notified immediately. Those labels supplied no correctness evidence; remaining authority extraction used explicit current INGEST fields only. Historical report bytes were processed only mechanically for hashes/normalization and never displayed or semantically relied upon. The exposure does not supply a prior verdict for this candidate and does not compromise the task-only implementation independence under the governing policy. This exception is explicit so the controller/maintainer can assess it.

**Limits and advisory score**

Advisory score:9.3/10 for this bounded offline component, not a full-readiness score. The named defect is reproduced and corrected under both modes, retained controls execute, and independent call assertions support the declaration checker. Remaining real profiles/adapters, native containment and broader source/runtime qualification keep full HR-01–18, A0–A4 and any9.5 advancement open. This result supplies no actual dependency resolution, metadata collection, download/install, artifact-byte/license/installed-profile provenance qualification, Docling/OCR/extraction/chunk/model/tokenizer acceptance, target-machine fact verification, production/store/provider/network effect, UAT, maintainer acceptance or delivery authority. Python-visible guard evidence has declared native/child/detective limits and is not OS containment. Full repository debt and preserved YAML whitespace remain unwaived. No new profile has been activated.

**Reproducible command ledger**

Initial external verification command, exit0:
```sh
shasum -a 256 /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-build-uk9g_iz6/corrected-review-request.json
```
Boundary verification and initial logical-index command both exit0:
```sh
shasum -a 256 /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c2-build-uk9g_iz6/corrected-review-boundary.json
GIT_OPTIONAL_LOCKS=0 git ls-files -s -z | shasum -a 256
```
Owned setup/integrity helper invocations (run_checks.py exits1 as disclosed below; final other helper invocations exit0):
```sh
/usr/bin/python3 -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/snapshot.py opening
/usr/bin/python3 -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/setup.py
/usr/bin/python3 -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/commands.py
/usr/bin/python3 -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/run_checks.py
/usr/bin/python3 -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static_checks.py
/usr/bin/python3 -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/admin.py
/usr/bin/python3 -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/audit_evidence.py
/usr/bin/python3 -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/tool_audit.py
/usr/bin/python3 -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/snapshot.py closing
```
run_checks.py completed all semantic/manual lanes, then exited1 on the initial invalid Ruff argv; static_checks.py completed the corrected static lane. Commands below are recorded individually and authoritative for result/exit:

delta-unfixed-normal — exit1; expected1; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/selection_worker.py unfixed witness
```
stdout SHA256ac17c00af1caee303615934dfb94795ca7380149799421dd01b42bd47f7b461b; stderr SHA2563f80572913596b629972fa5e27c1784dde1b52311148932f0f0972c16b1d5003.

delta-unfixed-optimized — exit1; expected1; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/selection_worker.py unfixed witness
```
stdout SHA2566ab71912920495a2e46c92c19a50e9eb971fe597850803a5bed476470ff2371e; stderr SHA2563f80572913596b629972fa5e27c1784dde1b52311148932f0f0972c16b1d5003.

delta-candidate-normal — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/selection_worker.py candidate witness
```
stdout SHA256df24c9bb84cc7325caa33aba1975ccece103419d631cec3187a6026874bd79a0; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

delta-candidate-optimized — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/selection_worker.py candidate witness
```
stdout SHA256c20c3355b50e583050b479ee2a93cf059f060ecde5ff3f0346c1b33c5247e2f7; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

independent-normal — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/selection_worker.py candidate independent
```
stdout SHA256807b9b4b854862417b0c49afcf7527f8efb2775628e34550e32d7f4de089ed87; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

selector-normal — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/selection_worker.py candidate selector
```
stdout SHA25648fd4604333cd40df96498193a0a05c460bb297e180392e0fad47b333a65b8ca; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

minimal-normal — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate/bootstrap.py selftest --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --scratch /private/tmp/ingest-c2-corrected-review-bAnS5rvE/selftest-normal --profile minimal
```
stdout SHA2563355208e1e28e5e262fe48fcc401963b8f06663a220e772681571544712561d7; stderr SHA256590fe79478d3d7e8bc6060b21095f117f27dbb26e0ab954c2b38013d9dada67a.

preflight-normal — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate/bootstrap.py preflight --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/control-normal.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA256c42ff291c5025a220694513b117a429f20e07801545102753aeebdb36bfa7c0c; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

init-normal — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate/bootstrap.py init --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/control-normal.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA25658b8b9fff50ae5de17b1746c4d66e0a81ec76f6b599ed6b4e8076e2ffb1ba7b4; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

prepare-fixtures-normal — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/harness/run.py prepare-fixtures --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/control.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA256b02c9484451a88064084f7c94cc73e59e285301249a3d4f715a3ce8d7b415681; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

blocked-all-normal — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/harness/run.py run --stage all --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/control.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA2563bfee0a2ba970ee3b94254a0706f473d93645b6b73a61c61368f00427f9d8160; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

blocked-A0-normal — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/harness/run.py run --stage A0 --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/control.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA256ba4bf7ee76f56b64b2c4fe876a71c9eaf13c4e306f9db6bb84aae4547762c53b; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

blocked-A1-normal — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/harness/run.py run --stage A1 --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/control.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA2563ae3bb2f2cead5ddeceb721aa6ef3e1b7b4404ff307331767055c9ad80892dc5; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

blocked-A2-normal — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/harness/run.py run --stage A2 --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/control.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA256a5af0503b6c83f54970f62821ae928a42d0c2042276513b9fb04a36056e7f3c0; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

blocked-A3-normal — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/harness/run.py run --stage A3 --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/control.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA2569229d8d250602aa127f1ef9512a2fb9477c1132e1992fc130ad5473a6a1946a2; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

blocked-A4-normal — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/harness/run.py run --stage A4 --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/control.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA2560c59c86950ca43d613e7428cab747d6a9ebeb108f8f5280925bc7a8583a9b420; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

prepare-model-blocked-normal — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/harness/run.py prepare-model --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/control.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA256aff6e10ffd70b72bd3a191d92ac72cb86431d4748d0c56fc213760df3a25c7ab; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

report-normal — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/harness/run.py report --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/control.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA256668668470029123bcac29d494548af5cc83a53f08d96238aae9793e9de55dd88; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

stop-normal — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/harness/run.py stop --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/control.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA2569f8114b9da37910d930c2d2f1be480a346620146bb279cd1113cc141730a2268; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

run-after-stop-normal — exit2; expected2; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/harness/run.py run --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/control.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; stderr SHA256a423a00e9452f5d8bf39fcbccd7ed26f2f910b08ff1559af2185c55e68982b3f.

report-after-stop-normal — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/harness/run.py report --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-normal/.friday_test/runs/review/config/control.json --config-sha256 636b1d7d82294413fb1cfb8205c11381736a57b762b1f6e6486d237b5073943a
```
stdout SHA2565873206230e190d4dc3305548b1b3ed6d6c35ea8284fb6eb19c6a5137a9b9904; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

independent-optimized — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/selection_worker.py candidate independent
```
stdout SHA2562d5518d4495a0cab05dabb1042ba0683e875074c5d40bf11ccfe128de915c599; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

selector-optimized — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/selection_worker.py candidate selector
```
stdout SHA256d410bd5e1ee48e1a23b8a9bdfedf2b617390fa2fa3161acebab28e5b3342010f; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

minimal-optimized — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate/bootstrap.py selftest --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --scratch /private/tmp/ingest-c2-corrected-review-bAnS5rvE/selftest-optimized --profile minimal
```
stdout SHA2567b02c4005a3cf0c9de5d8b7c5fb0cb6330f29e052e8b04bb52896c7e0945b7d2; stderr SHA256038a5b60585ecaec62b9218696c102e62f008008dc5746a7b2921db26a4f0075.

preflight-optimized — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate/bootstrap.py preflight --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/control-optimized.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA2569c767bc99547b438d45342f600ca5aa32e3d3f8e803f7eb7478b7c755befaebb; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

init-optimized — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate/bootstrap.py init --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/control-optimized.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA25680f129889f8ffe5a4f9039e4d5315a28dcbad2bcf6ec8d27b99abc29bdb5d9fa; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

prepare-fixtures-optimized — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/harness/run.py prepare-fixtures --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/control.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA256647690c64f1ee5200d365fe6b7a60014e1c06ae1b296493f9d4b574c3647a276; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

blocked-all-optimized — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/harness/run.py run --stage all --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/control.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA25690643bacd984125db9ca62829bc09c6174a5fb1041e8860755307db4118cf95c; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

blocked-A0-optimized — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/harness/run.py run --stage A0 --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/control.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA2569984cc0129baf5bebc0a9d355925db82fd1281f81eda501a13b614cf91958d31; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

blocked-A1-optimized — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/harness/run.py run --stage A1 --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/control.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA256afb1acfe8c1ab75f103c02127f1d63c840e67982d0ebf9115201257e58d33343; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

blocked-A2-optimized — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/harness/run.py run --stage A2 --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/control.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA25698dc556f6ed25fc5e4e6ce4047b0aac48d31c1b6ab03e02c7f50fc73840ee9ce; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

blocked-A3-optimized — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/harness/run.py run --stage A3 --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/control.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA256b60cce254f3f4f79279e8a3a2ee239b2bb07f9166527db3d139407de4a28c6bd; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

blocked-A4-optimized — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/harness/run.py run --stage A4 --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/control.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA256a1952fe4a7465b122c1db4e82d5b2d1b9aee79dcb6ba02cdbb68ab936a6339c7; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

prepare-model-blocked-optimized — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/harness/run.py prepare-model --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/control.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA256e46debccaa20bc2f19e52962a2b0857ef288ae7e97420a62fb3cb6983ca4e7ff; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

report-optimized — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/harness/run.py report --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/control.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA2562dfa7ac0a8d280e933d4fd04d6ab93b7006f9af743eb479d366992ce67ea3dab; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

stop-optimized — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/harness/run.py stop --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/control.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA2569f8114b9da37910d930c2d2f1be480a346620146bb279cd1113cc141730a2268; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

run-after-stop-optimized — exit2; expected2; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/harness/run.py run --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/control.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; stderr SHA256a423a00e9452f5d8bf39fcbccd7ed26f2f910b08ff1559af2185c55e68982b3f.

report-after-stop-optimized — exit3; expected3; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B -O /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/harness/run.py report --harness-manifest /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/harness-manifest.json --harness-manifest-sha256 f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/manual-optimized/.friday_test/runs/review/config/control.json --config-sha256 9d411adbb9937b9091a1832771664052eb1d8ec992454114489b494865ed6b9c
```
stdout SHA25658f800ea1f6d2da92b6d0e4e0a2d2e1bbb2eee326cb5c89dfe9c61f60fd9e1d3; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

ruff-check — exit2; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/private/tmp/ingest-c2-corrected-review-bAnS5rvE/validation-tools/ruff check --isolated --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/validation-tools/pyproject.toml --no-cache /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest
```
stdout SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; stderr SHA256c8e4dbc505e00fb2ce1fed1e428d6e30e1cd3f651a1085fbe4af2c403c191202.

ruff-check-corrected-command — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/private/tmp/ingest-c2-corrected-review-bAnS5rvE/validation-tools/ruff check --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/validation-tools/pyproject.toml --no-cache /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest
```
stdout SHA25682b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

ruff-format — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/private/tmp/ingest-c2-corrected-review-bAnS5rvE/validation-tools/ruff format --config /private/tmp/ingest-c2-corrected-review-bAnS5rvE/validation-tools/pyproject.toml --no-cache --check /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest
```
stdout SHA2567715b02781372f8741fb309aee97a6483e689c9039f0d78081dd910f70b0256e; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

mypy — exit0; expected0; cwd /private/tmp/ingest-c2-corrected-review-bAnS5rvE.
```sh
/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13 -I -S -B /private/tmp/ingest-c2-corrected-review-bAnS5rvE/run_private_mypy.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/validation-tools/mypy-target /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate /private/tmp/ingest-c2-corrected-review-bAnS5rvE/candidate-manifest.json f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843 70e03f2215282e2d4aa6fd0a58161ce0b9858981a114caba49f4826f5833599c --config-file /private/tmp/ingest-c2-corrected-review-bAnS5rvE/validation-tools/pyproject.toml --no-site-packages --namespace-packages --explicit-package-bases --cache-dir /private/tmp/ingest-c2-corrected-review-bAnS5rvE/validation-tools/mypy-cache /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/bootstrap.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/config.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/environment.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/export.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/fixtures.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/ledger.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/manifests.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/paths.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/protection.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/reports.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/run.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/stages.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/startup.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/tests/test_cli.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/tests/test_environment.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/tests/test_export.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/tests/test_fixtures.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/tests/test_ledger.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/tests/test_manifests.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/tests/test_paths.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/tests/test_protection.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/tests/test_reports.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/tests/test_startup.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/tests/test_window.py /private/tmp/ingest-c2-corrected-review-bAnS5rvE/static-source/ingest/window.py
```
stdout SHA256521e53066a363ec69a3862127d20de642114463485e6923ba593c38250537f8d; stderr SHA256cd989e3e0dd61fa7fe32ff956a1da16d62ef5e2c14b6e50fc50b4ce90f804ff6.

board-validate — exit0; expected0; cwd /Users/chuckrussell/Dev/gendev/agent-framework.
```sh
uv run --offline --frozen --no-sync --no-python-downloads --no-env-file python -B scripts/friday-dev-board.py validate
```
stdout SHA256c4d2aec671b8fd5d5a978b1c191b186f6d151f7ace4785fbd74b06c3c5f3fdae; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

board-render-check — exit0; expected0; cwd /Users/chuckrussell/Dev/gendev/agent-framework.
```sh
uv run --offline --frozen --no-sync --no-python-downloads --no-env-file python -B scripts/friday-dev-board.py render --check
```
stdout SHA256a28df31135633728c76b88ed1a836e90f2c8046e1d72663c8881937c7693ba33; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

board-show — exit0; expected0; cwd /Users/chuckrussell/Dev/gendev/agent-framework.
```sh
uv run --offline --frozen --no-sync --no-python-downloads --no-env-file python -B scripts/friday-dev-board.py show friday-command-refactor
```
stdout SHA25646d0b1d1e9e2c31f604d93379003d63e12129c8ce137165ada08318a6308b27b; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

docs-lifecycle — exit0; expected0; cwd /Users/chuckrussell/Dev/gendev/agent-framework.
```sh
uv run --offline --frozen --no-sync --no-python-downloads --no-env-file python -B scripts/check-documentation-lifecycle.py
```
stdout SHA2563d251169dc785521a9fc96df6a4b06728e71bdb459eab9837e3fa5e819b615dc; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

package-metadata — exit0; expected0; cwd /Users/chuckrussell/Dev/gendev/agent-framework.
```sh
uv run --offline --frozen --no-sync --no-python-downloads --no-env-file python -B scripts/check-package-metadata.py
```
stdout SHA256b755228d64e991cad2a40d1ea238ea00e97d8d2fd420a5141fffa00476ed690f; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

whitespace-owned — exit0; expected0; cwd /Users/chuckrussell/Dev/gendev/agent-framework.
```sh
git diff --check -- tests/readiness/ingest docs/planning
```
stdout SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

whitespace-cached — exit0; expected0; cwd /Users/chuckrussell/Dev/gendev/agent-framework.
```sh
git diff --cached --check
```
stdout SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

whitespace-range — exit0; expected0; cwd /Users/chuckrussell/Dev/gendev/agent-framework.
```sh
git diff --check 73fbda9b7f4e90da9912be442e1eb05b494a13b5..3985edc21474a86fce0bb29794ff52315c12ad5c
```
stdout SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

whitespace-working-baseline — exit2; expected2; cwd /Users/chuckrussell/Dev/gendev/agent-framework.
```sh
git diff --check
```
stdout SHA2562d96c7153fcaa4d254bff546bf5fa277d29b30d5be1bb319363765e342937f22; stderr SHA256e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

**Evidence artifacts**

- [setup.json](evidence/setup.json.gz), SHA256141184499cc278d29113e0aaf0b3f2c15f781bccd1354c2ecff3f7c793ef0323.
- [candidate-manifest.json](evidence/candidate-manifest.json.gz), SHA256f4d0e22c089d839780e60cd2ab543257db2e300ccfb1bebfdd6b065c53687843.
- [unfixed-manifest.json](evidence/unfixed-manifest.json.gz), SHA256c9197333b7b124b73fe086a759a9e25d909d6814e4b85cb1b16287a8975a305a.
- [candidate-paths.json](evidence/candidate-paths.json.gz), SHA2568b2c9b23f1afd8f332e7d195b3726a40df3796d492365918d3d1c9511f666cca.
- [correction-source.diff](evidence/correction-source.diff.gz), SHA2563be8c716e17ca71b6d0b14848540de1d665f0d328092bc00d312bd3d6299dd1e.
- [aggregate-source.diff](evidence/aggregate-source.diff.gz), SHA256feffbebffcc8cad4fcd66d304d42bbee6ca9ff1b7f07cb3ac39d458ea678bfad.
- [selection_worker.py](evidence/selection_worker.py.gz), SHA256348516dcd0182300eb14c5e61fd886cb7b4029cbeb985efd38d700e0874036f6.
- [commands.jsonl](evidence/commands.jsonl.gz), SHA256c0bc1931ab27f30b9e67f55e0b73382aac055f08490cc9745d74a689d86e0a97.
- [current-authority.json](evidence/current-authority.json.gz), SHA256a968d78bdc910c5e7ec2bd3fdae0dd380896ec892b6642102a9f82817e7c299d.
- [manual-summary.json](evidence/manual-summary.json.gz), SHA256b7169725c5d0fe4867a5ebe7584d3d58a64ee4ba2b09e17ef9584d9a4e580f1d.
- [independent-manual-matrix.json](evidence/independent-manual-matrix.json.gz), SHA2565a71c61ce7375857378941117c4ee05c4fc1be86c15acda45f45bcbd9923bf73.
- [tool-origin-record-audit.json](evidence/tool-origin-record-audit.json.gz), SHA256865eac5a0444f8f0c03aa20d435780c09a9e6a366833069333042795fb43db24.
- [embedded-evidence-audit.json](evidence/embedded-evidence-audit.json.gz), SHA25605d2754dbc9000527a6d710bb19f3125da13bfeaf7ca1ec3a2524ffb8d0ee44c.
- [readable-normalization-audit.json](evidence/readable-normalization-audit.json.gz), SHA2564ee840ddd3005caf4d71f435084cb63ae153b73538c3cc15b836eefe625ca534.
- [opening.json](evidence/opening.json.gz), SHA2565d52f0b6a00b0503ea8351c771f5f5e8bbfb5f3aaec769f371138aba50301bd9.
- [closing.json](evidence/closing.json.gz), SHA2565d52f0b6a00b0503ea8351c771f5f5e8bbfb5f3aaec769f371138aba50301bd9.
- [integrity.json](evidence/integrity.json.gz), SHA256b838673c06f2bebad865283e76d40588c4e1f1fb1eb87f5904e0db26a474dac0.

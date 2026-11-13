# Command/evidence ledger

All commands ran in `/Users/chuckrussell/Dev/gendev/agent-framework`, except filesystem operations with explicit absolute paths. All fresh commands exited 0. No test/build/install/network command was run. Shell read outputs were inspected in the tool transcript; only the evidence files listed below were persisted. Large combined terminal reads were truncated; governing sections were subsequently reread in bounded ranges. This ledger records exact verification commands and read selectors; it is not a shell-session recording.

## Qualified invocation constants

P = `/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13`
H = `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-product-council-r1-3346ng5a/review_tools.py`
Q = `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-product-council-r1-3346ng5a/request.json`
S = `/private/tmp/ingest-sol-review-jDcr1r`

These constants below are notation for the exact absolute argv elements, not environment variables actually used.

| Fresh operation | Exact invocation (constants expanded as above) | Exit/evidence |
| --- | --- | --- |
| Request verification, first call | `/usr/bin/shasum -a 256 Q` | 0, expected digest matched before cat |
| Request read | `/bin/cat Q` | 0 |
| Helper verification | `/usr/bin/shasum -a 256 H` | 0, expected digest matched |
| Full helper read | `/bin/cat H` | 0, full source inspected |
| Scratch creation | `umask 077` then `/usr/bin/mktemp -d /private/tmp/ingest-sol-review-XXXXXX` | 0; physical S, private 0700 |
| Opening | `P -I -S -B H boundary --request Q --scratch S --label opening` | 0; opening-integrity.json |
| Administration | `P -I -S -B H admin --request Q --scratch S` | 0; admin-commands.json (all seven exact subprocess commands and exits) |
| Static source/inventory | `P -I -S -B S/static_audit.py` | 0; script is preserved, static-evidence.json and source-excerpts.txt |
| Read manifest | `P -I -S -B S/read_manifest.py` | 0; script preserved, read-manifest.json |
| Closing | `P -I -S -B H boundary --request Q --scratch S --label closing` | 0; closing-integrity.json |
| Changed filenames only | `GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1 git diff --name-only 8c36d8e26c618032c1ff536004a582c07ec56a5b..fb587e7a12f48ef0d6937e008045de1de2dd8cd2` | 0; planning-only filenames; no raw history contents |

Helper environment injects GIT_OPTIONAL_LOCKS=0, PYTHONDONTWRITEBYTECODE=1, UV_NO_CONFIG=true, UV_PYTHON_DOWNLOADS=never and private UV_CACHE_DIR/XDG_CACHE_HOME/XDG_CONFIG_HOME/TMPDIR beneath S. Each boundary executes `git ls-files -s -z` before status and checks protected hashes/metadata. All helper outputs go to S, never the supplied controller directory.

## Read-only inspection commands

`/bin/cat` read AGENTS.md, current-controls.json and pinned criteria; all three repository policies; the full target and companion; REM, compatibility annex, test migration, architecture plan, guide handoff, Tools adoption proposal, package-impact assessment/approval; preparation/council authorization, readiness decision, authority manifest, preparation-checks, baseline summary and migration seed; named behavior/E2E/large-corpus results; and eight owner pyproject.toml files. Full target/assessment/annex and relevant policy sections were read again where earlier combined output truncated. REM was read in bounded ranges `1,240`, `241,520`, `521,850`, `851,1200`, `1201,1420`, `1280,1420`; annex in `1,300`, `301,583`. No raw board/authority/navigation/log history or peer-report linked destination was opened.

Other source reads: `cat packages/friday-chat/src/friday_chat/commands/files.py packages/friday-runtime/src/friday_runtime/tool_loading.py`; `cat S/source-excerpts.txt`. Targeted `rg -n` patterns `def (ingest_file|_handle_ingest|_handle_read|execute|build_framework_embedding_service|ingest|_store|read)|chunk_size|embed_query|embed_documents|PersistentClient|create_task` searched only registry.py, adapters.py, smart_read.py, vector.py, assembler.py, embeddings.py and readers/factory.py. `nl -ba` plus `sed -n '35,85p'` targeted directive activation/slice lines; `nl -ba` plus `sed -n '50,90p'` targeted readiness decisions. All exited 0.

Two qualified `P -I -S -B -` inline standard-library inspections parsed gzip inventory keys/first record and named measured JSON facts/indexes. The inventory read is superseded by preserved static_audit.py and its full hash verification. The measured JSON inspection read only behavior-evaluation/evidence-index.json, end-to-end-evaluation/{facts,evidence-index}.json and large-documents/{facts-v2,evidence-index-v2}.json; its persisted parsed output is measured-evidence.json. It did not follow member paths, open model assets/stores or inspect peer reports. All exited 0. Metadata read and AST parse are feasibility evidence, never import/install/runtime proof.

Inspected preparation-checks.json records older administration, including full-worktree whitespace exit 2; it was not replayed. Named measured reports' tests/live calls/component verdicts are inspected attribution only. Fresh checker argv/exits are authoritative in admin-commands.json. Report generation, ledger creation and checksum generation write only new reviewer-owned S files and execute no product code.

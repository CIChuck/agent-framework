# Isolated INGEST readiness — C0 control-plane foundation

This is the first construction slice of CD-CMD-INGEST-GATE-A-001 v0.3. It uses
**CPython 3.13.10 and its standard library**, with `-I -S -B` on every entry and
`-O` on optimized lanes. It imports no Friday application package and never uses
the working `.venv`. Versioned files belong here; all unit inputs and outputs
belong to a new explicitly selected private unit project/scratch.

C0 implements committed-byte startup, strict controls, physical paths, private
child settings, a promotion/budget ledger, read-only Git object export, metadata
detection, fake model-window/transport controls, structural PDF/DOCX seeds and
manual control-run operations. It is **not the completed A0–A4 pipeline**. Real
resolution, installs, conversion/chunking, model calls, the full thirty-document
matrix and implementation of their qualified execution adapters remain later
construction/activation. A successful C0 test or report does not qualify Docling,
OCR, an embedding model, a vector store or production `/ingest`.

## Trust and preparation

1. Select the recorded CPython 3.13.10 base binary (not a `.venv` symlink) and
   verify its SHA256 against the construction receipt. Site processing stays off.
2. Use the frozen harness selection manifest supplied with the C0 construction
   evidence. It binds the code commit/tree and every regular file's Git blob and
   SHA256. Verify the manifest digest and the single `bootstrap.py` digest
   externally before launch. A path or a self-generated dirty manifest is not
   approval. The post-init frozen `run.py` remains a ledger-bound entry and an
   accidental-change check; it cannot authenticate malicious replacement of itself.
3. For a manual C0 run, create a fresh private **unit project** and a separate
   control directory outside the live checkout. Copy `config.example.json` there
   and fill the explicit unit project, run ID, approved manifest digest, pinned
   envelope digest and interpreter digest. Compute the exact config SHA256.
   Do not load an application YAML or scan existing stores. The actual repository
   `.friday_test/` remains absent during C0 builder/validator runs.
4. No dependency or endpoint is needed for C0 selftests. The separately approved
   private Ruff/mypy tool profile supplies static checks; it is not a runtime
   dependency or permission to install Docling. Keep package/lock bytes unchanged.

The construction handoff supplies concrete paths and digests for the frozen
manifest/interpreter, so these operations can be repeated without an agent.
Placeholders below must be replaced explicitly, never inferred from HOME/cwd.

## Manual commands

These commands are implemented. Use an operator-verified bootstrap whose complete
selected file bytes match the committed manifest. It reads/hashes once and compiles
exactly those buffers; pyc caches, extra Python files and path-loader reopens refuse.

```text
<base-python> -I -S -B <verified-bootstrap.py> preflight --harness-manifest <manifest> --harness-manifest-sha256 <approved-digest> --config <control.json> --config-sha256 <config-digest>
<base-python> -I -S -B <verified-bootstrap.py> init --harness-manifest <manifest> --harness-manifest-sha256 <approved-digest> --config <control.json> --config-sha256 <config-digest>
```

Preflight creates no file, Git view, network request or store. C0 init requires an
absent run directory, creates only that owned unit run, copies the verified harness
and writes canonical controls plus an immutable ledger identity. It does not export
the application source or establish actual upstream activation. Its JSON output
names the frozen harness/config/manifest paths and canonical config digest.
All subsequent operations execute that frozen copy:

```text
<base-python> -I -S -B <run-root>/harness/run.py selftest --harness-manifest <frozen-manifest> --harness-manifest-sha256 <approved-digest> --scratch <new-private-test-output>
<base-python> -I -S -B -O <run-root>/harness/run.py selftest --harness-manifest <frozen-manifest> --harness-manifest-sha256 <approved-digest> --scratch <other-new-private-test-output>
<base-python> -I -S -B <run-root>/harness/run.py run --stage all --harness-manifest <frozen-manifest> --harness-manifest-sha256 <approved-digest> --config <frozen-control.json> --config-sha256 <canonical-config-digest>
<base-python> -I -S -B <run-root>/harness/run.py report --harness-manifest <frozen-manifest> --harness-manifest-sha256 <approved-digest> --config <frozen-control.json> --config-sha256 <canonical-config-digest>
<base-python> -I -S -B <run-root>/harness/run.py stop --reason operator_stop --harness-manifest <frozen-manifest> --harness-manifest-sha256 <approved-digest> --config <frozen-control.json> --config-sha256 <canonical-config-digest>
```

The scratch directories must already exist and be explicitly private. Selftest
arms the Python guard before verified test discovery, uses only unit-owned fake
roots and qualifies its intended assertion paths in normal/optimized modes. Tests
under `tests/` are not collected by the root's default pytest paths. Bare external
pytest/working-environment discovery is not a supported harness entry.

C0 `run --stage all` and selected A0–A4/prepare-model currently return
`BLOCKED_NOT_ACTIVATED`, exit **3**, with zero upstream effects. They are admission
interfaces, not successful no-op implementations of those future stages. Report
returns `INCOMPLETE`, exit **3**, and lists unqualified work. Future adapters require
separate qualified source/tool/asset/model inputs and later implementation proof.
A mere receipt cannot turn this C0 version into an implemented upstream adapter.

`promote --manifest <candidate> --sha256 <digest> --approval <receipt>` verifies an
existing candidate and exact predecessor; no stage promotes itself. Actor strings
and hash chains are consistency records, not cryptographic authentication of a
malicious local owner. Stop is atomic, sticky and lease-free. In this C0 version a
manual stop is terminal for the run's effects: use a new run ID, with no implicit
clearance. Report stays available. No service or unrelated process is terminated.
Refusals exit **2**; selftest success/failure exit **0/1**. Refusals/setup failures
are not semantic negative-test credit unless the expected control assertion runs.

## Evidence and limits

The guard intercepts declared Python-visible reads/probes/writes/process/network
operations; ancestor metadata needed for physical path checks does not allow
ancestor payload reads or listing. Native children and extension code are not OS
contained. Their known channels require separate qualification/detection; unsupported
profiles block. C0 native Git writes are allowed only inside private fixture
repositories, never the live `.git`. Export uses a separate private object view.

The qualified CPython 3.13.10 C0 entrypoint installs these boundaries before
verified discovery/imports. All standard `threading.Thread` launches and low-level
`_thread.start_new_thread`/`start_new`/`start_joinable_thread` launches refuse while
guarded. The interpreter's `_thread.start_new_thread` and
`_thread.start_joinable_thread` audit events cover imported-before-guard builtin
aliases too. C0 supports no in-process worker-thread propagation; the separately
bound guarded Python child remains the supported worker shape.

The supported discovery inventory is installed `os.stat`, `lstat`, `fstat`,
`access`, `readlink`, audited `listdir`, `scandir`, `chdir`/`fchdir`, and their
`pathlib`/`os.path` delegates. Present and absent outside paths refuse identically;
convenience functions such as `Path.exists` and `os.path.exists` catch that stat
refusal and return `False` for both without performing the outside stat.
Only stat/lstat/readlink metadata on exact ancestors is admitted for declared-root
canonicalization; it grants no access/permission probe, payload, listing or write.
All supported `dir_fd` probe forms refuse, even with an absolute pathname. Regular
or directory target descriptors refuse as unclassified, including `stat`/`fstat`,
directory listing and mutation fd variants; existing standard-stream/FIFO
classification is unchanged. Directory entries must be acquired through guarded
enumeration. This is an installed Python-entrypoint boundary, not interception of
saved raw pre-install nonaudit builtins, previously acquired directory-entry
objects, `pathconf`/`statvfs` profiles or arbitrary native calls. A future profile
requiring those channels needs separate qualification and otherwise blocks.

The complete qualified directory-relative mutation inventory is `open`, `mkdir`,
`remove`/`unlink`, `rmdir`, `chmod`, `chown`, `utime`, `rename`/`replace`, `link`,
`symlink`, `mkfifo` and `mknod`. Every nondefault source/destination `dir_fd`
refuses before effect. The qualified audit argument positions (zero based) are:

| Audit event | Directory descriptor positions |
| --- | --- |
| `os.mkdir`, `os.chmod` | 2 in `(path, mode, dir_fd)` |
| `os.remove`, `os.rmdir` | 1 in `(path, dir_fd)` |
| `os.chown` | 3 in `(path, uid, gid, dir_fd)` |
| `os.utime` | 3 in `(path, times, ns, dir_fd)` |
| `os.rename`, `os.link` | 2 and 3 in `(source, destination, src_dir_fd, dst_dir_fd)` |
| `os.symlink` | 2 in `(source, destination, dir_fd)` |

These audit events represent an omitted descriptor as `-1`; only `None`/`-1`
admit the ordinary path branch. `open`, `mkfifo` and `mknod` require installed
wrappers because their audit event is absent or omits `dir_fd`; wrapper calls
admit only the default `None`. `fchmod`/`fchown`/`ftruncate` and fd `utime` audit
the actual target descriptor, which receives the unclassified-descriptor refusal.
Regression tests retain ordinary owned-path positives and compare rejected fake
targets' mode, timestamps and content, with no production target involved.

All fixtures and tests are disposable, explicitly rooted and retained for inspection;
no cleanup scans/reset of user state. The deliberately unsafe startup-canary control
processes only its fake site. It never alters actual user/system sites. The fake
transport is in-process, and a character-count callback in a protocol test is not
model-token qualification. Thirty-format oracles are retained as future requirements
in `fixtures/expectations.json`; the two C0 structural seeds earn no A2 credit.

The fake transport rechecks stop and expiry after counting and all reservations,
immediately before its final handoff. A control change during either callback
prevents that handoff and leaves actual attempts at zero; completed reservations
remain charged across refusal and reopen. Entering the synchronous fake callback
is the bounded accepted-in-flight boundary: a change inside that callback cannot
cancel the attempt it has already accepted, and the next request refuses. This
does not promise an atomic OS/service handoff or a race-free real HTTP adapter.

Static verification uses a hash-bound private copy of root Ruff/format/mypy rules,
private tools, `--no-site-packages`, explicit namespace/source paths and private
caches. No source suppression or root rule weakening is authorized. Historical
root lint/collection/format debt remains failed/unwaived; C0 is not a whole-repo
passing claim. Fresh independent implementation review is required before a
construction slice can be called verified; human acceptance and delivery stay separate.

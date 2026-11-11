# Gate-A harness — execution and evidence contract

Version: **0.1 — corrected draft**, 2026-11-11. No construction or stage effects
are activated. This contract resolves the six design-gap groups from the first
council. Its obligations are proposed requirements, not claims of implemented
guards or completed qualification. The construction directive pins these bytes.

## 1. Trust roots, startup and interpreters

The operator selects an exact qualified CPython 3.13.10 base interpreter and
records its binary/stdlib identity and the approved launcher hash before launch.
This is the initial trust root; a program cannot authenticate its own replacement
after that replacement has begun executing. A compromised OS, trusted binary or
malicious operator is outside this test-harness threat model. No production
interpreter, installation or configuration is changed to establish trust.

All Python invocations, including preflight, init, control/report commands,
tests and Python workers, use **`-I -S -B`**, with `-O` added in optimized lanes.
No automatic site initialization, `site.main()`, arbitrary `.pth`,
`sitecustomize` or `usercustomize` is allowed. `PYTHON*` variables are not relied
on under isolated mode; required behavior is explicit in argv. Before non-stdlib
imports, validate executable/stdlib origins, lexical and canonical paths, ownership,
run bindings and the controlled import roots. Reject the working `.venv` by both
invocation path and resolved identity/context; a symlink to a shared base binary
does not make its working-venv invocation acceptable.

The core orchestrator uses only qualified stdlib and the hash-bound harness.
Load sibling modules by explicit validated file locations, then install only the
approved frozen harness roots. Installed-profile workers use separately recorded
private interpreters and distribution/file manifests. With Python 3.13 `-S`, do
not derive private site paths from `sys.prefix`: use the validated installation
manifest and explicit private dependency roots. Do not restore discovery using
`site.addsitedir`, `.pth` execution or ambient site initialization. Workers load
the hash-bound guard explicitly before dependency imports, not via startup hooks.

Required future proof: disposable fake-site `.pth`/`sitecustomize` canaries, clean
positive startup and an intentionally unsafe private control showing the canaries
are armed. Safe commands must enter the intended harness successfully with no
canary execution, forbidden import/write or premature network request. Cover all
entry points and Python children, normal and `-O`. A setup/import failure does
not prove a guard. Never plant canaries in the actual user/system installation.

## 2. Ambient settings and native tool profiles

Leave real HOME unchanged but do not use its settings as test configuration.
Construct a minimal child environment, stripping inherited Python, loader,
provider, proxy, credential and Git-discovery overrides. Explicitly select cwd,
interpreter, target, config, cache/temp/log/output and credential locations under
the run. Tools must not discover the parent production workspace merely because
`.friday_test/` is nested inside it. Record each tool binary/version/hash, exact
argv, effective config origins and the suppression mechanism actually qualified.

| Tool/channel | Required profile |
| --- | --- |
| uv | Qualified `--no-config`; no dotenv; explicit run-owned target/interpreter/cwd and selected requirements/export. Disable project discovery unless an exact run-owned metadata rehearsal is selected. `--no-project` alone can still discover a venv, so it is insufficient without explicit target binding. All UV/XDG data/cache/config/credential roots and `NETRC` point to owned empty/private locations; keyring and Hugging Face credential discovery disabled. No auth command or credential-bearing URL. |
| pip | No pip executable invocation in this unit; use the manifest-qualified uv wheel installer. Adding a pip workflow needs an explicit profile/scope revision rather than assuming its isolated flags are sufficient. |
| Git | Use the private object view in section 3, never production repository discovery/configuration. Disable optional locks, replace objects, user/system configuration, hooks/fsmonitor, prompts, credentials, pagers, auto-maintenance and network protocols; bind cwd/git-dir/objects explicitly. |
| HTTP | Direct clients with proxy/environment/netrc/keyring discovery disabled, explicit certificate trust origin, exact host/redirect/method/path policy and no automatic auth. Do not use macOS system proxy discovery. Empty environment variables alone do not establish this. |
| Ruff/mypy/other validation tools | Explicit private config/project boundaries and `--no-cache` or run-owned cache/temp paths. Their argv/profile is part of the manifest; no upward discovery or repository cache. |
| Third-party Python/native libraries | Manifest-owned local assets and all known library cache/output roots explicitly bound. Unknown configuration/cache/credential channel stops that profile before qualification; do not guess an environment-variable name. |

Flags and variables are version-qualified against each pinned tool, not assumed
from current upstream documentation. The profile records bootstrap TLS roots
separately from the final target Certifi verification. No insecure TLS bypass is
allowed. An unsupported isolation switch, required ambient credential or unknown
mirror blocks the dependent stage. No production setting is modified to repair it.

Future tests use a fake HOME-like directory and fake parent project/repository
under test-owned roots, never real HOME. Poison those fixtures with tool settings,
proxies, credentials and cache paths; prove they are ignored/refused and effective
origins remain explicit. Reading or printing real credential files is forbidden.

## 3. Exact committed-source export without production Git mutation

Activation supplies full commit/tree IDs for the application source and harness,
the source object-directory path and an explicit source-selection manifest.
Preflight validates declarations and paths only; it does not create a Git view or
claim object availability. Init checks objects before third-party effects.
Do not copy the working tree or read dirty example YAML bytes. Untracked/ignored
state, `.env`, `.friday*`, exports and live credential-bearing tests are excluded.
In particular, exclude `packages/friday-finance/tests/test_integration_massive.py`.
Committed configuration examples may be selected as data, never auto-loaded as
the operator's configuration. Do not display source payloads in export receipts.

Init materializes a minimal **run-owned bare control directory**, with its own
HEAD/config/objects/refs and empty config/template/credential files. This is an
object-reading view, not a clone, checkout or worktree. The production object
directory is a declared read-only alternate; production `.git/config`, index,
refs, hooks and workspace discovery are not used. Reject undeclared alternate
object roots. The view has no remotes/promisor configuration or lazy fetching.
No `git init`, clone, fetch, checkout, worktree, stash, reset, status or diff is
needed by the harness. Creating this view with stdlib writes only inside the run.
Bind `GIT_DIR`/`GIT_OBJECT_DIRECTORY` to that view and only declared alternate
objects. Set `GIT_OPTIONAL_LOCKS=0`, `GIT_CONFIG_NOSYSTEM=1`, empty private
`GIT_CONFIG_SYSTEM`/`GIT_CONFIG_GLOBAL`, `GIT_TERMINAL_PROMPT=0` and
`GIT_NO_REPLACE_OBJECTS=1`; strip inherited Git/config/worktree/index overrides.
The qualified private config disables hooks, fsmonitor, credential helpers,
auto-maintenance and all network protocols. Only the index-copy collector gets
its explicit private `GIT_INDEX_FILE`. Report effective origins and argv.

Only qualified read-only `rev-parse`/`cat-file`/`ls-tree` object operations are
allowed against that explicit private view for export. Export selected regular blobs by
object ID; do not use worktree filters, LFS/smudge programs, export substitution,
attribute-dependent omissions or archive extraction to produce source bytes.
Independently verify commit/tree/blob identities, selected paths, Git object
type/length/hash, output SHA256 and modes. An absent object fails locally; never
fetch it. Selected symlinks/gitlinks/path escapes are refused unless excluded in
the approved selection manifest; do not follow them into external state.

Both harness and source copies must match their recorded commits and manifests.
The committed export stays read-only. A0 may derive a separately named private
profile overlay for the already proposed dependency metadata rehearsal, changing
only selected metadata/requirements/lock files. Record the base tree, patch plan,
before/after bytes and resulting overlay manifest; promotion binds that derivation.
A1 builds from the declared overlay with all code files byte-identical to base.
This is a proposed install profile, never changed product code or shipped metadata.
No uncommitted source fallback. Production `.git/` mutations, index refreshes,
locks, refs/config/worktree changes and credential lookup are forbidden.
For boundary evidence, take a stable read-only byte snapshot of the declared
production index into the run, rejecting a changing source during the copy. A
separate allowed collector runs `git ls-files -s -z --cached` against that copy
via the same private Git view and explicit `GIT_INDEX_FILE`; it never refreshes
the production index or runs status. Copy declared split-index dependencies too
when that format is qualified; otherwise stop without changing source settings.
Hash the logical entries; a raw index-file
hash alone is not a substitute. HEAD/ref identities are collected read-only from
explicit declared metadata paths. Host T3 checkpoint activity is identified
separately and never attributed to or authorized for the harness. Future export tests use private
fixture repositories with dirty/untracked/ignored traps and poisoned config.

## 4. Run identity, promotion ledger and resumable stages

Pre-init control inputs live under `.friday_test/control/<run-id>/`; they must
not pre-create the run root. Init requires an absent `runs/<run-id>/`, then binds
immutable schema/run ID, source/harness IDs, approved config/envelope and seed
manifest. It creates `state/bindings.jsonl`. Later candidate manifests do not
rewrite this initial identity.

Reject oversized control files before parsing: receipts/config/ledger records
are at most 1 MiB each; inventory/manifest bytes remain within the existing 64 MiB
metadata ceiling with explicit finite record bounds. No silent truncation.
Use versioned strict JSON and canonical UTF-8 serialization (sorted keys, fixed
separators, no NaN/duplicate keys). Each append-only ledger record has sequence,
event, previous-record SHA256, timestamp and payload hashes; its own SHA256 covers
the canonical record without the self-hash. No payload/document text or secrets.
Init/promotion/stage operations take one run-owned exclusive writer lease;
concurrent writers fail rather than race. Reports read a stable snapshot.
Validate order, referenced bytes, allowed transitions and resource counters on
every reopen. Missing/truncated/tampered/out-of-order records fail; never silently
reinitialize or repair a ledger. Hash chaining detects inconsistency, not a
malicious local owner who rewrites every trusted input.

A stage emits candidate manifests/evidence. Promotion is a separate explicit
`promote` operation supplied with an approved manifest SHA256 and a matching
promotion receipt from the activation's named promoter (Chuck or delegated Codex
controller within the envelope). Bind actor, time, run, stage, manifest digest,
scope and predecessor ledger tip. The explicit authorized operation and pinned
receipt are the consent; an actor string or self-consistent hash chain alone is
not proof of authority. No stage promotes its own output or manufactures consent.
Only enumerated promotions/windows may extend the binding. Later model/counter/input facts are typed candidate manifests supplied under
`control/<run-id>/`, not edits to the immutable init config. The initially unset
example fields describe missing promoted facts. Other source/config/envelope
changes invalidate the run and require a new run ID.

| Transition | Prerequisites and output |
| --- | --- |
| Init to A0 | Activated metadata/source scope; immutable identity. A0 emits the candidate dependency/wheel manifest. |
| A0 to A1 | Explicit promotion of exact dependency/wheel/build-tool metadata. A1 installs private profiles and emits installed evidence plus candidate asset/fixture/counter plans. |
| A1 to A2 | Explicit promotion of assets/inputs and allowed transfer/fixture effects. A2 produces real-format evidence and candidate input/preparation manifests; local counts remain preliminary until qualified. |
| Prepare A3 | Offline `prepare-model --model-profile <candidate-profile>` freezes the exact candidate model/counter/profile, synthetic or supplied test batch payload hashes and budgets after A2 promotion. It makes no endpoint call. Changes require a new candidate/promotion, not mutation of the previous batch. |
| A2 to A3 | Explicit promotion of those exact manifests/batches, then a window receipt binding their hashes and the current promoted ledger tip. Only now can model status/embedding requests begin. The receipt anchors that promoted prefix; ordinary budget/status execution records may extend it, but any new scope-affecting promotion invalidates the receipt. |
| A4/report | Aggregate observed/blocked/skipped results without new model/network/store effects. Full readiness requires every required qualification; a scoped offline pass never implies that. |

`run --stage all` executes only consecutively ready stages. At a missing approval,
promotion or window it returns `AWAITING_PROMOTION`/`AWAITING_WINDOW` and exits;
it never waits interactively, polls for consent, bypasses a gate or auto-promotes.
The operator/controller reviews the candidate, invokes promotion and starts
another invocation. The window is prepared only after its referenced hashes
exist. This resolves the former impossible up-front receipt/static-init binding.

Preserve all numeric envelope ceilings. The two-hour allowance is cumulative
**active qualification execution across invocations**, not two hours per stage.
Human waiting between invocations is reported separately and consumes no running
child/process budget. Metadata/install subcaps accumulate across resumed invocations
and profiles; single/warm conversion limits are per conversion. No numeric limit
is increased; the envelope names the clarified overall_active_seconds field. Charge/reserve
time, attempted transfers and requests before effects, conservatively account for
an interrupted invocation, and never reset counters on resume. On exhaustion,
stop effects and use only the existing quiescence grace to record failure; no
fresh qualification allowance is created. No stalled human prompt keeps a process
or model window alive. Record wall and active time separately.

## 5. Preventive controls, detective evidence and protected roots

The production/no-fallback requirement remains mandatory. Do not describe Python
audit hooks as native/OS containment. Classify controls individually:

| Class | Required scope and proof |
| --- | --- |
| Prevention | Startup suppression, configuration/manifest/path validation and instrumented Python operations are refused before the controlled effect. Explicit worker bootstrap proves the guard is installed before dependency imports. OS/native preventive controls, if used, must be identified and qualified, not assumed. |
| Detection | Before/after bounded metadata snapshots of declared shared/default cache roots and protected production state cover native/non-Python channels that cannot be intercepted by Python. A change fails isolation credit and stops further work; it is never excused or reported as prevented. |
| Residual/unknown | No coverage claim for undeclared roots, arbitrary native syscalls or the entire filesystem. If a profile's known default/config/cache/write channels cannot be neutralized or covered to the approved boundary, that profile is blocked. A passing fixture does not override this. |

Before any real tool/library profile runs, its activation manifest names protected
checkout/source/config/lock/test paths, production `.git` logical state, `.venv`,
`.env`, `.friday/`, `.friday-old/`, exports and each tool/library's specific default
cache/config roots (including absent roots). Hash committed/declared production
files where permitted. For user cache directories collect only bounded metadata
(canonical path, entry type, size, mode, mtime), no payloads, no symlink traversal
or whole-HOME scan. Bind enumeration limits; if coverage would truncate or exceed
the envelope, stop rather than silently claim a complete snapshot. Never inspect
LM Studio model-directory payloads; the operator supplies served-model identity.

Native tool binaries are qualified, hash-bound and run with explicit settings,
private paths and exact network scope. Where available, qualify additional native
write/network containment. Metadata-only detection is bounded evidence, not an
OS guarantee or permission for an outside write. A detected production/cache
change is an isolation failure requiring attribution/stop, not automatic cleanup
or restoration. The separately authorized LM Studio window is classified as a
shared-service exception, not a blanket exception for framework/tool caches.

Required future tests use simulated production/cache roots under the test run:
one explicit Python refusal before effect, a native/child fake-cache write that
is detected and fails isolation, an instrumented-child positive control, and
snapshot failure/truncation/unknown-root refusal. Real protected paths are never
used as destructive test targets. Native source-export controls and external
cache metadata limits must be demonstrated before real upstream effects activate.

## 6. Shared LM Studio loaded-state and window contract

Keep the approved existing endpoint; no new server or copied served weights.
The operator stops production, restarts the server, separates logs and confirms
the selected embedding model is already loaded. The harness performs none of
those service/config/model operations. It uses direct test-owned clients/config,
never DI/Runtime assembly that could open a default store or background task.

Before **any** server request, the run-specific receipt binds the promoted source/
config/dependency/asset/input/batch/model/counter hashes, endpoint, limits and
budgets; operator identity and stop/restart/log evidence; confirmation/expiry;
loaded model key/instance/identity and the operator-attested JIT, idle-TTL and
eviction behavior. Require a configuration in which requests cannot trigger a
load/eviction and the loaded instance remains available through the window.
Unknown/unsafe conditions block A3. Do not silently configure the server to make
them safe. A setting change beyond the approved operator restart would need its
own authority; no such change is made or granted by this paper correction.

The operator selects **one** supported native read-only status profile in advance:
`GET /api/v1/models` (matching embedding key and `loaded_instances[].id`) or
`GET /api/v0/models` (matching embeddings ID and `state == loaded`). Qualify that
profile against the declared installed server version; no automatic probing or
fallback between paths. A downloaded-only listing is not loaded-state evidence.
V0's unavailable instance details remain operator-attested and labelled as such.
Do not upgrade the server or require a second endpoint to gain an observation.
If the selected version cannot substantiate the needed state, A3 is blocked.

Only that exact GET status route and `POST /v1/embeddings` are permitted; no
SDK getter that may load a model, admin route, redirect, provider fallback, auth
discovery, TTL override or model-management payload. Bind the exact loaded request
identifier in the receipt and validate response identity/shape. Current scope
assumes an explicitly allowed local unauthenticated endpoint; authentication
requirements block rather than sourcing a production credential or changing
server security. The receipt is not evidence the actual local server is ready.

Validate the receipt and fresh read-only loaded state immediately before every
embedding batch and again after it. Require the operator-attested no-JIT/no-evict/
no-idle-unload conditions throughout; the before/after check is additional evidence,
not a remedy for a check/request race. Status and embedding calls all count toward
the same 64-request ceiling; vectors/tokens retain their existing cumulative caps.
Unexpected model/state/identity change, expiry, revocation or exhausted budgets
stops further requests without a reload or service action. Latency is diagnostic,
not sole proof of loading or identity.

The revocation channel is `state/stop.json`, bound to run/schema/sequence and
re-read before every request. The receipt starts under the control input root,
then is copied read-only/hash-bound under `config/windows/<digest>.json`; its
digest is appended without rewriting earlier promotions. Check its anchored
promotion prefix, not equality with the constantly extending execution tip.
Revocation is sticky until a new explicitly confirmed window; its atomic test-owned
stop-file update does not wait for the stage writer lease. It prevents new
requests, not an already in-flight request that can only finish or time out. No window or endpoint
facts are filled in by this specification. Operator resumption is always manual.

Future simulated-server controls cover unloaded/downloaded-only models, unsafe
or unknown JIT/TTL/eviction settings, stale receipts, unsupported status shapes,
wrong IDs, state changes, stop/expiry and zero unauthorized requests. Include a
valid already-loaded flow, exact call budgets and labels for attested versus
observed fields. Use an in-process stub transport, not a real socket/server, for C0 tests.
No real LM Studio or other network operation is needed for harness unit tests.

## 7. Explicit proof and reporting

Reports must distinguish control class, effective tool config/origins, operator
attestation versus live observation, candidate versus promoted versus qualified
manifests, cumulative budgets, stopped/resumed invocations and scoped/full status.
Use typed versioned records and explicit exceptions, normal and optimized proof,
source/private-target origins and unchanged protected-state evidence. Keep all
validation caches private; no production suite/configuration is rewritten.

Suggested CLI statuses are `PASS`, `FAIL`, `AWAITING_PROMOTION`, `AWAITING_WINDOW`
and `INCOMPLETE`, each with scope and `readiness_complete`. `all` returns nonzero
when awaiting/incomplete; report-render success is not qualification. Publish
exact exit codes and walkthrough only after construction; no CLI exists today.

Primary mechanism references, not installed-target qualification:
[Python 3.13 site](https://docs.python.org/3.13/library/site.html),
[uv configuration](https://docs.astral.sh/uv/configuration/files/),
[uv HTTP credentials](https://docs.astral.sh/uv/concepts/authentication/http/),
[Git object-directory environment](https://git-scm.com/book/en/v2/Git-Internals-Environment-Variables),
[LM Studio native V1 model status](https://lmstudio.ai/docs/developer/rest/list),
[native V0 status](https://lmstudio.ai/docs/developer/rest/endpoints) and
[loading/TTL/eviction](https://lmstudio.ai/docs/developer/core/ttl-and-auto-evict).

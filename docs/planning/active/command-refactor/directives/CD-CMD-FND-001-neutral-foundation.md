# CD-CMD-FND-001 — neutral command foundation

Date: 2026-11-04
Revision: 2026-11-06 — bounded Step 3 readiness correction; construction approval pending
Status: DRAFT — not approved; product implementation not authorized
Initiative: `friday-command-refactor`
Work unit: `CMD-FND-001`; proposed P2 foundation slice, not P2 completion
Branch: `feature/command-refactor`
Historical source baseline inspected: `25d2dcb6`; exact local execution base
and applicable local baselines must be frozen at approval. This imported draft
is not a construction authorization for either checkout.

Current product-source baseline: `bbbd90e05143137c5a1d49eacedb4125d254b8fb`.
The proposed execution base is the fresh corrected readiness-validation
candidate supplied by full SHA in its correction-validation dispatch, with
matching product bytes. The original round-one council candidate is historical,
not the proposed execution base. Step 4 must record the new exact base before
execution; a later base/authority change requires revalidation. Approved API
input SHA-256:
`e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74`.

## Role, authority and entry conditions

Builder implements only the approved foundation API. Follow repository
`AGENTS.md`, engineering/independent-validation policies, the board,
[scope decisions](../scope-decisions.md), [phase plan](../phase-plan.md) and
[API draft](../shared-command-api.md). This directive remains a draft until
maintainer approval and the exact API revision/base are recorded. Independent
architecture review and applicable P0/P1 gates must be satisfied or explicitly
amended by the maintainer; the scope decisions alone do not waive those gates.

Before construction, record the full execution-base SHA, authority file digests,
accepted API-01–API-06 criteria and review disposition in the unit report. Run
board validate/next/show and confirm started/granted/current branch. Unresolved
family behavior and installed baseline gaps cannot be silently waived; the
maintainer must explicitly confirm this foundation-only unit's readiness.

## Proposed foundation-only prerequisite amendment — not approved

The [Step 3 readiness review](../readiness-review.md) defines RD-01 and RD-02.
Step 4 must explicitly approve both the directive and those scoped dispositions;
approval of CMD-DESIGN-001 alone supplies neither. Until then the existing full
P0/P1 gate continues to block construction.

RD-01 would permit only this standard-library, synthetic-handler foundation
before final family/P1 closure. Complete per-command behavioral signoff, family
schemas/service mapping, progress/cancellation, installed-client acceptance and
final scenario/platform obligations remain mandatory before affected migration
units. All 50 cases/three aliases have proposed owners in the readiness map;
none migrates here. No API-01–API-06, neutral-import, runtime-invariant,
standalone-wheel or fresh-independent-review obligation is deferred.

RD-02 records distinct default-profile results: Chat, its registry and generic
CLI modules import, and Chat help loads; an explicit `friday_tools` import fails
on missing `friday_finance`. The local `friday_tools.sandbox` module uses the
standard library; the optional `friday_sandbox` distribution is imported lazily
and is a separate surface. The absent generic CLI `app` remains an installed
entry-point limitation. None of these observations proves runtime health.
Do not fix clients or widen their dependencies here. The diagnostic
finance+sandbox install does not establish the minimum extras required or
repair the default tools import. Required installed-client packaging/entry-point
dispositions remain before affected delivery gates, separately from FND-001's
source-level CLI regression and foundation wheel proof (SC-08). This amendment
cannot approve future migrations or whole-refactor exit.

## Objective and non-goals

Create a separately installable, standard-library-only neutral foundation with
typed metadata/requests/outcomes and a registry supporting injected handlers.
Implement exactly the foundation types/signatures in the approved API revision.

Do not add production default handlers, wire Chat/TUI, move any handler, remove
any of the nine names yet, alter generic CLI, fix the missing generic CLI entry
point, change example configs, add provider/domain transports, alter persistence
or admission gates, implement family capabilities, or expose a new executable.
No push, PR, merge, release or deployment is authorized by this directive.

## Exact allowed paths

New package metadata:

- `packages/friday-commands/pyproject.toml`
- `packages/friday-commands/README.md`

Existing integration metadata, tests and inventory, only for cohort membership:

- Root `pyproject.toml`: add `friday-framework-commands==0.1.0a4` to the existing
  `project.optional-dependencies.all` and add
  `friday-framework-commands = { workspace = true }` to `tool.uv.sources`.
  Do not add a default root dependency or change other extras, pins, workspace
  globs, test settings or build settings.
- `uv.lock`: only the new workspace member/package and the two required root
  `all` metadata references, under the lock procedure below; no other resolution
  change or upgrade.
- `tests/integration/test_package_cohort_metadata.py`: extend the exact cohort
  from 17 to 18 projects (root plus 17 members) and include
  `friday-framework-commands`; preserve existing assertions. Add focused checks
  for its empty dependencies/no scripts, root `all` pin/workspace source, and
  artifact-inventory membership with import `friday_commands`. Do not add a
  public API export solely to satisfy an unrelated runtime-version check.
- `scripts/check-package-artifacts.py`: add
  `friday_framework_commands: friday_commands` to the wheel inventory and
  foundation-specific `py.typed`, empty `Requires-Dist` and absent entry-point
  checks. Preserve all existing inventory entries and checks.
- Root `README.md` package-map count/row and `AGENTS.md` package list: add only
  this package and its neutral-library purpose; no unrelated policy rewrite.

New source:

- `packages/friday-commands/src/friday_commands/__init__.py`
- `packages/friday-commands/src/friday_commands/py.typed`
- `packages/friday-commands/src/friday_commands/contracts.py`
- `packages/friday-commands/src/friday_commands/registry.py`

New tests:

- `packages/friday-commands/tests_commands/test_contracts.py`
- `packages/friday-commands/tests_commands/test_registry.py`
- `packages/friday-commands/tests_commands/test_import_boundary.py`

Unit receipts only:

- `docs/planning/active/command-refactor/validation/CMD-FND-001-report.md`

The workspace glob already discovers the directory, but it does not satisfy
the explicit cohort, root `all` inclusion or artifact inventory contracts.
The additions above are required; the package joins the lock-step 0.1.0a4 cohort
as its eighteenth project. No existing client/package dependency, source or test
may change except the explicitly named cohort test and artifact checker. Stop
for any additional path or metadata change. Do not stage unrelated backlog/
config edits. Board/controller state transitions and independent-review reports
are controller/reviewer responsibilities, not builder-owned acceptance.

## Workstreams and acceptance

1. **FND-01 packaging / API-01:** distribution `friday-framework-commands`, import
   `friday_commands`, version 0.1.0a4, Python >=3.13.4. Match existing Hatchling
   packaging convention (including license/authors/URLs/README and explicit
   wheel selection), declare `dependencies = []`, ship `py.typed`, no extras,
   runtime dependencies or scripts. Join the 18-project cohort without adding a
   dependency from Chat, CLI or another member to this package.
   Exports must match the approved API draft; no hidden frontend imports.
2. **FND-02 contracts / API-04:** frozen typed metadata, request/execution,
   closed `FoundationData` union, error/UI-effect/outcome/dispatch models. Enforce
   every row of the API runtime-validation table with exact TypeError/ValueError
   boundaries; no trusted-only constructor bypass; no source-level mypy blanket
   suppression, `Any`, casts hiding an interface defect, or untyped payload escape.
3. **FND-03 registry / API-02–API-03:** normalized canonical/alias maps, immutable
   snapshots, rebuilt canonical stored specs, one-pass normalization, explicit
   blank-alias rejection, deterministic ordering and atomic registration failures.
   Current Chat whitespace grammar, unknown and noncommand semantics are fixed.
   No generic enforcement of metadata choices/required args or shell tokenization.
4. **FND-04 execution / API-05–API-06:** await one injected async handler once;
   propagate unexpected exceptions and cancellation. No I/O, host state mutation,
   UI application, retries, built-in/default handler set or automatic discovery.

## Meaningful tests

- Metadata rejection: blank normalized canonical name/alias, blank trimmed
  description/category/usage, blank argument name/description,
  canonical collision, alias collision and same-call duplicate alias. Compare
  full registry state before/after each failure to prove no partial registration.
  Mixed-case/slashed/padded inputs must yield canonical keys from names() and
  matching rebuilt spec values through resolve()/specs()/request, while leaving
  caller input unchanged. Test
  normalization collisions and the non-idempotent normalization-order examples.
- Copy/freeze invariants: caller collection changes cannot change registered
  metadata; returned names/spec snapshots cannot mutate the registry.
- Parsing: ordinary text, leading space before slash, bare slash, uppercase name,
  extra whitespace, aliases, quoted fragments, //HELP, ///HELP and slash/space
  normalization order. Use the independent API fixture table exactly, including
  zero handler calls for the unresolved /help key from ///HELP. Expected sequences
  come from P0 observations, not a call to the implementation under test.
- Dispatch: unknown name calls no handler; alias delivers canonical request;
  exact argument spelling/order; one awaited call; synthetic handler exception
  and cancellation are propagated, not wrapped or retried. Non-callable handlers,
  nonawaitable returns, invalid outcome types and invalid execute input/context
  types raise TypeError at the specified boundary without retry.
- Constructor negatives cover every row of the runtime-validation table: wrong
  scalar/container/member types (including bool-vs-int), opaque/subclass payloads,
  invalid error codes, raw-string UI effects, mismatched request/spec names, both/
  neither data/error and invalid handled/outcome/effect combinations. Assert the
  exact built-in exception class. Test copied finite iterables and immutability;
  metadata blank-value semantics remain registration checks, not argument policy.
  Exit/clear data are returned, not applied. NoData remains typed semantic data.
- Boundary: importing foundation with frontend modules blocked succeeds; static
  imports and built wheel contain no frontend/domain dependency. Synthetic
  handlers only; no live provider or tool execution and no persisted stores.
- Cohort/inventory: exactly 18 named projects at 0.1.0a4; root `all` includes
  the exact new pin and workspace source; the new package has no dependencies,
  extras or executables; artifact inventory has all 18 distributions and the
  correct new import/typed marker. Exercise the foundation artifact checks with
  a valid wheel/sdist and disposable malformed copies (missing `py.typed`,
  injected dependency or entry point) that must be rejected. Use temporary
  copies only; preserve original artifacts and existing package checks.

Freeze the expected token/result fixtures in tests independently of the new
implementation. There are no command-family parity claims from synthetic cases.
The existing 50-name baseline remains unchanged in Chat throughout this unit.

## Permitted registry access and one lock-generation procedure

These instructions apply only after Step 4 approves this exact directive and
execution base. Current planning remediation authorizes no registry access or
construction. Future construction may read public Python package metadata from
`https://pypi.org/simple/` and download Python artifacts from
`https://files.pythonhosted.org/` for resolution, Hatchling builds and verification.
Only these HTTPS hosts and existing local workspace/cache artifacts are allowed;
no alternate index, Git/VCS dependency, credentials, upload, Python-runtime
download, application tool execution, live provider, telemetry endpoint or
persisted runtime/store construction is permitted. This covers package-manager
traffic, not network permission for tests/application code. Stop for any required
additional host or service. Never use `--upgrade`, `--upgrade-package` or
`--refresh`; existing package resolutions must remain unchanged.

Before editing, freeze approved base/authority hashes, protected dirty-file
hashes, uv/Python/tool versions and installed versions. Inspect package-manager
configuration without disclosing credentials; reject additional indexes,
find-links, resolver overrides and upgrade/refresh settings, including inherited
environment or user configuration. Set `UV_DEFAULT_INDEX=https://pypi.org/simple`,
`UV_PYTHON_DOWNLOADS=never` and `PYTHONDONTWRITEBYTECODE=1` for this unit. Use an
already installed compatible Python and an adequately provisioned validation
environment; missing test/build tools are a reported prerequisite, not permission
for unpinned installation or upgrading the environment.

After only the allowed package/root metadata edits, use this single procedure
from the repository root (`CMD_FND_BASE` is the approved full execution-base SHA):

```sh
export UV_DEFAULT_INDEX=https://pypi.org/simple
export UV_PYTHON_DOWNLOADS=never
export PYTHONDONTWRITEBYTECODE=1
CMD_FND_TMP=$(mktemp -d)
git show "${CMD_FND_BASE}:uv.lock" > "$CMD_FND_TMP/base.lock"
uv lock --default-index https://pypi.org/simple --no-python-downloads
git diff -- uv.lock pyproject.toml
```

Do not run a plain `uv run` to generate the lock implicitly. Before installation
or checks, compare parsed TOML against the saved base lock. The following
stdlib-only comparison removes only the explicitly permitted additions; every
other package record (including versions, sources, dependency/marker graphs,
artifact URLs and hashes) and top-level resolution option must compare equal:

```sh
.venv/bin/python -I - "$CMD_FND_TMP/base.lock" uv.lock <<'PY'
import json
import sys
import tomllib
from pathlib import Path

old, new = [tomllib.loads(Path(p).read_text()) for p in sys.argv[1:]]
name = "friday-framework-commands"
def require(condition, message):
    if not condition:
        raise SystemExit(message)
def canonical(value):
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in value.items()}
    if isinstance(value, list):
        return sorted((canonical(v) for v in value),
                      key=lambda v: json.dumps(v, sort_keys=True))
    return value

require(name not in old["manifest"]["members"], "base already has member")
require(new["manifest"]["members"].count(name) == 1, "missing/duplicate member")
new["manifest"]["members"].remove(name)
added = [p for p in new["package"] if p["name"] == name]
require(len(added) == 1, "expected one new package record")
require(added[0] == {"name": name, "version": "0.1.0a4",
                    "source": {"editable": "packages/friday-commands"}},
        "unexpected new package resolution/dependency metadata")
new["package"].remove(added[0])
root = next(p for p in new["package"] if p["name"] == "friday-framework")
for entries, expected in [
    (root["optional-dependencies"]["all"], {"name": name}),
    (root["metadata"]["requires-dist"],
     {"name": name, "marker": "extra == 'all'",
      "editable": "packages/friday-commands"}),
]:
    require(entries.count(expected) == 1, "missing/duplicate root reference")
    entries.remove(expected)
require(canonical(old) == canonical(new), "unrelated semantic lock change")
print("Only new member/package and root all references changed")
PY
uv lock --check --offline --no-python-downloads
```

Save the textual diff, semantic comparison output, base/new lock hashes and
registry/build receipt in the unit report. If uv emits any additional semantic
change, stop for disposition; do not relax the comparison or delete/recreate
the lock to force resolution. The procedure is a future requirement, not a claim
that today's offline cache can resolve the added workspace member.

## Verification commands and expected results

After the lock proof, use this frozen, no-sync editable overlay for **every**
package/root check. It installs the dependency-free new member in the execution
overlay even though root default dependencies do not include it; `--no-sync`
preserves the provisioned environment and `--frozen` prevents relocking. Do not
replace these commands with plain `uv run`. Run pytest without cache writes:

```sh
cmd_fnd_run() {
  uv run --frozen --no-sync --no-python-downloads \
    --with-editable packages/friday-commands "$@"
}
cmd_fnd_run python -c 'from pathlib import Path; from importlib.metadata import version; import friday_commands; p = Path(friday_commands.__file__).resolve(); assert Path("packages/friday-commands/src").resolve() in p.parents; assert version("friday-framework-commands") == "0.1.0a4"; print(p)'
cmd_fnd_run pytest -p no:cacheprovider -q packages/friday-commands/tests_commands
cmd_fnd_run pytest -p no:cacheprovider -q tests/integration/test_package_cohort_metadata.py
cmd_fnd_run python scripts/check-package-metadata.py
cmd_fnd_run ruff check packages/friday-commands tests/integration/test_package_cohort_metadata.py scripts/check-package-artifacts.py
cmd_fnd_run ruff check .
cmd_fnd_run ruff format --check packages/friday-commands tests/integration/test_package_cohort_metadata.py scripts/check-package-artifacts.py
cmd_fnd_run mypy packages/friday-commands/src scripts/check-package-artifacts.py
cmd_fnd_run pytest -p no:cacheprovider -q packages/friday-chat/tests_chat/test_command_registry.py packages/friday-chat/tests_chat/test_command_foundations.py
cmd_fnd_run pytest -p no:cacheprovider -q packages/friday-cli/tests_cli
cmd_fnd_run pytest -p no:cacheprovider
cmd_fnd_run python scripts/friday-dev-board.py validate
cmd_fnd_run python scripts/check-documentation-lifecycle.py
uv lock --check --offline --no-python-downloads
git diff --check
```

Keep live-provider opt-ins disabled and use the deterministic baseline profile.
If a required check would execute a live application provider/tool, stop and
report the unrun check; registry permission cannot authorize that execution.

All new-package checks, extended cohort/metadata checks and the registry/
foundation Chat suites must pass. Generic CLI must retain its historical
155-pass source-suite baseline unless a reproducible unrelated difference is
recorded and dispositioned before completion; this is not installed-entry-point
acceptance. Metadata validation must cover 18 projects, not just the new member.
Prove the new import succeeds before any root or owning-suite result is used.

The unchanged root pytest gate remains required, but has a known collection
baseline: root discovery includes both whole client suites and their duplicate
`test_display.py` modules produce an import-file mismatch (2026-11-06 planning
probe: 5,923 collected, exit 2). Merely selecting `--import-mode=importlib` also
breaks two Chat tests' sibling `test_mcp_execution_security` imports. Do not
rename tests, change pytest configuration/import paths, omit tests or infer a
policy waiver here. Record the root attempt and baseline failure honestly;
separate new failures, including any foundation import error, from that debt.
Follow repository policy by reporting broader failures and running the narrow
meaningful checks above; there is no unconditional root-pass claim or exemption
from independent review/disposition of remaining gate failures.

Verify baseline 50/3 Chat metadata using the P0 capture method, with new outputs
in the unit report. Full owning-suite proof, if required by review, must preserve
committed-example/xterm controls and disclose pre-existing dirty inputs. Do not
overwrite historical receipts or alter the protected examples to obtain a pass.

Build wheel and sdist in the disposable directory, and validate the new artifacts
against the amended inventory; no upload or all-client install is authorized:

```sh
uv build --package friday-framework-commands --no-python-downloads \
  --default-index https://pypi.org/simple --out-dir "$CMD_FND_TMP/dist"
cmd_fnd_run python scripts/check-package-artifacts.py \
  --package friday_framework_commands "$CMD_FND_TMP/dist"
uv venv --no-python-downloads --python .venv/bin/python "$CMD_FND_TMP/venv"
uv pip install --offline --no-index --no-deps \
  --python "$CMD_FND_TMP/venv/bin/python" "$CMD_FND_TMP"/dist/*.whl
```

The extended cohort test must also compare the complete artifact inventory to
all 18 project names; a selected artifact check alone cannot prove completeness.
Run the malformed artifact checks described above and record their refusal
results. This unit builds/proves the foundation artifacts, not a release of the
entire cohort.

Outside the repository, use the disposable interpreter in isolated mode with
inherited `PYTHONPATH` cleared. Save this stdlib-only independent smoke fixture
as `$CMD_FND_TMP/foundation-smoke.py`, not as a product file:

```python
import asyncio
import sys
from importlib import metadata, resources
from pathlib import Path

class BlockOtherFriday:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith("friday_") and fullname.split(".")[0] != "friday_commands":
            raise ModuleNotFoundError(fullname)

def block_network(event, args):
    if event in {"socket.connect", "socket.bind", "socket.getaddrinfo",
                 "socket.gethostbyname", "socket.gethostbyaddr", "socket.sendto"}:
        raise RuntimeError("network forbidden in foundation smoke")

sys.meta_path.insert(0, BlockOtherFriday())
sys.addaudithook(block_network)
import friday_commands
from friday_commands import (
    CommandExecution, CommandOutcome, CommandRegistry, CommandSpec, NoData,
)

assert Path(friday_commands.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
dist = metadata.distribution("friday-framework-commands")
assert dist.version == "0.1.0a4" and not dist.requires
assert not dist.entry_points
assert resources.files(friday_commands).joinpath("py.typed").is_file()
assert {d.metadata["Name"] for d in metadata.distributions()
        if d.metadata["Name"].startswith("friday-")} == {"friday-framework-commands"}
calls = []
async def handler(request, execution):
    calls.append((request.name, request.args, request.spec.name, execution.session_id))
    return CommandOutcome(data=NoData())

async def smoke():
    registry = CommandRegistry()
    registry.register(CommandSpec("help", "Help", "test", "/help", aliases=("h",)), handler)
    execution = CommandExecution(session_id="wheel-smoke")
    for text in ("/help Topic", "/H Topic"):
        result = await registry.execute_text(text, execution)
        assert result.handled is True and type(result.outcome.data) is NoData
    assert calls == [("help", ("Topic",), "help", "wheel-smoke")] * 2
    result = await registry.execute_text("/missing", execution)
    assert result.handled is True and result.outcome.error.code == "unknown_command"
    assert result.outcome.error.command_name == "missing"
    result = await registry.execute_text("hello", execution)
    assert result.handled is False and result.outcome is None and len(calls) == 2

asyncio.run(smoke())
print("Isolated foundation wheel/import/dispatch proof passed")
```

Run it from the disposable directory (the subshell preserves the caller's cwd):

```sh
(
  cd "$CMD_FND_TMP"
  env -u PYTHONPATH "$CMD_FND_TMP/venv/bin/python" -I -B foundation-smoke.py
)
```

Include its contents/hash in the report. Never use the workspace overlay or a
source path for this proof. This is foundation installation proof; installed
Chat and generic CLI entry-point acceptance remain separate later obligations.
Record exact commands/results, wheel/sdist hashes, tool versions, environment,
counts, skips, baseline failures and protected-file preservation in the report.

## Handoff and stop conditions

Stop before editing if approval/API/base pins are absent or branch/board disagree.
Stop for scope expansion, unresolved contract ambiguity, dependency cycles, required
frontend imports, unrelated lock changes or a need to modify existing source/
tests outside the expressly allowed cohort test and artifact checker.
Do not implement deferred features, invent new defaults or weaken security behavior.
Report failures/skips and partially completed work honestly; do not self-approve.

After required checks, commit only allowed paths and provide the candidate full
SHA/diff, authority digests, test/install receipts and limitations. Stop for a fresh
read-only independent validator reviewing API-01–API-06 and the exact directive.
A changed candidate requires fresh validation. No automatic remediation loop,
phase closure, maintainer acceptance or external delivery follows from this unit.

# C2 bounded tag-component correction

Finding **INGEST-C2-VAL-001**, medium, from the fresh review of `120def19`:
the standards parser splits tags without rejecting empty components, allowing
`py3--any` and `py3-none-` to match equally malformed wheel declarations.

Correct only the harness tag-consistency validation in `manifests.py`, appended
regression assertions in its existing test module, and corresponding README and
evidence. Add explicit syntactic checks for nonempty interpreter/ABI/platform
components and compressed-tag members before accepting targets or wheel tags.
Keep the approved parser for version/requirement/marker semantics. Preserve valid
universal, native and compressed tag positives and all prior test bodies.

This is a mechanical declaration-validation correction within the unchanged
approved test-only directive and continuation. The builder may perform it; no
storage data, package ownership, guard architecture, actual dependency operation
or production behavior changes. All execution and qualification flags stay false.

Verification: reproduce the actual unfixed call assertions in both modes; corrected
empty-component and compressed-member cases must refuse under the guarded real
parser. Rerun minimal normal/-O, explicit selector, frozen manual flows, private
root-rule static checks, administration, scope and preservation. Commit a stable
correction; a fresh read-only validator reviews the numbered delta first and then
the full bounded C0/C1/C2 aggregate. Setup failures earn no rejection credit.
The first report remains immutable history. No 9.5/full-readiness advancement,
actual A0–A4 effect, UAT, acceptance or delivery follows. Stop after two unsuccessful
correction cycles under repository policy; no automatic council is authorized.

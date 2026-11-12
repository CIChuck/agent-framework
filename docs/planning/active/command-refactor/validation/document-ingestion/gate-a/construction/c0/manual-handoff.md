# Manual C0 foundation handoff

The [C0 scope](implementation-scope.md) and [builder evidence](builder-evidence.md)
cover only offline controls. This version cannot run actual A0–A4 qualification.
Independent implementation validation is pending. Do not use an application YAML,
existing store or production project as the private unit project.

The exact source is `f6ef86491a88464bfc07cf2aabeb68d7e596e4de`.
The [committed harness manifest](harness-manifest.json) SHA256 is
`50e1d67cc01dae457155e11e1b79394975d7b18b89373117932b905b11cbbdeb`.
Bootstrap SHA256 is
`70e03f2215282e2d4aa6fd0a58161ce0b9858981a114caba49f4826f5833599c`.

Qualified base interpreter:
`/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13`
SHA256 `e2adf1814122d8b26166917ef7d294d7426963e0f59e28d0d5aef773f67c4bb0`.
No working `.venv` is used.

A retained read-only committed harness export is currently at:
`/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-c0-build-ffm98ttz/formal/source/tests/readiness/ingest`.
It is temporary scratch. If unavailable, export the 29 exact selected blobs from
the recorded commit into a new private directory and verify every blob/SHA against
the manifest. Do not copy the dirty working tree or generate an unapproved manifest.

For an offline selftest, create a new, empty private output directory outside this
checkout. Then substitute explicit paths into:

```text
<base-python> -I -S -B <verified-export>/bootstrap.py selftest --harness-manifest <committed-manifest> --harness-manifest-sha256 50e1d67cc01dae457155e11e1b79394975d7b18b89373117932b905b11cbbdeb --scratch <new-empty-private-output>
```

Repeat with `-O` and a different empty output directory. There are37 distinct
cases in this C0 source. The tests use their own disposable project/store-shaped
fixtures and in-process fake transport; they call no actual model or store.
Output is PASS/FAIL for C0 only, never upstream readiness.

The [source README](../../../../../../../../../tests/readiness/ingest/README.md)
provides preflight/init/frozen-copy/control command syntax. The manual demo in the
builder evidence is already terminally stopped; use a fresh unit project/run ID
for another demo. Real pipeline adapters, dependency/model activation, human
acceptance and delivery remain separate gates.

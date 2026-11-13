# Private resolver-tool profile — proposed

[Exact manifest](private-resolver-tool-profile.json), SHA256 `f81bc1edc54635a51dcb720fe6cc82e990affd85b73fc75c5b69be91698bffe6`.

Download one lock-pinned `packaging==24.2` wheel: **65451 bytes**, one request,
no retry/redirect/resolver/source build. Inspect hash/RECORD/licenses/startup files
before private extraction and execution. This supplies the standard Python version,
requirement and environment-marker parser for offline dependency-resolver tests.

All target/cache/output paths are private. No working .venv, package/config/lock,
store, model or LM Studio change. No actual Docling installation or A0–A4 execution
is activated by this profile.

Separate approval is required by the reviewed directive: “Required private validation
tools need their own exact activated offline manifest; do not borrow .venv.”
The earlier five-wheel typing profile did not include this resolver helper.

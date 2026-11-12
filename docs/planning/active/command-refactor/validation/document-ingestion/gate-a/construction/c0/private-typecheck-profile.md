# Proposed private C0 type-check profile

Status: **NOT ACTIVATED**. [Exact manifest](private-typecheck-profile.json),
SHA256 `329f572b587c5998a4b8e96e6cfda8605a69f2bce6cbe4637fa191394300a568`.

Download exactly five wheels already pinned in the unchanged repository lock:
`mypy==1.19.1` (pure Python), `librt==0.7.7` (CPython3.13/macOS-arm64),
`mypy-extensions==1.1.0`, `pathspec==0.12.1`, `typing-extensions==4.15.0`.
Total **2,609,181 bytes**; at most five requests, no retries/resolver/source build.
Verify hashes, inspect package/license/RECORD/startup data, then use only the
named private target/cache with an explicit isolated interpreter and config.
Unexpected requirements, redirects, credentials or package behavior stop the profile.

This finishes the directive's required typing check for the new C0 harness. It
does not authorize Docling/upstream installation, actual model/conversion work,
production environment edits or package/lock changes. It never borrows `.venv`.
The existing private Ruff copy already supplies offline lint/format checks.

Separate approval is needed because the reviewed directive says: “Required
private validation tools need their own exact activated offline manifest; do not
borrow `.venv`.” The C0 permission otherwise excludes dependency installation.
No profile transfer, extraction or execution has been performed.

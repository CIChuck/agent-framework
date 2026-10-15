# SEC-002 implementation

Two parity tests now load an independent static fixture containing the original
50 registered command/alias names plus both fallback-only names (52 total). The
legacy AST parser and file dependency are removed; required-name/count and
registry-subset assertions remain. Fixture provenance pins the base source and
fixture hashes. No runtime source or deprecated-folder files changed.

All 30 compatibility tests pass at e5a3066c with the entire private legacy
memory directory unavailable, restored in finally. Ruff, Mypy, board, render
and whitespace checks pass. Documentation lifecycle exits1 for two existing
broken colon-line links in the unchanged SEC-001 report; no new failures.
That earlier report is preserved byte-for-byte. Receipts pin final candidate,
explicit guarded environment, product before/after hashes and raw output hashes.

Provider rotation/revocation pending; no folder deletion, external requests,
new secrets, broad cleanup, push or history rewrite.

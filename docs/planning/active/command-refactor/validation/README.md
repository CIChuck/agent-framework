# Imported command-refactor evidence

These receipts, pinned manifests, scripts and reviews were imported intact from
the source commit recorded in [the reconciliation manifest](../reconciliation/import-manifest.json).
They describe the source checkout and its dirty-input/environment controls.
Absolute source paths and historical branches inside reports are provenance.
They do not by themselves validate product code in the current Agent Framework
checkout. Current planning lives in `agent-framework` on `feature/command-refactor`.

Preserve the original receipts and JSON snapshots. Do not run capture/control
scripts here into their historical output paths: they would overwrite evidence
with a different baseline. Future local checks need a separate output location,
exact local source pins and fresh authority. The reconciliation manifest lists
source/test hash matches, differences and missing paths for the earlier TUI
transfer, not the current checkout.

The [2026-11-06 local continuation](local-2026-11-06/README.md) records a new
comparison and local checks separately. It does not overwrite historical receipts
or carry their review verdicts forward.

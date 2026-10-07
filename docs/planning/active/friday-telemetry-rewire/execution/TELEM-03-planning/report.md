# TELEM-03 proposal preparation evidence

Status: prepared proposal; not approved, READY or VERIFIED. Date: 2026-10-06.
Preparation revision: 4ca9baecdcdcf26fc5e8055b326c3a54cda36cb7.

The maintainer authorized directive preparation with "proceed". This work changes
only proposal/index/log/board metadata; no product source, tests, runtime settings,
lock, dependency, accepted authority/evidence or unrelated dirty payload is changed.
[CD-003](../../directives/CD-003-safe-llm-metrics.md),
[contract](../../telem03-contract.md), [profile](../../verification-profile-TELEM-03.md)
and separate [WVR-005](../../validation/WVR-005-telem03-lint-disposition.md) await
explicit decisions. The [manifest](../../authority-manifest-TELEM-03.yaml) pins
22 controlling inputs and 28 permitted future product paths.

## Fresh static baseline

A private tracked snapshot omitted 267 protected tracked runtime paths before
checkout. No original dirty/runtime payload overlay, product import, SDK/exporter/
channel activation, provider call, pytest collection or behavioral test occurred.
The [static inventory](source-inventory.md) and [AST/hash data](source-inventory.json)
freeze current APIs and construction paths. Missing new-module checks are future
candidate obligations, not silently labelled baseline passes.

| Check | Actual result |
| --- | --- |
| Board validate | Exit 0, 24 tracked tasks |
| Board next | Exit 0; memory-v2 awaits approval at higher priority; this session explicitly directs telemetry preparation |
| Board show friday-telemetry-rewire | Exit 0; started/granted on named branch, TELEM-03 preparation gate |
| Documentation lifecycle | Exit 0, 456 Markdown files |
| Native uv lock offline/check/no-download/no-build | Exit 0, 201 packages; no lock write |
| Root Ruff JSON | Exit 1, exactly 327 identities matching historical WVR-004; no current exception is approved |
| Mypy, 8 prospective existing source files | Exit 1, two no-any-return errors in adapters.py:325/328; explicit CD-003 correction required |

Each [raw compressed receipt/log](receipts/) preserves actual commands, cwd,
revision, allowlisted environment, timestamps, exits and tracked-before/after result.
All baseline command receipts report tracked_unchanged=true. Raw Ruff includes all
identities; its exact comparison is retained. pricing.py's existing whole-file
ignore is visible in inventory; the proposal requires removal, not a typing waiver.
Existing source/class AST/archive/17 lint-config hashes match the proposed scope.

## Proposal metadata checks and preservation

Final proposal board/dashboard, documentation links, manifest/path integrity,
whitespace and exact root-lint comparison are checked in a separately overlaid
isolated snapshot; receipts are retained under receipts/. Those static checks do
not establish behavioral correctness or independent proposal readiness. Final proposal board validate, dashboard render --check, documentation lifecycle
(462 Markdown files) and git diff --check each exit 0. Root Ruff again exits 1
with the exact 327 identities; integrity/preservation checks pass. The final
planning commit/evidence manifest identifies exact stored artifacts.

Original nonprotected dirty files, deleted family-tree.md, untracked tool-manifest
packet and docker audit tree remain separate. Board/dashboard metadata uses clean
index-only versions excluding the unrelated user row/events; the worktree retains
that row/events. Accepted unit authority hashes and all package source/test inputs
are unchanged. No branch push, merge, external service activation or live validation.

Next: explicit CD-003 scope and separate WVR-005 decision, required fresh review of
renewed lint authority and approved-authority reconciliation, then fake pre-build
behavioral probes before construction. Stable product commit and fresh independent
unit plus aggregate validation are mandatory future gates.

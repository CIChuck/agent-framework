# Planning-document transfer to Agent Framework

Date: 2026-11-05
Authority: Maintainer explicitly requested moving the planning documents from
TUI back to Agent Framework, with no source inspection, evaluation or changes.
Current planning folder: `agent-framework`
Current branch reference: `feature/command-refactor`

## Documents transferred

The complete Friday TUI planning packet, including the previously uncommitted
vision/PRD and decision drafts, is copied into `docs/planning/deferred/friday-tui/`.
Current command-first planning documents and their review/provenance records are
also carried over, with working-folder references corrected. Byte-identical
files are left alone. No `.py` file is copied or modified. Document snapshots
containing historical evidence are copied as opaque artifacts, not executed.

Original source planning documents remain in the TUI folder as safety copies.
Only the destination planning tree changes. Destination overlaps are preserved
in `destination-before.tar.gz`; the existing destination backlog working draft
is preserved verbatim in `destination-backlog-before.md.txt`. Its CMD-F11 row
and paragraphs remain in the current backlog.

## Authority and limits

The latest maintainer direction supersedes the earlier TUI-folder consolidation.
Historical approvals, reviews, implementation/UAT claims and receipts retain
their original context. The local board's lifecycle/authority values are not
promoted by this transfer. TUI construction remains deferred. The import grants
no design approval, implementation authority or source-code verification.

## Verification

The transfer manifest records every source document hash, destination overlap
and final document hash, plus excluded non-document files. Checks are confined
to planning-document bytes, relative navigation and preservation of working
drafts. No product source, tests, package metadata, configuration or lockfiles
are read, evaluated, run, changed or merged. No runtime tests or repository
validation scripts are executed. No files are deleted from the source folder.

# CDR-004 directive readiness review

CHANGES_REQUESTED

Candidate: `c3a4c6c68d345f4fe1fe58b001740ad88003d848`; authority delta from `325a0e52f5b292f27f6ecd81fc821097e8405349`. Reviewer: fresh-context agent `/root/cd001_a03_reviewer`, GPT-6 family (exact runtime version unavailable), 2026-10-05. Mode: read-only authority readiness. No shared builder context or prior review conclusions were used. References below are relative to the frozen checkout.

## CDR-004-F01 — medium: external-service manifest omits approved PyPI setup exception

`docs/planning/active/friday-telemetry-rewire/authority-manifest.yaml:39-40` declares `external_services: none`, permitting only synthetic loopback fixtures. Yet the approved `remediation/REM-002-verification-directive.md:31-40` and `verification-profile.md:69-74` expressly permit frozen, integrity-checked public PyPI downloads, without credentials, solely for a separate temporary Python 3.10 environment. The A03 amendment reference at manifest lines 41-42 does not make its explicit external-services declaration accurate.

The independent-validation policy requires reconciliation of conflicting authority (`docs/reference/policies/independent-validation-policy.md:64-66`) and exact permitted external effects in frozen review inputs (lines 108-119). The inconsistent metadata risks an executor or downstream validator applying the wrong network boundary.

Required fix: record this precise, already-approved provisioning exception in `authority-manifest.yaml`, while preserving credential-free execution, no interpreter download or dependency re-resolution, and no vendor/live traffic during tests. Freeze a new authority candidate and obtain a fresh readiness review. Reverify its hashes, docs-only delta and preservation checks; no product regression tests are needed for this metadata correction. This does not require a new maintainer scope approval. Product source/tests/config, lock, package metadata and shared environment remain outside the correction scope.

## Remaining review checks

All twelve request-pinned hashes match. HEAD is the requested candidate, status is clean before and after, and SHA-256 hashes of all 2,086 tracked files are unchanged (`pinned-hashes.json`, `before.json`, `after.json`). The complete eight-file delta changes planning/authority/board artifacts only (`authority-delta.patch`). Board and packet keep the initiative started with granted authority, validation pending and readiness preceding execution.

The exact root importlib invocation preserves both approved live exclusions and root testpaths; the Chat helper path addresses current bare sibling imports. Base/candidate collect-only runs, full required gates and retrospective comparison remain mandatory (`verification-profile.md:10-35,127-145`; `CD-001-local-telemetry-assembly.md:104-128`). No default-root failure is erased.

The three named nodes use the existing synthetic `ThreadingHTTPServer(("127.0.0.1", 0), ...)` fixture with shutdown/close/join (`packages/friday-chat/tests_chat/test_llm_adapter_migration.py:338-351,375-445`). REM-002 limits privilege to those nodes, requires the guard and isolated credential-free environment, and retains nonzero broad-suite results (`REM-002:22-30`; profile:76-85).

Python 3.10 setup is limited to an existing interpreter, frozen supported lock artifacts and a separate environment; incompatible lock resolution must stop (`REM-002:31-40`; profile:69-74,115-123`). `uv.lock:1-15` declares >=3.10 and a <3.11 resolution branch; this is no runtime compatibility claim. Required minimum-version typing/syntax/API evidence remains mandatory.

Lint and timing exceptions remain unapproved, baseline failures remain failed, and narrower successes cannot replace broad gates (`REM-002:69-79`; profile:138-145). No waiver or product behavior change was introduced.

Only read commands, hashing and review-artifact writes under `/private/tmp/telem-01/CDR-004` were performed. No product tests, collection, installation, downloads, source/docs/test/board/Git mutations, original application state, credentials or vendor traffic were used. Static readiness cannot establish implementation VERIFIED, successful executable gates, completion or acceptance.

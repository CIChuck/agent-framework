# INGEST-001 — existing-store upgrade policy decision

Maintainer: Chuck Russell. Recorded on2026-11-10.

The maintainer explicitly answered the existing-store upgrade question:

> Require an explicitly configured fresh store; preserve the old files and keep /read available (Recommended)

This selects the fresh-store-required policy for an existing store without
embedding identity, beyond the earlier testing-only decision. No legacy mode,
automatic alternate path, stamping, reset, migration or re-embedding is selected.
The corrected REM specifies the request mechanism and root-state/operation
matrix, with `/read` independent of Memory/embedding readiness.

This records the policy choice only. The full REM remains proposed and must meet
the separately authorized council gate. No construction, gate-A execution,
installation, actual store creation/reset/inspection, human acceptance or delivery
is authorized by this decision. Existing local files remain untouched.

# WVR-001: proposed baseline PTY timing exception

Status: Proposed; maintainer approval not yet granted.
Owner on approval: repository maintainer.
Date proposed: 2026-10-05.
Scope: TELEM-01/CD-001 and its bounded REM-001 revalidation only.

## Exact exception

Permit the otherwise mandatory full Chat/telemetry test run to retain only the
unchanged baseline failure:

`packages/friday-chat/tests_chat/test_reorganization_terminal.py::test_provider_free_pty_acknowledges_before_bounded_progress_completes`

The test's 0.8-second startup acknowledgement deadline failed on independently
executed base and frozen-candidate checkouts, including a warm rerun. The
validator's evidence must support this decision; the builder cannot grant it.
This exception acknowledges that the startup timing criterion is not verified
in this execution environment. It neither weakens the test nor changes its
source or deadline.

## Conditions

- The test file is unchanged from base `2155a0fc51f5b20dea4e35c6cfc70f1d52002735`.
- A fresh validator reruns the actual test on the remediated candidate and
  reports its result, rather than omitting or marking it passed.
- All other mandatory checks and AC-01 through AC-05 have independent evidence.
  VAL-001-F01 is fully remediated; this waiver cannot cover a source defect.
- TERM/NO_COLOR controls and localhost fixture permissions are reported
  explicitly. No new failing identifiers or failures caused by the remediation
  qualify for this exception.
- The final report retains the unverified timing risk; no live/exporter,
  performance, release, merge, or deployment readiness is inferred.

## Follow-up and cleanup

Follow-up: `TELEM-PTY-BASELINE-01`, to reconcile the PTY test's startup deadline
with a controlled environment before whole-initiative closeout. The maintainer
must separately authorize any test or infrastructure change. This exception
expires at TELEM-01's remediation review and does not carry into later units,
aggregate initiative acceptance, delivery, or release. If the test passes on
revalidation, record the evidence and do not invoke the waiver.

Approval must be explicit and recorded with maintainer, date, reason, scope,
validation, and this follow-up. Changing controlling authority requires a fresh
review; the current VAL-001 result cannot be relabeled VERIFIED using this draft.

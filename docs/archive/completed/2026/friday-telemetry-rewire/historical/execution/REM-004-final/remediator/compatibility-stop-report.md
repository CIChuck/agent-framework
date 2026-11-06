# REM-004 remediator compatibility stop

Separate remediator: `/root/rem004_remediator`. Source review began at approved authority `559ae9ffb246ef61ca3f19119aabaa79d41f4dcc`. All 16 controlling manifest pins matched; the 80 live-lint file baseline hashes matched; all four additionally permitted regression files existed. Construction was released by the controller only after fresh approved-authority READY. The controller subsequently recorded readiness in metadata-only HEAD `1718ed21f6b60c9c51edfcdb288853be557cb9f3`.

## Exact stop

R4-06 requires preserved public variance, forbids generic API drift and requires zero live Ruff findings without new suppressions or artificial compatibility mechanisms. `packages/friday-cli/src/friday_cli/commands.py:74` currently declares invariant `CommandRegistry(Generic[T])`; `T` appears only as input to `execute(context:T)`. Replacing only that class header with `class CommandRegistry[T]` causes inferred contravariance.

The isolated installed-Python 3.13.10/mypy probe uses the exact original module text and an otherwise identical PEP 695 variant. Its consumer attempts `CommandRegistry[Parent]` assignment to `CommandRegistry[Child]`. Original declaration rejects the assignment; PEP 695 accepts it. Mypy reports only the expected original rejection at line 6. This is a demonstrated public typing-contract change, not a hypothetical risk.

Ruff 0.14.10 still reports UP046 for both `TypeVar("T", covariant=False, contravariant=False)` and `TypeVar("T", infer_variance=False)` with the original generic class. Neither meaningful invariant declaration resolves the mandatory lint gate. No phantom member, artificial base, suppression, cast, dependency/configuration change or public generic conversion was attempted.

Evidence: `../runs/remediator-probe-01/variance-types.{json,log}` and `variance-02.{json,log}`; exact private probe programs are `variance_type_probe.py` and `variance_probe.py`. The former runner wrapper exits zero because it records a deliberate negative mypy probe whose inner exit is one. The latter likewise records inner Ruff findings. Neither is represented as a required candidate gate passing.

## Preserved partial changes

`compatibility-stop.json` pins the six allowed changed files and `partial-changes.patch` freezes their current diff:

- Agent conftest snapshots decorator declarations and restores them through finally.
- Web validator classifies literal IPv4/IPv6 addresses before DNS and applies the existing private-address policy; domain resolver policy is unchanged.
- Reader tests force the exact optional import unavailable, distinguish installed-library invalid-container errors, and add valid synthetic reads.
- Web tests add resolver-independent literals/overrides, mixed domain answers, unchanged resolver-failure policy, and transport-before-rejection sentinels.
- PTY test adds finite bootstrap readiness, parent trigger, unchanged 0.8-second post-trigger acknowledgment and one-second work delay, bounded kill/reap, and descriptor cleanup.

These are uncommitted partial edits, not a completed implementation. Product pytest, new regression before/after runs, final changed-file lint, response-branch typing fixes, the 133 live finding remediation, aggregate checks and independent product review have not run. The new tests have not yet been validated. The deterministic runtime registry preservation regression is not yet added.

## Preservation and next gate

All four accepted archive files retain their original hashes. Original dirty config, deleted family tree, security directories, queued tool-manifest work and unrelated board/dashboard work were not edited by this remediator. No original runtime state, credentials, provider/exporter, real network, synchronization, installation, staging or commit was used.

Construction stopped when the actual variance conflict was demonstrated. The next gate is a precise controller/maintainer compatibility decision under R4-06. Current authority permits neither silently accepting contravariance nor hiding UP046. Further authorized unaffected work requires controller reconciliation of the directive stop.

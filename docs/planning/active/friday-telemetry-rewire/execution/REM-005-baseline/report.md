# REM-005 true pre-edit baseline

Separate remediator reproduced all five original VAL-009 findings at frozen1547fae
before source writes. Original fake, tool, closure and schema probes reproduce
F02–F05. The separately approved owned SDK probe reproduces F01 with one incorrect
foreground parent; owned resources close and the global provider stays unchanged.
F04 also reproduces independently at the true unit basee6209e3.

[Raw receipts and hash manifest](artifact-manifest.json) preserve helper/source
hashes, stdout/stderr, commands/cwd/allowlisted environments and original attempts.
These are pre-build findings, not successful-product verification. CDR-020 READY
and all five reproduced baselines preceded controller source release.

# Friday alpha3 repository version bump

Status: started. Implementation authority: granted by Chuck Russell.
execution_phase: closeout; validation_state: verified.

Bump all 17 projects and their exact internal pins to 0.1.0a3, with current
runtime/release helper version expectations synchronized. Preserve historical
records and third-party dependency resolutions. [Authority](authority.json),
[construction directive](directives/CD-REL-A3-001-version-bump.md).

Independent review: [VERIFIED source candidate 8b85bd91](validation/report.md).
191 focused tests and all ten required checks passed.
Production publication completed: all 17 distributions / 34 files are live on PyPI, hashes match, and the clean production-only install and smoke checks pass. See [release evidence](../../../reference/releases/friday-package-cohort-0.1.0a3-release-evidence.md).
Next gate: maintainer lifecycle closeout; PyPI delivery is released and verified.
The original version-only unit remains independently verified. Publication authority is recorded separately in [publication-authority.json](publication-authority.json); no GitHub release or source push is included.

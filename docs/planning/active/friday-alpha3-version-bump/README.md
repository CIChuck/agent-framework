# Friday alpha3 repository version bump

Status: started. Implementation authority: granted by Chuck Russell.
execution_phase: closeout; validation_state: verified.

Bump all 17 projects and their exact internal pins to 0.1.0a3, with current
runtime/release helper version expectations synchronized. Preserve historical
records and third-party dependency resolutions. [Authority](authority.json),
[construction directive](directives/CD-REL-A3-001-version-bump.md).

Independent review: [VERIFIED source candidate 8b85bd91](validation/report.md).
191 focused tests and all ten required checks passed.
Production publication is now explicitly authorized. [Release readiness](validation/publication/release-readiness.md): artifact/install checks pass; upload is blocked by an invalid PyPI token.
Next gate: configure a valid credential, upload the frozen artifacts, then verify registry hashes and a production-only install.
The original version-only unit remains independently verified. Publication authority is recorded separately in [publication-authority.json](publication-authority.json); no GitHub release or source push is included.

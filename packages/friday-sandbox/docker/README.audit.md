# Optional security audit assets

These assets are opt-in manual audit aids. They are not part of Friday startup,
installation, package builds or the default test suite. Publishing them does not
authorize executing scanner workflows or privileged host checks.

- `Dockerfile.audit` builds a separate sandbox-inspection image containing
  amicontained and deepce. Its comments show the restricted runtime invocation.
- `workflows/audit_2_nginx.yaml` describes a separate local nginx/scanner audit.
  It provisions containers and pulls images; the active scanning tasks depend
  on its human-approval gate. Review the full workflow before executing it.
- `docker-bench-security/` is an upstream Git submodule pinned by the parent
  repository's gitlink. Initialize it with `git submodule update --init --recursive`
  from the repository root. Host audit execution requires separate operator
  authorization. Its untracked reports stay local and are not included in the PR.

The Docker daemon was unavailable during publication validation. YAML loading,
workflow graph/approval ordering and shell syntax were checked; no Docker image
was built, no container was started and no scan was executed. Runtime behavior
and scan results therefore remain unverified. Ubuntu/scanner image tags and the
default deepce branch are mutable; pin digests/commit refs and verify downloaded
artifacts before relying on repeatable or trusted audit results.

Keep generated results under the ignored root `exports/` directory or the
submodule's local output paths. Do not commit host/container findings or secrets.

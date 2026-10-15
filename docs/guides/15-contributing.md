---
title: Contributing and maintaining guides
description: Workspace setup, focused checks, engineering authority and documentation maintenance.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Contributing and maintaining guides

The same release is published as multiple Python distributions. Work from the
monorepo root so shared dependency resolution and cross-package checks use the
workspace configuration. Read [AGENTS.md](../../AGENTS.md) and the canonical
[engineering policy](../reference/policies/repository-engineering-policy.md)
before changing contracts or runtime behavior.

## Set up a development checkout

Use Git, uv and Python 3.13.4+. Clone with your normal repository credentials;
the command below does not establish public/private access policy:

```bash
git clone https://github.com/CIChuck/agent-framework.git
cd agent-framework
uv python install 3.13
uv sync --all-packages --all-extras --group dev --python 3.13
uv run --no-sync python -c "from friday_runtime import RuntimeKernel; from friday_agent import InteractiveAgent; print('Friday imports OK')"
```

`--all-packages` includes every workspace member; `--all-extras` includes optional
integrations. Installation may need platform-specific system dependencies for
audio or execution backends; it does not authorize hardware, Docker or provider
calls. Configure only the integrations needed for your work.

Keep the shared `uv.lock` and aligned Friday versions intentional. An ordinary
later `uv run` can resynchronize the environment; `--no-sync` preserves the
prepared workspace/extra selection for checks. Do not install similarly named
unrelated distributions in place of the metadata's `friday-framework-*` names.

## Make a focused change

Inspect branch/HEAD and existing changes before editing. Preserve unrelated
work, ignored user data and state. Use a dedicated branch or isolated checkout;
stage exact paths rather than broad staging in a mixed worktree.

Keep cross-package behavior on public typed contracts. Product invariants need
explicit exceptions rather than assertion-only enforcement. Do not hide type
debt with broad suppressions. If a change needs an API fix, document the affected
callers and migration rather than making an example depend on private behavior.

## Run appropriate checks

From the root after setup:

```bash
uv run --no-sync pytest packages/friday-memory/tests_memory -q
uv run --no-sync pytest packages/friday-agent/tests_agent -q
uv run --no-sync pytest packages/friday-runtime/tests_runtime -q
uv run --no-sync pytest packages/friday-chat/tests_chat -q
uv run --no-sync ruff check .
uv run --no-sync mypy packages tests main.py
uv run --no-sync python scripts/check-documentation-lifecycle.py
git diff --check
```

Choose the narrow meaningful tests for the changed behavior; the examples above
show actual suite paths, not a requirement to run all four for a prose edit.
Root pytest discovery includes package `tests_*` and experiment test directories;
top-level integration suites are a separate invocation. Finance, Optimization
and Transcript do not currently have package-local test directories.

Repo-wide static/test checks can expose existing debt. Report that separately
from new failures and show focused evidence. An import smoke check is not a
substitute for persistence, security, cancellation or behavioral verification.
Live provider tests require explicit provisioning/authorization and must not be
run as a side effect of a documentation example check.

## Authority and review

The [development board](../planning/README.md) tracks scope, state, authority,
branch and next gate; its YAML is canonical. Before applicable generation, run:

```bash
uv run --no-sync python scripts/friday-dev-board.py validate
uv run --no-sync python scripts/friday-dev-board.py next
```

Inspect the selected packet and current maintainer instructions. A queued item
is not implementation authority. Product generation needs a started task,
granted authority and a bounded construction directive or an explicitly
maintainer-recorded permitted exemption. See the [task lifecycle policy](../reference/policies/development-task-lifecycle.md).

Applicable work is committed as a stable candidate and handed to a fresh-context
read-only validator with exact authority hashes, diff, acceptance criteria and
checks. `VERIFIED` is independent validation, not maintainer acceptance or
authorization to push, merge or publish. See the [validation policy](../reference/policies/independent-validation-policy.md).
Keep behavioral remediation bounded and independently re-reviewed when the
candidate or authority changes.

## Maintain end-user documentation

Use the numbered guides for technical explanations and operational recipes,
package READMEs for entry points, and reference specifications for precise
contracts. Historical plans are evidence of intent, not proof that an API ships.
Update the guide that owns a subject and link to it instead of copying a second
full reference into an appendix or feature list.

For each guide update:

1. Verify claims against current source, package metadata, schemas and command
   handlers. Distinguish framework capabilities from application integration.
2. Record `framework_version` and the actual `last_reviewed` date in front matter.
   Change metadata only after the substantive review.
3. Keep runnable examples complete, public-API-based and isolated. Label live
   operations and fragments with prerequisites and effects.
4. Compile Python examples, execute offline ones with synthetic data and check
   YAML through the owning parser when possible.
5. Check relative links/anchors and Markdown rendering. Do not link retired
   local absolute paths or advertise unavailable CLI commands.
6. State measured validation limits. A mock does not prove live provider behavior,
   a local model does not confer compliance, and telemetry does not redact logs.

The guide front-matter keys are `title`, `description`, `framework_version`,
`last_reviewed`, `status`, `audience` and `doc_type`. Current guides use
`status: current`; this describes the documentation basis rather than a release
acceptance decision. Update the index, outline and capability reference when
scope or implemented status changes.

## Submit useful review evidence

Describe the user-visible problem and resulting behavior, affected package
boundaries, configuration migration and meaningful checks. For docs, identify
the old misleading claim and current source contract. Report offline versus
live evidence separately. Do not attach credentials, raw user stores, content
exports or machine-specific absolute links.

Use the [repository](https://github.com/CIChuck/agent-framework) and
[issue tracker](https://github.com/CIChuck/agent-framework/issues) for current
contribution channels. This guide does not promise a separate discussion forum,
documentation domain, release schedule or community support SLA.
Friday is distributed under the [MIT license](../../LICENSE).

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)

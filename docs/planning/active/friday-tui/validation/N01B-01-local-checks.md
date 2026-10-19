# TUI-N01B-01 local construction checks

**Date:** 2026-10-18 (America/New_York)

**Branch/before-code source:** `feature/friday-tui` /
`9b24588676c3b84d62c262d4937f4b0d2b39fbfc`.

**Authority:** Maintainer-approved
[CD-TUI-N01B-01](../directives/CD-TUI-N01B-01-neutral-transcript-query-contracts.md).
This is builder evidence before independent review, not a `VERIFIED` verdict,
TUI acceptance or authority to push.

The only product/test changes are the new
`friday_runtime.transcript_views` module, the `friday_chat.transcripts`
compatibility facade, and one focused test file in each package. The neutral
module owns the three frozen query views and the four-method asynchronous
protocol. Chat re-exports the same four objects and retains its export result
and all query, persistence, handler and file-export effects. No package
metadata, dependency lock, workflow, CLI source or TUI package changed.

| Check | Local result |
| --- | --- |
| Before-code unchanged transcript/identity/`friday-cli` baseline | 171 passed at the prior planning source. |
| New contract/facade tests plus unchanged transcript, identity and `friday-cli` tests | 179 passed after final formatting. |
| Full `friday-runtime` suite | 339 passed with local loopback fixtures enabled. |
| Full `friday-chat` suite | 848 passed, 5 skipped, 1 existing deprecation warning with local loopback fixtures enabled. |
| Unchanged full `friday-cli` suite | 155 passed. |
| Ruff check, Ruff format check and Mypy on four changed product/test files | Passed. |
| `uv lock --check --offline`, board validation, dashboard and `git diff --check` | Passed. |
| Runtime/Chat wheel builds and isolated installed-package checks | Passed; details below. |

A combined Runtime/Chat/CLI pytest invocation stopped at collection because
both Chat and CLI contain a `test_display.py` module. Separate package suites
completed. The first sandboxed full Runtime/Chat runs had nine Runtime failures
and ten Chat failures plus three Chat setup errors, all at test fixtures that
bind `127.0.0.1` and received `PermissionError`. The same suites passed in
full when rerun with local loopback access. No protected test was changed to
work around either runner limitation.

Built the Runtime and Chat wheels and their local Friday dependency wheels
from this checkout into `/private/tmp/friday-tui-n01b01-wheels`. The Runtime
wheel contains `friday_runtime/transcript_views.py` and declares no
`friday-chat` or `friday-framework-cli` dependency. In a fresh Python 3.13
venv under `/private/tmp`, the eight local Runtime dependency wheels and their
declared third-party dependencies installed; `uv pip check` passed for 111
packages. From outside the checkout with `python -I`, the neutral module came
from the installed venv, while Chat/CLI packages were absent and neither
frontend was importable or loaded. After adding the five local Chat-side
wheels and their declared dependencies, `uv pip check` passed for 130
packages. The installed Chat facade's four query objects were identical to
the installed neutral objects; all four old Chat pickle global lookups
resolved, and `TranscriptExportResult` remained Chat-owned. The isolated
dependency resolver needed public package downloads because `litellm` and
`massive` were not in the offline cache; no live provider or credential was
used.

The unchanged Chat production transcript tests exercised fake and
framework-backed query stores, archived sessions, entries, context logs and
export behavior with disposable state. Source inspection found no pickle use
inside `friday-transcript` persistence. These observations support the
compatibility comparison; new pickle byte streams have a different owning
module by design and are not claimed byte-identical.

**Open gate:** Commit this exact candidate and obtain a fresh-context,
read-only independent review. No N01B-01 exact-source Ubuntu run, installed
terminal UAT, user acceptance or external delivery is claimed. The green
CI03 Ubuntu run predates this source change; any N01B-01 Linux workflow run
requires a separately authorized, reviewed push.

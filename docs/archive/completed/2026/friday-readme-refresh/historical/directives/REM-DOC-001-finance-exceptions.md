# REM-DOC-001 — accurate Finance exception documentation

Authority: the maintainer's approved17-README rewrite for precision and CD-DOC-001. This is a bounded low-risk documentation correction within that existing scope, not a new runtime feature or a request to normalize SDK exceptions.

Input: frozen candidate b6dad87b568aee3a81dc20e145bb2644e4796609; initial independent report validation/initial-review/report.md. Finding DOC-001 (medium) appears exactly once here.

DOC-001: packages/friday-finance/README.md currently implies typed provider timeout, not-found and authentication normalization. Source client.py raises MassiveAuthError only for a missing key; execute_query maps message text containing429 to MassiveRateLimitError, otherwise preserving the original SDK/transport exception. Declared Friday timeout/not-found types have no implementation raise sites. Readers relying on them could miss real failures.

Only deliverable change: replace the single Finance error-handling sentence with an accurate explanation of missing-key handling,429 message matching and propagation of other exceptions, including remote authentication/timeout/not-found failures. Preserve every code fence, installation command, unrelated README and all source/metadata/version/lock contents. Supporting changes may only record the finding, recompute that README hash and update task validation evidence.

Verify corrected prose against current client.py and the retained synthetic contract check; compile/link/render the READMEs, confirm code fences unchanged and the exact bounded diff, then commit a stable candidate for a fresh read-only delta and aggregate review. Existing successful offline scenarios remain applicable because their complete code is unchanged; the fresh reviewer may reproduce them. No product tests, provider requests, credentials, Docker, package publication or Git remote actions. Stop on any additional substantive finding or source change.

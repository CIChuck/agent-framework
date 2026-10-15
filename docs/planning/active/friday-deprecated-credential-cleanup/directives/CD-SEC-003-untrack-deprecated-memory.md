# CD-SEC-003 — untrack deprecated integration memory

Authorized by Chuck Russell: "Let's do that. Track memory and add it to .gitignore. I'll Remove it at my leisure." In context this accepts the preceding recommendation to UNTRACK the folder while retaining its local files. Existing task remains started/granted on security/remove-deprecated-credentials; current explicit instruction selects this unit while Langfuse stays queued.

Exact product scope: remove the 287 tracked tests/integration/memory/** entries from Git's index and replace the narrow retired-config ignore rule with /tests/integration/memory/. Never delete/move/modify the main checkout's local memory files. Packet/board metadata only otherwise.

Plan: record root preservation metadata; add anchored folder ignore rule; remove only this subtree from the isolated candidate index; commit stable candidate; validate; install targeted Git index entries and advance local branch without a working-tree deletion operation. No reset/read-tree/ordinary merge that would remove main-checkout data.

Acceptance: (1) zero candidate-tracked paths in this subtree; all local main-checkout files retain inode/size/mtime/mode; (2) entire subtree ignored, including a hypothetical new file; (3) 30 compatibility tests, board/docs/render, whitespace pass with the private candidate memory directory unavailable and restored in finally; (4) changed product paths are only anchored ignore rule and exact 287 removals; preserve unrelated staged/dirty/untracked work; (5) fresh-context read-only full unit review of stable candidate; record outcome before completed claim. Do not print deleted content/diffs, embedded keys or credential-bearing baseline copies.

Verification: existing private Python 3.13 environment, unchanged network guard, explicit clean environment and private HOME/TMP/cache, no installs/sync/inherited keys/live providers. Temporary directory rename for validation is confined to isolated private checkout; no main data moves. No new tests or runtime changes required.

Maintainer separately confirmed credential rotation/retirement; record that as maintainer-reported, not issuer-verified. Non-goals: local data deletion, other removed folders, other exposed artifacts, history rewrite, key use, push/merge/publication or acceptance of the whole initiative. Stop on local-file drift, scope expansion or regression.

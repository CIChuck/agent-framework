# SEC-003 index-only retirement

The candidate removes exactly 287 deprecated memory subtree entries from Git
and anchors /tests/integration/memory/ in .gitignore. No main-checkout local
file deletion/move/write occurred. Targeted changed-index updates and a
fast-forward branch-ref update installed the local candidate; all 287 original
local inode/size/mtime/mode records and 18 unrelated path states were preserved.
The whole folder is ignored, including new hypothetical files; zero descendants
remain tracked. All compatibility tests (30), board, docs, render and whitespace
checks passed with the private folder unavailable and restored. Credential
rotation/retirement is maintainer-confirmed; no issuer validation was performed.
No external publication or history rewrite.

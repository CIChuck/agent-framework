# SEC-001 bounded removal

Two deprecated credential-bearing artifacts are deleted; the retired config is
ignored and the existing `.friday/` rule protects the copied log. The active
compatibility comparison now uses the unchanged sanitized fixture. Its 406 active
option paths matched the original before removal. No runtime source changes.

Final guarded checks: config 17 passed; compatibility 30 passed; full Chat
828 passed, 5 skipped, 1 warning. Ruff, Mypy, board/docs/render checks passed.
Earlier failures were harness errors: sparse exclusions hid a product module,
OS restrictions blocked fixture sockets, and spawned children lacked the test
package parent on PYTHONPATH. Original receipts remain retained; the final suite
passes with the unchanged external-network guard and corrected import paths.

Remaining exposure: 52 legacy SQLite files, the Massive integration test, and an
archived tar bundle still contain known values. These 54 paths are outside this
bounded removal. Git history also retains deleted values. Provider rotation and
old-key invalidation are the maintainer's confirmed plan, pending confirmation.
No live provider requests, rotation, push, merge or history rewrite performed.

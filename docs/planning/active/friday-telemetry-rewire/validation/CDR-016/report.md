Storage note: this readable copy adjusts links to compressed receipts. The [original frozen reviewer report](reviewer-report.md.gz) retains exact reviewer bytes.

# CD-002 A02 proposal review

Verdict: **READY** for the explicit proposal approval decision only. No findings.
A02 remains unapproved and noncontrolling. This is not product VERIFIED, acceptance,
or activation authority.

Reviewer: `/root/telem02_a02_proposal_review`, fresh independent agent; GPT-6 family
(exact runtime model/version unavailable). Date: 2026-10-06. Review mode: read-only
frozen proposal delta plus existing approved controls and official source semantics.

Candidate: `db9223e68e11facc74d2b88853ab4c3a2eaeb17b`.
Base: `95949e49df7b55f8da391a47f6df67cc2ff8e5ce`.
The exact delta adds only `directives/CD-002-A02-native-retry-disable.md` (48 lines).
Proposal SHA-256: `88dfcd97f2580f23d103542e1e9db3baca3ed9fb6173cbb37a400de6d01e6889`.
`git diff --check` exits 0. [Exact diff](exact.diff.gz), [hash receipts](evidence.json),
[reproducible audit](audit.py.gz), and [numbered proposal](proposal.numbered.txt.gz) accompany this report.

The amendment is concrete and necessary. The current unit contract requires no
implicit retries (line 82), while limiting channel options to proxy disablement and
bounded message sizes (lines 162–164). A02 lines 17–24 require exactly one additional
fixed option, `grpc.enable_retries=0`, in both insecure and secure branches.
The Python <3.14 lock selection pins grpcio 1.67.1 (`uv.lock` lines 1618–1622).
The [version-pinned gRPC header](https://github.com/grpc/grpc/blob/v1.67.1/include/grpc/impl/channel_arg_names.h)
documents retry enablement by default and includes transparent and service-configured
RPC retries (raw browser lines 301–310). The [official retry guide](https://grpc.io/docs/guides/retry/)
confirms that transparent retries can remain without a retry policy and that disabling
retries at channel creation prevents both forms (browser lines 137–145).
Consequently, one application Export invocation and a finite deadline alone do not
establish the existing no-retry requirement. This conclusion is a source-grounded
prospective specification assessment, not a native retry experiment.

The boundary is preserved. All 17 manifest pins independently match; every pinned
control and the manifest itself are byte-identical across base, candidate, and current
control files. The approval record, WVR-004 identities/content/expiry, and listener
scope remain unchanged. A02 adds no product/test path, public API, user setting,
dependency, service config, reconnect/backoff policy, credential, TLS execution,
listener/effect, suppression, or waived gate. Existing CD-002 and separately WVR-004
approvals remain valid within their exact scope. [Authority excerpts](authority-excerpts.json)
record the current contract, directive, approval, and profile line evidence.

Verification is adequate for this bounded option amendment: A02 lines 35–42 require
exact option assertions in both mocked branches, one Export per batch, finite timeout,
`wait_for_ready=False`, no application retry loop, and actual intercepted loopback
target/options in the two existing successful/UNAVAILABLE collector nodes. The native
guard limitation, bounded cleanup, and mocked HTTPS scope are retained. These nodes
do not empirically prove every low-level retry race; source semantics plus exact
option construction are the expressly stated evidence boundary. No fault-injection
experiment or extra listener is required or granted. Future product verification,
all other current profile checks, and maintainer acceptance remain separate gates.

Before option implementation or native OTLP test execution, the controller must
record explicit maintainer approval of A02, reconcile exact contract/directive/profile
wording and current-unit authority hashes, and obtain fresh approved-amendment
readiness (A02 lines 26–31). READY here does not satisfy that later gate.

Controller-disclosed independent builder product work continues outside the paused
OTLP gate. Uncommitted product files and whole-worktree status were not inspected;
their changes do not invalidate this frozen proposal review. Only selected frozen
Git blobs, approved control documents, and official browser sources were read.
No SDK import, collection/test run, native channel/listener/provider, live/credential/
runtime read or copy, install/sync/download/build, protected checkout, original write,
stage/commit, or original environment mutation occurred. Review artifacts were written
only under `/private/tmp/telem-02/a02-proposal-review`.

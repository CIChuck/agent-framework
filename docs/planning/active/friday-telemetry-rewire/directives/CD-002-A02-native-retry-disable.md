# CD-002 A02: require native gRPC retries disabled

Status: proposal; not approved. Date: 2026-10-06.
Work unit: TELEM-02. Finding: T02-B01.

The approved contract requires no implicit retries but limits channel options to
proxy disablement and bounded message sizes. The owned exporter makes one public
unary call with a finite deadline and no application retry loop; this does not
establish that native transparent retries are disabled. The official
[gRPC retry guide](https://grpc.io/docs/guides/retry/) describes default transparent
retries, and the pinned [gRPC1.67.1 channel argument header](https://github.com/grpc/grpc/blob/v1.67.1/include/grpc/impl/channel_arg_names.h)
provides grpc.enable_retries with an enabled default. No native retry experiment
or external service was used to establish this specification conflict.

## Exact proposed amendment

Permit and require one additional fixed channel option, grpc.enable_retries=0,
for both insecure literal-loopback and secure-channel construction. Revise the
contract's exact option allowlist to grpc.enable_http_proxy=0,
grpc.enable_retries=0 and bounded send/receive message-size limits. This disables
native transparent/configured RPC retries and implements the existing no-retry
requirement. It is not a user-configurable retry setting. No service-config,
authority/hostname override, backoff, retry policy, reconnect option, environment
mutation or dependency change is added.

The controller must record explicit maintainer approval of A02, update the exact
contract/directive/profile wording and current-unit authority hashes, then obtain
fresh approved-amendment readiness before this option is implemented or native
OTLP tests execute. Until then the builder continues independent authorized work
and pauses the affected OTLP construction/test gate. Original CD-002 and WVR-004
approvals remain valid; this does not renew or expand the lint disposition.

## Required verification and preserved scope

Mock both channel branches and assert the exact approved options with retries0,
proxy0 and finite message-size limits; verify one public Export invocation per
batch, finite timeout, wait_for_ready=False and no application retry loop. The
two already approved native collector nodes must intercept and record the actual
literal-loopback target/options and deterministic successful/UNAVAILABLE results
with bounded cleanup. Real native fault-injection retry experiments are not required
or granted; source semantics plus exact option construction and those existing
nodes are the stated evidence boundary. HTTPS remains mocked.

No new product/test paths, public API, collector/listener IDs, external effects,
credentials, TLS activation, installs/downloads, package/config/lock changes,
source suppression, waived test/type/lint gate or acceptance is proposed. Exact
13 synthetic listener effects,327 WVR-004 identities/hashes/expiry, caller-owned
Chat injection and every other CD-002 requirement remain unchanged.

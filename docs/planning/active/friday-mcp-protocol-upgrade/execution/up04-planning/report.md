# UP-04 planning evidence

Status: Planning-only; product construction is not authorized.

UP-03 was independently VERIFIED and accepted by the maintainer. This packet
proposes 20 product paths (17 existing, 3 new), ten criteria and 20 required commands.
[Baseline inventory](baseline-inventory.json) references actual prior full checks;
those are historical UP-03 evidence, not newly run UP-04 tests. The source baseline
is 3fd5437088c5ddf5d68be3a2a097770c294cba6b; private acceptance commit changes only
process/archive files. [Stored artifacts](stored-manifest.json) retain lossless
raw receipts/stdout/stderr and probe source with decoded/stored hashes.

## Reproduced gaps and limits

The initial synthetic no-network probe failed due to a wrong exception import;
its full source/receipt/failure are retained. The corrected probe imports
MCPToolExecutionError from friday_mcp.client.base and exits 0. It uses the actual
modern base send/receive/request loop and public adapter cache API. It observes:
initial invalid structured output is rejected; explicit refresh fails; cached
old wrappers remain; invalid structured output is then accepted without its
former schema; malformed isError/content is classified `tool_error`; stop leaves
zero pending requests. Three tool calls were issued. Existing adapter Ruff is
clean. This is a builder planning observation, not an independent validator
verdict, live-peer test or proof of identical HTTP behavior. The source was not
pre-frozen before the initial run; both exact sources are now archived.

HTTP source inspection identifies a separate same-generation schema/header
binding requirement. Real modern stdio and both dated TLS HTTP profiles, controlled
races and emitted-header/call-counter proof are mandatory after approval.
The complete dated 2025 Tasks capture and both pinned schemas establish that
required-task tools must be excluded while Tasks is unsupported; do not project
that dated field into the modern schema or claim Tasks conformance.

## Current authority

The proposed directive, contract, profile and authority manifest are immutable
approval inputs. Current process state and board name UP-04 as planning only with
unit authority not_granted. Existing initiative state remains started/local;
accepted UP-02A/02B/03 and original control/report/source/ledger bytes remain intact.
No dependency/checker/product changes, public peers, external services, model calls,
ambient credentials, real stores or publication occurred during packet preparation.

## Planning checks and preservation

Guarded board validation/next/show, documentation lifecycle and rendered-board
consistency all pass with raw child exit0. This was planning validation only;
none of the proposed product tests was executed as UP-04 evidence. All19 captures
match decoded and compressed hashes. All original tracked packet inputs except
the named mutable process/log files are byte-identical to the accepted baseline;
all20 proposed product baselines and47 accepted UP-03 product/metadata hashes
match. The root mixed checkout is transferred with six unrelated path hashes,
two unrelated board tasks and three unrelated events preserved; root installation
checks will be retained privately. No remote publication is requested or performed.

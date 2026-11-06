# Independent quick-start review

VERIFIED

Reviewer: `/root/chat_quick_start_new_user_review`, independent Codex agent
(GPT-6 family; exact backend build not exposed). Review date: 2026-10-15.
Mode: fresh-context, full frozen-candidate documentation review, read-only.
No builder reasoning or conclusions were supplied as validation evidence. The
packet's executable checker was inspected before replay and its results were
independently regenerated. Builder reports were read only after that replay.
There were no shared-context exceptions, candidate edits, commits, delegation,
delivery or publication.

The reviewed checkout is `/private/tmp/friday-chat-quick-start`, branch
`docs/chat-quick-start`, at candidate
`6a83ad509b9f0cc43838e405a03610b16c74e7c1`. The exact review range is
`316749cc1584d5bff1ef8ae4358766ca0acecaac..6a83ad509b9f0cc43838e405a03610b16c74e7c1`.
The checkout was clean before and after checks. All 13 changed paths are within
the two deliverables, authorized initiative packet, board and generated dashboard.
The complete diff is retained in `candidate-diff.json` as base64-encoded UTF-8;
command output is JSON-encoded to preserve terminal output without introducing
trailing-whitespace log lines.

The frozen request is retained as `review-request.json`. Its hash, the exact
authority hashes, installed/source comparisons and commands are recorded in
`independent-results.json`. All six request-pinned authority digests match:

| Input | SHA256 |
| --- | --- |
| AGENTS.md | `02c6360f0e2532a3ea761d7ae228fb105231c60d447146ead69c01c6ff99d152` |
| docs/reference/policies/repository-engineering-policy.md | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` |
| docs/reference/policies/development-task-lifecycle.md | `7087fb62381cc8a46128bc6745476d1aa08e1d577b4c73340760657ae834fe2a` |
| docs/reference/policies/independent-validation-policy.md | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` |
| docs/planning/active/friday-chat-quick-start/authority.json | `6dd8c733f71595b136f91cbef62184169fbfd306c3bb48c974e2bb147782fc4b` |
| docs/planning/active/friday-chat-quick-start/directives/CD-QS-001.md | `0885fea33c042b734b2e4804207a4c521f9b9d97627ffd3cf1449e5e37b6b5d5` |

The guide SHA256 is
`b50c4b9e567d48af20d54d27b9d4c93653039ae4d80ddea683cf133ced06b755`.
Policies inherited from the base have identical candidate bytes; new authority
and directive inputs are pinned at the candidate above. Current source reviewed
includes root and Chat metadata, Chat configuration/display/CLI/runtime/adapters,
background/exit behavior, reorganization path assembly, canonical library
schemas/loading and embedding adapter behavior. Ten relevant source files were
also byte-compared with the installed alpha3 files used for replay; all match.

**UC1 newcomer assessment: PASS.** Following guide lines 65-97 establishes the
clone directory, compatible interpreter, complete editable workspace/extras,
activation and maintained executable. The command's all-packages/all-extras/locked
flags match local uv 0.11.3 help; metadata requires Python >=3.13.4 and supplies
`friday-chat = friday_chat.cli:app`. The user keeps that environment activated,
creates the ignored client directory and chooses a model-server path. The guide
supplies complete content and explicit destination names for models.yml,
config.yml, cli.yml and the launcher, generates friday.env with the selected
interpreter, then makes the launcher executable. Offline parsing and fake mode
precede the explicitly live checks and real session. No missing file-creation,
activation or launch transition was found within these stated prerequisites.

**UC2 newcomer assessment: PASS.** Guide lines 99-145 start in the user's existing
compatible, activated environment and own application directory. Quoted pip and
uv-add requirements pin the complete framework cohort including Chat. `python
-m pip` binds to the chosen interpreter; `uv add --active` is explicitly a
project dependency/environment operation, and the bare-venv uv-pip alternative
is distinguished. The shared instructions need no checkout-only templates or
scripts: the user saves the complete examples directly. The generated absolute
environment executable and script-relative client directory permit later
launches without activation. Application ignore rules, executable shell input,
private credential editing and the setup-only lifetime of CLIENT_DIR are clear.
Both UC1 and UC2 reach the same tested configuration and launcher behavior.

**Model serving, roles and memory: PASS.** The Ollama and LM Studio branches
identify local compatible bases with /v1, distinguish downloaded names from API
IDs and require the user's actual revision/model IDs. The Ollama startup/context
and LM Studio Developer/server/context instructions precede API listing and file
creation. Authentication alternatives and server-not-started conditions are
explained. Both complete libraries resolve ten chat roles and two embedding
roles through the owning parsers. Runtime source confirms mandatory maintenance
resolution, conditional compaction/router/smart-file use, default-pool regular
embedding selection and explicit maintenance embedding selection. The guide
correctly separates embedding vectors from chat text, dimensions from batch/cache
options, and availability probes from extraction/retrieval quality. Its migration
instructions avoid reusing incompatible collections. Config-relative library
paths and cwd-relative persistent paths match current assembly.

**Commands and documentation: PASS.** The shared launcher is usable with either
installation and either complete model-library choice. Source confirms alpha3's
environment runtime precedence, which the script explicitly normalizes. Both
model-library variants, complete runtime/display settings, generated environment
permissions/refusal to overwrite, default/explicit modes, paths containing spaces,
launches from another cwd, missing files and invalid arguments pass the replay.
A separate fake session with actual newline-separated greeting and /q input also
returns a deterministic response and exits successfully. The guide links the CLI
reference instead of reproducing its command catalog and explains new sessions,
stable stores, priming, normal shutdown and what successful recall does not prove.
The index adds the quick-start link and updates its document count consistently.

The following independently executed checks passed; detailed stdout/stderr and
exact argv are in `packet-replay/results.json`, `independent-results.json` and
`independent-command-receipts.json`:

- Three embedded Python snippets compile, four complete YAML examples parse,
  and sixteen Bash fences pass `bash -n`.
- Both model libraries load through the canonical/Chat/display owners and
  supporting-context/compaction validators. Non-started real assembly constructs
  extractor, compactor and persistent graph without adapter-gap diagnostics and
  resolves the intended private vector/transcript layout.
- Both preflight snippets execute with synthetic LiteLLM transports, producing
  the expected model/base routes, a nonempty chat response and vector, followed
  by asynchronous client cleanup. No socket is used.
- Missing credential, unknown profile and missing required maintenance-role
  cases fail as documented.
- Both model variants pass complete generated-environment and launcher tests;
  the additional actual-newline fake session passes independently.
- Both changed guide bodies render with readme_renderer without warnings;
  75 links are enumerated, including 64 local targets/anchors checked.
- Board validate, next, show and render --check pass; the task remains started,
  authorized on the named branch, pending independent validation. The generated
  dashboard matches the board.
- Documentation lifecycle validation passes for 621 Markdown files. Its internal
  uv-run subprocess is narrowly shimmed to the exact existing alpha3 interpreter,
  with no sync/install operation.
- Full `git diff --check` over the exact base..candidate range passes, and scope,
  hashes and pre/post clean status checks pass.

Reproduction uses only the existing alpha3 environments, with sanitized process
environment, synthetic local-only credentials, a private HOME/TMPDIR, disabled
telemetry and the inspected network/write guard. From the frozen checkout, run:

```bash
env -i PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  PYTHONDONTWRITEBYTECODE=1 \
  QS_CHECKOUT=/private/tmp/friday-chat-quick-start \
  QS_OUTPUT=/private/tmp/friday-chat-quick-start-independent-review/packet-replay \
  /private/tmp/friday-alpha3-pypi/production-install/bin/python \
  /private/tmp/friday-chat-quick-start-independent-review/replay-packet.py
env -i PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  PYTHONDONTWRITEBYTECODE=1 \
  /private/tmp/friday-alpha3-pypi/production-install/bin/python \
  /private/tmp/friday-chat-quick-start-independent-review/independent-checks.py
```

`replay-packet.py` is an unchanged copy of the candidate's inspected checker;
SHA256 `6628306b761ad290fffc5128edb9fc21835e0e6e388c4e85c53505fa577cca1d`.
`independent-checks.py` has SHA256
`027f335ffee9f322a8431ecfcf0347f63f59a3fe2ff27444cbc8942d79ed9cf6`.
The installed interpreter is Python 3.13.10; the renderer is the separate
existing tools environment named in the frozen request. Initial independent
helper attempts guessed a nonexistent source filename and selected TMPDIR
outside the guard's allowed output prefix. Only the external helper was corrected;
the final reproduced checks above pass. These were harness errors, not guide
defects or candidate remediation.

There are no numbered findings or unresolved mandatory violations. This result
is bounded documentation verification, not maintainer acceptance. No actual
install/sync, network, model download, real provider/model execution, hardware,
Docker or shared store was used. External reference reachability/current UI,
native optional dependency installation, model capacity/quality, real extraction,
persistent semantic recall, Windows/PowerShell and live endpoint readiness remain
outside the permitted review. The guide marks live operations and describes the
user checks needed for those limits. No broad pre-existing product/guide review
or product test suite was undertaken.

# Independent hosted OpenAI quick-start review

VERIFIED

Reviewer: `/root/chat_hosted_openai_review`, fresh independent Codex agent
(GPT-6 family; exact backend build unavailable), 2026-10-15. Mode: read-only
hosted-amendment delta plus bounded aggregate/new-user review. No inherited
builder reasoning, shared-context exceptions, candidate edits, remediation,
commits, delegation, acceptance or external delivery occurred. The packet checker
was inspected and replayed independently before builder results were considered.

Candidate: `89ad03a70d1c2ff9d5e8a2048f3491bb7c74903d`, branch
`docs/chat-quick-start`, checkout `/private/tmp/friday-chat-quick-start`.
Exact delta: `b08f1de43cd4a898631d469cbbfac3bf8b2e588c..89ad03a70d1c2ff9d5e8a2048f3491bb7c74903d`.
Exact aggregate: `316749cc1584d5bff1ef8ae4358766ca0acecaac..89ad03a70d1c2ff9d5e8a2048f3491bb7c74903d`.
All seven frozen request authority hashes match current bytes. AGENTS,
engineering/lifecycle/independent-validation policies, authority.json,
CD-QS-001 and ADD-QS-001 were read. The checkout was clean before and after;
HEAD remained the candidate. The 11 delta and 36 aggregate paths remain in the
authorized guide/navigation, initiative packet, board and generated dashboard.
There is no package/source/test/dependency/version/script change.

The entire quick start was read as a new UC1/UC2 user choosing hosted OpenAI.
Both installation paths still converge on complete user-owned models.yml,
config.yml, cli.yml, environment and launcher contents. Hosted prerequisites
explicitly require API credentials/access/usage allowance and let users skip
Ollama/LM Studio. The maintained executable, compatible Python, full cohort,
uv-project versus bare-venv behavior and subsequent launch transitions remain
clear. Local examples retain their model-ID/revision/context/authentication
instructions. The neutral `chat_model` and `memory_embedding` profile names
resolve all ten chat and two embedding bindings for all three complete libraries.
The mixed hosted-chat/local-embedding assembly also resolves the intended routes.

The hosted model, authentication and embedding claims agree with official OpenAI
pages opened on this review date. The selected GPT-5.4 mini snapshot and default
`none` reasoning effort appear on its [model page](https://developers.openai.com/api/docs/models/gpt-5.4-mini),
which lists Chat Completions. GPT-5.4's temperature restriction is documented in
[parameter compatibility](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.4).
Installed LiteLLM accepts the documented temperature and maps `max_tokens` to
`max_completion_tokens` for the exact snapshot without a provider request.
[Authentication](https://developers.openai.com/api/reference/overview#authentication)
supports the environment/key-management approach. The embedding model is
documented on its [model page](https://developers.openai.com/api/docs/models/text-embedding-3-small);
the [embedding guide](https://developers.openai.com/api/docs/guides/embeddings)
confirms its default 1536 dimensions. Friday's owning schema exposes batch/cache
controls rather than dimensions. The guide distinguishes alias provenance,
vector-space compatibility, local database paths, provider processing and API
usage. Account access, live availability and actual model quality are not inferred.

Independent checks passed:

- Unmodified current `validation/check-hosted-guide.py.txt` replay: 15 scenario
  groups, zero errors. All three model libraries pass owning-schema/display
  resolution, non-started real assembly with no adapter gaps, mocked preflight,
  credential/profile/required-role rejection and generated-environment/launcher
  checks. Mixed hosted/local assembly and synthetic hidden-key export pass.
- Three Python snippets compile, five complete YAML examples parse, and 17 Bash
  fences pass syntax checks. Both guide bodies render without warnings; 85 links
  are enumerated and 70 local targets/anchors checked.
- Additional actual-newline greeting and `/q` interaction passes through the
  installed CLI with the hosted library. A fresh shell without the key fails
  even in fake mode. Synthetic tests confirm inherited-key preservation,
  environment-file assignment precedence and file-supplied key behavior in a
  new shell. These match guide lines 942-959. The launcher's explicit runtime
  environment normalization matches CLI source precedence.
- Source/install metadata agrees on alpha3, Python >=3.13.4, the aggregate all
  extra and `friday_chat.cli:app`. Sixteen relevant Chat/LLM/runtime source files
  byte-match the installed alpha3 files used for replay. Local uv help confirms
  the documented flags.
- Board validate/next/show and render --check pass. The task remains started,
  granted, local and pending this review. `next` names queued Langfuse awaiting
  approval; CD-QS-001 explicitly authorizes this maintainer-selected quick start.
  Documentation lifecycle passes for 625 Markdown files. Its sole uv-run board
  subprocess uses a narrowly matched private shim to the existing interpreter;
  no install/sync occurs. Both exact full-range whitespace checks pass.
- Prior independent full and introduction review trees are unchanged from the
  amendment base; the retained full-report digest matches. Their unchanged
  baseline evidence supports this bounded aggregate review; neither is treated
  as verification of the hosted delta.

Reproduction and exact stdout/stderr are retained outside the candidate in
`evidence.json`, `replay/results.json`, and the two complete diff JSON files.
Run with the existing environments only:

```bash
env -i PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  PYTHONDONTWRITEBYTECODE=1 \
  QS_CHECKOUT=/private/tmp/friday-chat-quick-start \
  QS_OUTPUT=/private/tmp/friday-chat-hosted-independent-review/replay \
  /private/tmp/friday-alpha3-pypi/production-install/bin/python \
  /private/tmp/friday-chat-hosted-independent-review/replay-hosted.py
env -i PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  PYTHONDONTWRITEBYTECODE=1 \
  /private/tmp/friday-alpha3-pypi/production-install/bin/python \
  /private/tmp/friday-chat-hosted-independent-review/independent-checks.py
```

Use a fresh private output directory for a fresh checker run: its scenario
directories are intentionally generated state. The independent helper records
22 passing assertions and 25 successful expected-result command checks.
Review artifact hashes:

| Artifact | SHA256 |
| --- | --- |
| Guide | `eedd970411de3cd3233d02427357b2ffb8fa9e97005b01c09f500cf714d26f5a` |
| evidence.json | `25a46bbe60abd36caa7ebc23e8a9adb2aba3cca73e9752d8eb3b3856a5a1bc4d` |
| replay/results.json | `306aea832d819420665d1d1eb319760b66fb98a12a2a3d6a49adf940864fd708` |
| replay-hosted.py | `6395f5f50451bb0cce3a17e0e6797b4670331f8ec6afdb23587a45e02fcfba34` |
| independent-checks.py | `729ddaeb0e7c64edd49c06bb3215f66d4c1458c1199fdc7b85e007d39debdbb5` |

No findings or violated mandatory requirements remain. Validation used sanitized
environments, synthetic credentials, private HOME/TMPDIR/stores and inspected
network/write guards. Official documentation browsing was read-only. No live
provider/account/model request, real secret, install/sync/download, hardware,
shared store or broad product suite was used. Actual installation on another
platform, native optional dependencies, live extraction/retrieval/persistence
quality and model capacity remain user-run/live-validation limits. VERIFIED is
documentation conformance, not maintainer acceptance or delivery authority.

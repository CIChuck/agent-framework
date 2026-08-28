# Friday Package Cohort 0.1.0a1 Release Evidence

- Evidence date: 2026-08-28
- Branch: `feature/friday-package-cohort-0.1.0a1`
- Artifact source commit: `fbe6e0e`
- Artifact directory: `dist/friday-package-cohort-0.1.0a1-fbe6e0e/`
- Status: published to production PyPI and post-publication verified
- Publication date: 2026-08-28
- Release tag: not authorized and not created

## Decision

The complete 17-distribution Friday family is published as one lock-step
`0.1.0a1` cohort. Every project version, internal dependency, optional extra,
self-reference, and exported runtime version uses `0.1.0a1`. The root
`friday-framework[all]` extra covers every other cohort distribution, including
`friday-framework-optimization`.

This evidence supersedes the rejected package-only Friday LLM and Friday Chat
artifact candidates. The maintainer explicitly authorized production PyPI on
2026-08-28. The exact files in the artifact directory above were published in
dependency order; TestPyPI was not used. A release tag remains a separate
authority gate.

## Dependency And Source Gates

- `uv lock --check`: passed with 204 packages.
- The yanked NumPy `2.4.0` lock entry was replaced by compatible non-yanked
  resolutions: `2.2.6` on Python 3.10, `2.4.6` on Python 3.11, and `2.5.2` on
  Python 3.12 and newer.
- Project metadata validator: 17 of 17 projects passed version, license,
  authors, README, URL, wheel-selection, and internal-pin checks.
- Cohort metadata/release-helper regression gate: 8 passed.
- Focused Ruff and mypy gates: passed.
- No framework runtime compatibility repair was required after the version and
  dependency alignment.

## Package And Repository Validation

The full runtime test pass preceded the final metadata/security-only commits;
the later focused gates revalidated the changed release contracts.

| Scope | Result |
| --- | --- |
| Friday LLM | 167 passed, 8 skipped |
| Friday Memory | 678 passed, 1 skipped |
| Friday Agent | 198 passed, 9 baseline failures |
| Friday Runtime | 42 passed |
| Friday CLI | 155 passed |
| Friday MCP | 31 passed |
| Friday Chat | 419 passed, 5 skipped, 2 baseline failures |
| Full repository with `--import-mode=importlib` | 2155 passed, 14 skipped, 15 baseline failures |

The 15 repository failures are unchanged baseline groups: nine Agent Copilot
mock/model validation failures, two Friday Chat PTY clear-screen failures, two
Runtime built-in-tool registration failures, and two Tools optional document
reader expectation failures. Default repository pytest and mypy still stop on
the pre-existing duplicate `test_display` module name. Repository Ruff still
reports 12 pre-existing findings outside the cohort changes. Focused changed-
file Ruff and mypy are green.

## Artifact Gates

- Clean detached worktree build: passed at `fbe6e0e`.
- Artifact count: 17 universal wheels and 17 source distributions.
- Custom archive validation: all 34 passed metadata, exact-pin, extras,
  resource, license, portability, and sensitive-content checks.
- `twine check`: all 34 passed.
- The definitive artifact bytes are identical to the fully exercised
  `28dbb69` build; the intervening source change only refreshed `uv.lock`, which
  is not included in these package archives.

The first cohort build exposed a tracked Moltbook registration response that
contained an apparent API credential, claim token, verification code, and an
absolute local path. The package file was removed and matching archived-doc
examples were redacted before the final build. The credential should still be
revoked at Moltbook because removing it from the current tree does not erase
history or invalidate it. Artifact directories ending in `be4ddef`, `dd4d8f3`,
or `28dbb69` are superseded and must not be uploaded.

## Clean Installation Gates

Friday Chat wheel installation was tested from the final-equivalent artifacts
without workspace sources on every supported interpreter:

| Python | Result |
| --- | --- |
| 3.10.19 | import, typed config, fake transport, CLI, and `pip check` passed |
| 3.11.14 | import, typed config, fake transport, CLI, and `pip check` passed |
| 3.12.12 | import, typed config, fake transport, CLI, and `pip check` passed |
| 3.13.10 | import, typed config, fake transport, CLI, and `pip check` passed |

The fake transport asserted that canonical `top_p=0.95` and provider-specific
`top_k=40` reached the final Friday LLM request. It made no live provider call.

On Python 3.13, `friday-framework[all]==0.1.0a1` installed from the cohort
wheels, all 17 distribution versions matched, all 16 import packages loaded,
the Friday Chat CLI reported `0.1.0a1`, and `pip check` found no broken
requirements. A second isolated install forced every Friday distribution to
build from the 17 sdists and passed the same version, import, CLI, and
`pip check` gates.

LiteLLM attempted its optional remote model-cost refresh while imports were
offline and correctly fell back to its packaged cost map. No provider inference
or generation request was made. Friday LLM's earlier bounded live LM Studio
matrix remains the behavioral transport evidence; Friday Chat's separate live
provider lane was not authorized or run.

## Production Publication Evidence

All 17 projects were uploaded to production PyPI in the dependency order from
the cohort plan. Before advancing each layer, the published wheel and sdist
SHA-256 values were compared with the frozen local files and the exact release
was installed from the production Simple API. PyPI propagation lag was observed
once for Friday LLM; publication paused until the Simple and JSON APIs converged.

Final post-publication results:

- all 17 releases and all 34 registry hashes match the manifest below;
- a fresh PyPI-only `friday-framework[all]==0.1.0a1` install succeeded;
- all 17 installed distribution versions and all 16 import packages passed;
- the root environment passed `pip check` and Friday Chat reported `0.1.0a1`;
- PyPI-only Friday Chat installs passed the typed-config/fake-transport, CLI,
  and `pip check` smoke on Python 3.10.19, 3.11.14, 3.12.12, and 3.13.10.

Primary release pages:

- [Friday Framework](https://pypi.org/project/friday-framework/0.1.0a1/)
- [Friday Chat](https://pypi.org/project/friday-chat/0.1.0a1/)
- [Friday LLM](https://pypi.org/project/friday-framework-llm/0.1.0a1/)

The temporary ignored `.env` credential file was removed after verification.
Because the PyPI token was disclosed in chat, it must be revoked in PyPI account
settings even though it is no longer stored in the checkout.

## SHA-256 Manifest

```text
648e131c952d32d16854cd720b403f22c387da6ee7785d2c30c9d737a8340f4e  friday_chat-0.1.0a1-py3-none-any.whl
95753bd78e1531d7adbedb6f7aea931d78550cc04246a76c706a90f51c38acd7  friday_chat-0.1.0a1.tar.gz
d52c09d21ff9e34665a7e7d389762835561332c110b3b2f00232f7240152a4df  friday_framework-0.1.0a1-py3-none-any.whl
2bbbfb1c040b525c5876ec4ac4b3fd55550eb71dd104709b74feec8db1c73f5c  friday_framework-0.1.0a1.tar.gz
868983b8b75849de9bc3a45b87ce71019d4817ee1f144f35895d897dcb57a4e9  friday_framework_agent-0.1.0a1-py3-none-any.whl
338148108827ce1c6ae246bcf090f9a312429209e0a1ef8b73fd36c68183662c  friday_framework_agent-0.1.0a1.tar.gz
28ae4592b97055614cf0c65794b712f3dd7870e086cd1f65a0210f802d9852d6  friday_framework_cli-0.1.0a1-py3-none-any.whl
eb1f5422951a3cab6ee89791df4ea6387358f9fa18c245fac17fc8ba836bf84e  friday_framework_cli-0.1.0a1.tar.gz
9ffe766ad5abb75eee681d1ce7dd6944dbcef521bcf9c68621aa1898a29f3847  friday_framework_core-0.1.0a1-py3-none-any.whl
75687d8f73b0217b63b632d78e309ac7cb17370b2a4e643ec7cb841d7a693b90  friday_framework_core-0.1.0a1.tar.gz
ab800ad44897e6ab6fb157fae71367156506505de960f56a64392bfaad184873  friday_framework_finance-0.1.0a1-py3-none-any.whl
3ffa23a118dcb907934f473a823d641367d7a5cbe73e31e6acad2e657c108596  friday_framework_finance-0.1.0a1.tar.gz
c536c38456055078fe97b36bd9dd38f7822786f3cdc1d9114591d8abee42ef43  friday_framework_llm-0.1.0a1-py3-none-any.whl
7d844bf6e7b247d509d1e61ad6dcb61265de19fbaba250f13fd32ba4e5ed21bd  friday_framework_llm-0.1.0a1.tar.gz
6f0261afec55c1f803873e993989b8d8403526576e28645469db9bbdafaddb27  friday_framework_mcp-0.1.0a1-py3-none-any.whl
381611f6765e4a703ff4b10a7f8d12e4b0d1211c60c3081c2cf791c7bb378f88  friday_framework_mcp-0.1.0a1.tar.gz
6257af76896745a9123e242b46a90c0cf39d838e7f5bc49bc0eb0f12bb85a5fd  friday_framework_memory-0.1.0a1-py3-none-any.whl
4800bf58933b92f2443350e067c9a268c15bca3899c68438c02f70483311be89  friday_framework_memory-0.1.0a1.tar.gz
d7d85a138f08ffd36c749f2aad49ff4b85cdd9d566fb584aa6a9515d1860b1b9  friday_framework_moltbook-0.1.0a1-py3-none-any.whl
d678633a515901a309ebe7cc3288e11574cb864d5aefd2c6a407c11b0757f04d  friday_framework_moltbook-0.1.0a1.tar.gz
9453f1d609246ee41afb859e6bd1fd0e5c0c937ff1ac09192151077299fcc687  friday_framework_optimization-0.1.0a1-py3-none-any.whl
b285ad1ceeb45c3aeea78a97a0c5f8bdb9465ec8f26716c7c9c25b94fe05423a  friday_framework_optimization-0.1.0a1.tar.gz
6727b2f9863e03bc6fa43c7d6a267d813199e22f27e7a6fa5131ad1936fa85de  friday_framework_runtime-0.1.0a1-py3-none-any.whl
e6c141b037756adfa7fccde71ca8a2a93943be0cf9c7f640de85331bea2e056e  friday_framework_runtime-0.1.0a1.tar.gz
18ace6231f95cf365f46a9ba2d8c72d3d0e0795affccfa8d98859ae9abb1cb90  friday_framework_sandbox-0.1.0a1-py3-none-any.whl
07be9c18a5e11bc3a92219683825620713c0e74a787a18933356b11b1abf8ae4  friday_framework_sandbox-0.1.0a1.tar.gz
ff25641175c22660cdf42455a0a77885cab21cac1f2d14016e19bc08c7ce40b6  friday_framework_speech-0.1.0a1-py3-none-any.whl
4e9d6df7cf7c7474668cf85dfcd1d189b0a34e465110b24278fa1f926c18a601  friday_framework_speech-0.1.0a1.tar.gz
f8fee7354ebd93fb667bbd09cc3674677a218f015289f7802b6a7531deac6533  friday_framework_telemetry-0.1.0a1-py3-none-any.whl
9c5b9ba9841266f8e7467563414627327df0f78003d70e5730fed9d229d64eba  friday_framework_telemetry-0.1.0a1.tar.gz
f62a5dddb24cc1a1b5f51064694eda330621763bb11f9fb5adeb9a0e04434e5e  friday_framework_tools-0.1.0a1-py3-none-any.whl
6276472fc05a98240d22f0d6f90648c758dd79423bee132d95240cd987022b1f  friday_framework_tools-0.1.0a1.tar.gz
3cfeff95a0e9452c84e7ff084f8d8807e3b76db47aeddd3b5f16356a3886ecbe  friday_framework_transcript-0.1.0a1-py3-none-any.whl
2f0eea08ed035cb016c5b107c30ff48b3f9e1c1bc975300eadd8635fae8589ff  friday_framework_transcript-0.1.0a1.tar.gz
```

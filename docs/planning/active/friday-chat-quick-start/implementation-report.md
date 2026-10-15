# Quick-start implementation and validation

UC1: full editable workspace install with locked all-packages/all-extras sync,
correct interpreter/executable, and a user-owned ignored client directory.
UC2: full framework[all] pinned pip and active uv-project installation, separate
bare-venv uv pip guidance, no source-tree/template dependency after install.
Shared: four complete YAML alternatives (two model-library choices, one runtime,
one display), ten chat/two embedding roles, explicit real/fake shell launcher,
private environment generation and configuration/connectivity/persistence steps.
The existing slash-command catalog is linked as further reference, not repeated.

Source basis: root/Chat package metadata and console entry points;
friday_chat.config canonical loading/credentials; runtime._resolve_maintenance_llms;
adapters build_framework_* and _build_* role factories; display resolver/prompt;
reorganization.assembly/layout/mutation paths and maintenance embedding provider;
background._should_extract; session identity; friday_llm model_library,
service/embeddings and process-client lifecycle. Endpoint/provider guidance was
checked against the primary linked Ollama/LM Studio/uv pages on2026-10-15.

[Builder checks](validation/builder-checks.json) record nine passing scenario
groups against the pre-existing installed production alpha3 environment:
- Both model libraries parse with complete runtime/display, all ten chat/two
  embedding specs, supporting-context/compaction schemas and non-started real
  assembly. Extractor/compactor and persistent graph construct with no adapter gaps.
- Both live preflight recipes execute with synthetic LiteLLM transport; routing
  model/base, text result, vector length and process-client shutdown work.
- Missing credentials, unknown profiles and missing required maintenance roles
  are rejected as documented.
- Both launchers execute an actual installed fake CLI session with piped hello/q.
  Environment setup refuses overwrite and sets0600; stub probes verify cwd and
  executable paths containing spaces, explicit/default modes overriding inherited
  values, invalid arguments and missing-file refusal.
- Three embedded Python snippets compile; four YAML examples parse; sixteen
  Bash fences pass syntax; both changed guide bodies render without warnings.
  Local targets/anchors pass. External links are linked references, not an
  exhaustive reachability certification.

The first checker assumed a Python fence instead of Bash-embedded heredocs, then
omitted the active interpreter's bin from the isolated PATH. Both harness issues
were corrected before the final passing replay; neither was a guide defect.
The live recipe was source-checked and transport-mocked before candidate freeze.

No installation/sync/model download, real provider/model call, hardware/audio,
Docker, Windows/PowerShell execution, production store migration or full product
suite was performed. Mock preflight and fake CLI do not establish real retrieval
quality or endpoint readiness. User-run live commands are explicitly labeled.
No product source, tests, dependencies, versions, locks or existing launchers
changed. No push, PR, merge or publication is authorized by this work.

Next: frozen candidate and fresh-context read-only reviewer walking both UC1 and
UC2 as a new user, including copy/paste order, exact roles and file/path behavior.

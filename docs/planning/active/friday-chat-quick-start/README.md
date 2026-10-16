# Friday Chat quick start

Status: started; implementation_authority: granted by explicit maintainer request.
execution_phase: validation; validation_state: pending.

[Authority](authority.json), [construction directive](directives/CD-QS-001.md)
and the maintainer-authorized [hosted API amendment](directives/ADD-QS-001-hosted-openai.md)
define the guide's UC1/UC2 installation, configuration and independent-review scope.

[Current independent review](validation/hosted-review/report.md): VERIFIED candidate
89ad03a70d1c2ff9d5e8a2048f3491bb7c74903d, with no findings. Hosted OpenAI,
local Ollama/LM Studio and mixed endpoints use the shared runtime/CLI/launcher.
[Hosted amendment and checks](hosted-amendment-report.md) record the additions,
model/credential/embedding details, actual verification and no-live-call limits.

Historical reviews remain unchanged and apply to their pinned candidates:

- [Initial UC1/UC2 review](validation/independent-review/report.md): VERIFIED6a83ad50.
  [Implementation report](implementation-report.md) records the original examples.
- [Self-contained PyPI introduction correction](validation/intro-review/report.md):
  VERIFIED847b5c34. Repository launcher reference is confined to UC1.

Next gate: maintainer review, completion/acceptance and separately authorized
delivery. Local documentation only; no acceptance, push or publication inferred.

Delivery amendment: [ADD-QS-002](directives/ADD-QS-002-delivery.md) records the
maintainer-authorized metadata correction, rename and GitHub delivery.
Current execution_phase: validation; validation_state: pending.
Next gate: independent delivery review, then authorized push/PR/merge and remote
branch deletion; alpha4 publication follows in a separate release unit.

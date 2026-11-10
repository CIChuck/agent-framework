"""Shared response evidence is bounded and independent of frontend packages."""

import json
import os
import subprocess
import sys
from dataclasses import FrozenInstanceError, asdict

import pytest
from friday_memory.response_diagnostics import response_diagnostic
from pydantic import BaseModel, ConfigDict, ValidationError


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    confidence: float
    status: str = "fixture"
    memory_id: str = "fixture"
    collection: str = "fixture"


class Response(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    decisions: tuple[Decision, ...]


@pytest.mark.parametrize("key", ["confidence", "status", "memory_id", "collection"])
def test_diagnostics_redact_root_keys_known_only_in_nested_schema(key):
    with pytest.raises(ValidationError) as caught:
        Response.model_validate_json(json.dumps({"decisions": [], key: "private"}))
    diag = response_diagnostic(
        role="judge",
        configured_model="fixture",
        response_model=Response,
        finish_reason="stop",
        error=caught.value,
    )
    assert [(issue.path, issue.code) for issue in diag.issues] == [
        (("<field>",), "extra_forbidden")
    ]


def test_diagnostics_redact_nested_key_known_only_at_root():
    with pytest.raises(ValidationError) as caught:
        Response.model_validate_json(
            '{"decisions":[{"confidence":0.5,"decisions":"private"}]}'
        )
    diag = response_diagnostic(
        role="judge",
        configured_model="fixture",
        response_model=Response,
        finish_reason="stop",
        error=caught.value,
    )
    assert [(issue.path, issue.code) for issue in diag.issues] == [
        (("decisions", 0, "<field>"), "extra_forbidden")
    ]


def test_diagnostics_redact_dictionary_keys_while_preserving_value_field_paths():
    class MappedResponse(BaseModel):
        decisions: dict[str, Decision]

    with pytest.raises(ValidationError) as caught:
        MappedResponse.model_validate_json(
            '{"decisions":{"confidence":{"confidence":"private"}}}'
        )
    diag = response_diagnostic(
        role="judge",
        configured_model="fixture",
        response_model=MappedResponse,
        finish_reason="stop",
        error=caught.value,
    )
    assert [(issue.path, issue.code) for issue in diag.issues] == [
        (("decisions", "<field>", "confidence"), "float_type")
    ]


def test_diagnostics_redact_input_keys_values_messages_and_context():
    secret = "private-provider-response-and-credential"
    payload = {"decisions": [{"confidence": secret}], secret: secret}
    with pytest.raises(ValidationError) as caught:
        Response.model_validate_json(json.dumps(payload))
    diag = response_diagnostic(
        role="judge",
        configured_model="openrouter/fixture-model",
        response_model=Response,
        finish_reason="stop",
        error=caught.value,
    )
    assert secret not in diag.summary()
    assert secret not in json.dumps(asdict(diag))
    assert "decisions.0.confidence:float_type" in diag.summary()
    assert "<field>:extra_forbidden" in diag.summary()
    assert "role=judge" in diag.summary()
    assert "model=openrouter/fixture-model" in diag.summary()
    with pytest.raises(FrozenInstanceError):
        diag.role = "changed"


def test_diagnostic_limits_and_unknown_finish_reasons():
    payload = {f"private-key-{i}": "private-value" for i in range(30)}
    with pytest.raises(ValidationError) as caught:
        Response.model_validate_json(json.dumps(payload))
    diag = response_diagnostic(
        role="bad\nrole",
        configured_model="x" * 300,
        response_model=Response,
        finish_reason="private-provider-value",
        error=caught.value,
    )
    assert len(diag.issues) == 5
    assert diag.role == diag.configured_model == "unavailable"
    assert diag.finish_reason == "other"
    assert "private-" not in diag.summary()
    absent = response_diagnostic(
        role="classifier",
        configured_model="fixture",
        response_model=Response,
        finish_reason=None,
    )
    assert absent.finish_reason == "unavailable"
    assert absent.issues == ()


def test_shared_response_boundary_runs_without_frontend_imports(tmp_path):
    code = """
import sys
class NoFrontends:
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in {'friday_chat', 'friday_commands', 'friday_tui'}:
            raise RuntimeError('frontend import: ' + fullname)
sys.meta_path.insert(0, NoFrontends())
from friday_memory.json_response import parse_json_object_from_text
from friday_memory.llm_completion import MemoryCompletion
from friday_memory.response_diagnostics import response_diagnostic
from pydantic import BaseModel
class Response(BaseModel):
    ready: bool
assert parse_json_object_from_text('{"ready":true}', recover_nested_objects=False) == {'ready': True}
assert MemoryCompletion(None).finish_reason is None
assert response_diagnostic(role='judge', configured_model='fixture', response_model=Response, finish_reason='length').finish_reason == 'length'
assert not any(n.startswith(('friday_chat', 'friday_commands', 'friday_tui')) for n in sys.modules)
print('shared response boundary passed')
"""
    env = dict(
        os.environ, PYTHONDONTWRITEBYTECODE="1", LITELLM_LOCAL_MODEL_COST_MAP="True"
    )
    run = subprocess.run(
        [sys.executable, "-I", "-B", "-c", code],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "shared response boundary passed" in run.stdout

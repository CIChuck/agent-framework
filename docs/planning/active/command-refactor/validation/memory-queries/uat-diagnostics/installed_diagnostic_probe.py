"""Offline installed response-boundary proof; creates no runtime or memory store."""

from __future__ import annotations

import asyncio
import json
import sys
import traceback
from pathlib import Path
from unittest.mock import AsyncMock


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def origins() -> dict[str, str]:
    files = {
        name: str(Path(module.__file__).resolve())
        for name, module in list(sys.modules.items())
        if name.startswith("friday_") and getattr(module, "__file__", None)
    }
    require(
        all(Path(path).is_relative_to(Path(sys.prefix)) for path in files.values()),
        "Friday module escaped installed prefix",
    )
    return files


def headless() -> dict:
    class NoFrontends:
        def find_spec(self, fullname, *_args):
            if fullname.split(".")[0] in {
                "friday_chat",
                "friday_commands",
                "friday_tui",
            }:
                raise RuntimeError("Frontend dependency: " + fullname)

    sys.meta_path.insert(0, NoFrontends())
    from friday_memory.json_response import parse_json_object_from_text
    from friday_memory.llm_completion import MemoryCompletion
    from friday_memory.response_diagnostics import response_diagnostic
    from pydantic import BaseModel

    class Response(BaseModel):
        ready: bool

    require(
        parse_json_object_from_text('{"ready":true}', recover_nested_objects=False)
        == {"ready": True},
        "Shared parser failed",
    )
    require(MemoryCompletion(None).finish_reason is None, "Metadata default changed")
    diagnostic = response_diagnostic(
        role="judge",
        configured_model="fixture",
        response_model=Response,
        finish_reason="length",
    )
    require(diagnostic.finish_reason == "length", "Shared diagnostic failed")
    require("friday_chat" not in sys.modules, "Shared boundary imported Chat")
    return {"mode": "headless", "passed": True, "origins": origins()}


async def maintenance() -> dict:
    from friday_chat.reorganization import mutation as m
    from friday_llm import (
        CompletionAssurance,
        LiteLLMService,
        TypedChatCompletionResponse,
    )
    from friday_memory.llm_completion import complete_memory_request

    valid = json.dumps(
        {
            "decisions": [
                {
                    "collection": "fixture",
                    "memory_id": f"record-{i}",
                    "status": "verified",
                    "confidence": 0.9,
                }
                for i in range(234)
            ]
        }
    )
    rows = []
    for role in (
        m.MaintenanceLlmRole.CLASSIFIER,
        m.MaintenanceLlmRole.RESEARCHER,
        m.MaintenanceLlmRole.JUDGE,
    ):
        for label, text, reason, expected in [
            ("valid", valid, "stop", None),
            (
                "length",
                '{"decisions":[]}',
                "length",
                m.MaintenanceResponseIncompleteError,
            ),
            (
                "truncated",
                valid[: len(valid) // 2],
                None,
                m.MaintenanceResponseParseError,
            ),
            (
                "invalid",
                '{"decisions":[{"confidence":"private-value"}]}',
                "stop",
                m.MaintenanceResponseValidationError,
            ),
        ]:
            client = AsyncMock(spec=LiteLLMService)
            client.chat_completion_request.return_value = TypedChatCompletionResponse(
                content=text,
                model="fixture-reported-model",
                finish_reason=reason,
                reasoning_content="private-reasoning",
                assurance=CompletionAssurance(),
            )
            provider = m.LiteLlmMaintenanceProvider(
                role=role,
                service=client,
                config=m.MaintenanceProviderConfig(model="fixture-configured-model"),
            )
            try:
                result = await provider.complete_model(
                    m.VerificationResponse,
                    system_prompt="Offline fixture",
                    user_payload="{}",
                )
            except m.MaintenanceResponseError as error:
                require(type(error) is expected, "Wrong error classification")
                require(error.diagnostic is not None, "Missing diagnostic")
                require(error.diagnostic.role == role.value, "Wrong role")
                require(
                    error.diagnostic.configured_model == "fixture-configured-model",
                    "Wrong model",
                )
                detail = "".join(traceback.format_exception(error))
                require(
                    "private-value" not in detail and "private-reasoning" not in detail,
                    "Content leak",
                )
                rows.append(
                    {
                        "role": role.value,
                        "case": label,
                        "error": type(error).__name__,
                        "diagnostic": error.diagnostic.summary(),
                    }
                )
            else:
                require(
                    expected is None and len(result.decisions) == 234,
                    "Invalid control result",
                )
                rows.append({"role": role.value, "case": label, "decisions": 234})
            require(
                client.chat_completion_request.await_count == 1,
                "Repeated provider execution",
            )
    completion = await complete_memory_request(
        client, messages=[{"role": "user", "content": "Offline fixture"}]
    )
    require(completion.model == "fixture-reported-model", "Completion model lost")
    require(completion.finish_reason == "stop", "Completion finish reason lost")
    return {"mode": "maintenance", "passed": True, "cases": rows, "origins": origins()}


if __name__ == "__main__":
    mode, output = sys.argv[1:]
    result = headless() if mode == "headless" else asyncio.run(maintenance())
    Path(output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"mode": mode, "passed": True, "optimize": sys.flags.optimize}))

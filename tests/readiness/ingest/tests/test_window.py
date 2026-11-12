from __future__ import annotations

import unittest

from ingest.manifests import Refusal, object_value
from ingest.tests.test_ledger import ledger
from ingest.window import FakeTransportGate, Window


def receipt() -> dict[str, object]:
    return {
        "schema": 1,
        "run_id": "unit",
        "endpoint": "http://127.0.0.1:1234",
        "model": "loaded-embedding-id",
        "status_profile": "LMS_NATIVE_V0",
        "confirmed": 1,
        "expires": 20,
        "prefix": "a" * 64,
        "bindings": {"batch": "b" * 64},
        "attestations": {
            "operator": "fixture-operator",
            "production_stopped": True,
            "server_restarted": True,
            "logs_separate": True,
            "already_loaded": True,
            "no_jit": True,
            "no_idle_unload": True,
            "no_eviction": True,
            "server_version": "fixture-only",
            "log_evidence": "fixture-only",
        },
    }


def window(value: object | None = None) -> Window:
    return Window.parse(
        receipt() if value is None else value,
        2,
        "unit",
        {"a" * 64},
        {"batch": "b" * 64},
    )


class Windows(unittest.TestCase):
    def test_valid_loaded_identity_and_no_fallback(self) -> None:
        selected = window()
        selected.loaded(
            {"data": [{"id": selected.model, "state": "loaded", "type": "embeddings"}]}
        )
        with self.assertRaises(Refusal):
            selected.loaded(
                {
                    "data": [
                        {
                            "id": selected.model,
                            "state": "not-loaded",
                            "type": "embeddings",
                        }
                    ]
                }
            )
        with self.assertRaises(Refusal):
            window(receipt() | {"status_profile": "OPENAI_DOWNLOADED_LIST"})

    def test_invalid_window_identity_expiry_and_policy(self) -> None:
        for update in (
            {"expires": 2},
            {"run_id": "other"},
            {"prefix": "c" * 64},
            {"endpoint": "https://external.example"},
            {"bindings": {"batch": "d" * 64}},
        ):
            with self.subTest(update=update), self.assertRaises(Refusal):
                window(receipt() | update)
        data = receipt()
        attestations = object_value(data["attestations"])
        attestations["no_jit"] = False
        with self.assertRaises(Refusal):
            window(data | {"attestations": attestations})

    def test_transport_attempts_status_retries_and_stop_share_budget(self) -> None:
        log = ledger()
        seen: list[str] = []

        def fake(method: str, path: str, payload: dict[str, object]) -> object:
            seen.append(path)
            return {"ok": True}

        gate = FakeTransportGate(
            window(),
            lambda: 2,
            log.stopped,
            lambda resource, amount, ceiling: log.reserve(
                resource, amount, min(ceiling, 3)
            ),
            fake,
        )
        for _ in range(3):
            gate.send("GET", gate.window.status_path, {})
        with self.assertRaises(Refusal):
            gate.send("GET", gate.window.status_path, {})
        with self.assertRaises(Refusal):
            gate.send("POST", "/api/v1/models/load", {})
        self.assertEqual(len(seen), 3)

    def test_revocation_and_expiry_prevent_further_transport_attempts(self) -> None:
        log = ledger()
        now = [2]
        seen: list[str] = []

        def fake(method: str, path: str, payload: dict[str, object]) -> object:
            seen.append(path)
            return {}

        gate = FakeTransportGate(
            window(),
            lambda: now[0],
            log.stopped,
            log.reserve,
            fake,
        )
        gate.send("GET", gate.window.status_path, {})
        now[0] = 21
        with self.assertRaises(Refusal):
            gate.send("GET", gate.window.status_path, {})
        now[0] = 2
        (log.state / "stop.json").write_text('{"schema":1}')
        with self.assertRaises(Refusal):
            gate.send("GET", gate.window.status_path, {})
        self.assertEqual(len(seen), 1)

    def test_prepared_input_and_vector_budgets_precede_transport(self) -> None:
        log = ledger()
        sent: list[object] = []

        def fake(method: str, path: str, payload: dict[str, object]) -> object:
            sent.append(payload)
            return {}

        gate = FakeTransportGate(
            window(),
            lambda: 2,
            log.stopped,
            log.reserve,
            fake,
            counter=len,
            max_input_tokens=4,
        )
        gate.send(
            "POST", "/v1/embeddings", {"model": gate.window.model, "input": ["1234"]}
        )
        payloads: tuple[dict[str, object], ...] = (
            {"model": gate.window.model, "input": ["12345"]},
            {"model": gate.window.model, "input": ["x"] * 257},
            {"model": "different", "input": ["x"]},
            {"model": gate.window.model, "input": ["x"], "ttl": 10},
        )
        for payload in payloads:
            with (
                self.subTest(payload_keys=list(payload)),
                self.assertRaises(ValueError),
            ):
                gate.send("POST", "/v1/embeddings", payload)
        self.assertEqual(len(sent), 1)
        self.assertEqual(gate.attempts, 1)
        unqualified = FakeTransportGate(
            window(), lambda: 2, log.stopped, log.reserve, fake
        )
        with self.assertRaises(ValueError):
            unqualified.send(
                "POST", "/v1/embeddings", {"model": gate.window.model, "input": ["x"]}
            )

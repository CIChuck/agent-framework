"""Offline model-window validation and fake-transport accounting. No HTTP client."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ingest.manifests import (
    SHA256,
    fields,
    integer,
    object_value,
    require,
    sequence,
    text,
)


@dataclass(frozen=True)
class Window:
    run_id: str
    endpoint: str
    model: str
    status_profile: str
    expires: int
    prefix: str
    bindings: dict[str, str]

    @classmethod
    def parse(
        cls,
        value: object,
        now: int,
        run_id: str,
        prefixes: set[str],
        bindings: dict[str, str],
    ) -> Window:
        data = fields(
            value,
            {
                "schema",
                "run_id",
                "endpoint",
                "model",
                "status_profile",
                "expires",
                "confirmed",
                "prefix",
                "bindings",
                "attestations",
            },
        )
        require(type(data["schema"]) is int and data["schema"] == 1, "Window schema")
        require(
            data["run_id"] == run_id and data["prefix"] in prefixes,
            "Window run/promoted prefix mismatch",
        )
        require(
            integer(data["confirmed"]) <= now < integer(data["expires"]),
            "Window not confirmed or expired",
        )
        attested = fields(
            data["attestations"],
            {
                "operator",
                "production_stopped",
                "server_restarted",
                "logs_separate",
                "already_loaded",
                "no_jit",
                "no_idle_unload",
                "no_eviction",
                "server_version",
                "log_evidence",
            },
        )
        for key in {
            "production_stopped",
            "server_restarted",
            "logs_separate",
            "already_loaded",
            "no_jit",
            "no_idle_unload",
            "no_eviction",
        }:
            require(attested[key] is True, "Unsafe/unknown operator-attested policy")
        for key in ("operator", "server_version", "log_evidence"):
            require(bool(text(attested[key]).strip()), "Missing operator fact")
        actual = object_value(data["bindings"])
        require(
            actual == bindings
            and bool(bindings)
            and all(SHA256.fullmatch(item) for item in bindings.values()),
            "Window manifest bindings mismatch",
        )
        endpoint = text(data["endpoint"])
        require(
            endpoint.startswith("http://127.0.0.1:")
            and endpoint.rsplit(":", 1)[1].isdigit(),
            "Exact loopback endpoint required",
        )
        profile = text(data["status_profile"])
        require(
            profile in {"LMS_NATIVE_V1", "LMS_NATIVE_V0"},
            "Unknown native status profile",
        )
        model = text(data["model"])
        require(bool(model) and "/" not in model[:1], "Missing loaded request model")
        return cls(
            run_id,
            endpoint,
            model,
            profile,
            integer(data["expires"]),
            text(data["prefix"]),
            dict(bindings),
        )

    @property
    def status_path(self) -> str:
        return (
            "/api/v1/models"
            if self.status_profile == "LMS_NATIVE_V1"
            else "/api/v0/models"
        )

    def loaded(self, payload: object) -> None:
        data = object_value(payload)
        if self.status_profile == "LMS_NATIVE_V0":
            rows = sequence(data.get("data"))
            require(
                any(
                    object_value(row).get("id") == self.model
                    and object_value(row).get("state") == "loaded"
                    and object_value(row).get("type") == "embeddings"
                    for row in rows
                ),
                "Exact embedding model is not loaded",
            )
        else:
            rows = sequence(data.get("models"))
            require(
                any(
                    object_value(row).get("type") == "embedding"
                    and any(
                        object_value(instance).get("id") == self.model
                        for instance in sequence(
                            object_value(row).get("loaded_instances")
                        )
                    )
                    for row in rows
                ),
                "Exact embedding instance is not loaded",
            )


class FakeTransportGate:
    """C0 protocol seam: caller supplies an in-process fake, never a socket client."""

    def __init__(
        self,
        window: Window,
        now: Callable[[], int],
        stopped: Callable[[], bool],
        reserve: Callable[[str, int, int], None],
        fake: Callable[[str, str, dict[str, object]], object],
        counter: Callable[[str], int] | None = None,
        max_input_tokens: int | None = None,
    ) -> None:
        self.window, self.now, self.stopped, self.reserve, self.fake = (
            window,
            now,
            stopped,
            reserve,
            fake,
        )
        self.attempts = 0
        self.counter = counter
        self.max_input_tokens = max_input_tokens

    def send(self, method: str, path: str, payload: dict[str, object]) -> object:
        require(
            not self.stopped() and self.now() < self.window.expires,
            "Window stopped or expired",
        )
        require(
            (method, path)
            in {("GET", self.window.status_path), ("POST", "/v1/embeddings")},
            "Unauthorized model route",
        )
        require(
            not payload
            if method == "GET"
            else payload.get("model") == self.window.model,
            "Wrong loaded-model request identity",
        )
        if method == "POST":
            counter, limit = self.counter, self.max_input_tokens
            if counter is None or limit is None:
                raise ValueError("Qualified counter/input limit missing")
            require(
                set(payload) == {"model", "input"}, "Unknown embedding request fields"
            )
            inputs = sequence(payload["input"])
            require(0 < len(inputs) <= 256, "Embedding vector-count boundary")
            counts = [integer(counter(text(item)), 1) for item in inputs]
            require(all(count <= limit for count in counts), "Prepared-input overflow")
            self.reserve("vectors", len(inputs), 256)
            self.reserve("tokens", sum(counts), 131072)
        self.reserve("requests", 1, 64)
        # Preparation and reservation callbacks may observe or publish stop/expiry.
        # Prior reservations remain charged even when this final admission refuses.
        require(
            not self.stopped() and self.now() < self.window.expires,
            "Window stopped or expired before transport",
        )
        self.attempts += 1
        # Entering the fake is the bounded accepted-in-flight handoff. A control
        # change inside that callback cannot cancel work it has already accepted.
        return self.fake(method, path, payload)

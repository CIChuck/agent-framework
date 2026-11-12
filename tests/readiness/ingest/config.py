"""Typed C0 controls. Real upstream effects require a separate activation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ingest.manifests import SHA256, fields, require, text
from ingest.paths import Layout


@dataclass(frozen=True)
class Config:
    layout: Layout
    harness_sha256: str
    envelope_sha256: str
    interpreter_sha256: str
    activation: str

    @classmethod
    def parse(cls, value: object) -> Config:
        data = fields(
            value,
            {
                "schema",
                "project",
                "run_id",
                "harness_sha256",
                "envelope_sha256",
                "interpreter_sha256",
                "activation",
            },
        )
        require(
            type(data["schema"]) is int and data["schema"] == 1,
            "Unknown configuration schema",
        )
        hashes = tuple(
            text(data[name])
            for name in ("harness_sha256", "envelope_sha256", "interpreter_sha256")
        )
        require(
            all(SHA256.fullmatch(item) for item in hashes),
            "Missing approved identity digest",
        )
        activation = text(data["activation"])
        require(activation == "C0", "Upstream stage activation is not granted by C0")
        return cls(
            Layout(Path(text(data["project"])), text(data["run_id"])),
            hashes[0],
            hashes[1],
            hashes[2],
            activation,
        )

    def record(self) -> dict[str, object]:
        return {
            "schema": 1,
            "project": str(self.layout.project),
            "run_id": self.layout.run_id,
            "harness_sha256": self.harness_sha256,
            "envelope_sha256": self.envelope_sha256,
            "interpreter_sha256": self.interpreter_sha256,
            "activation": self.activation,
        }

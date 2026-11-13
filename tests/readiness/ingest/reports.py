"""Report only observed evidence; report rendering is never qualification."""

from __future__ import annotations

from ingest.ledger import ZERO, Ledger
from ingest.manifests import SHA256, fields, integer, object_value, require, text


def report(ledger: Ledger) -> dict[str, object]:
    rows = ledger.records()
    prepared: list[dict[str, object]] = []
    for row in rows:
        payload = object_value(row["payload"])
        if row["event"] == "finish" and payload.get("operation") == "prepare_fixtures":
            payload = fields(
                payload,
                {
                    "operation",
                    "manifest_sha256",
                    "fixture_count",
                    "converter_qualified",
                },
            )
            sha = text(payload["manifest_sha256"])
            require(bool(SHA256.fullmatch(sha)), "Invalid prepared-input digest")
            count = integer(payload["fixture_count"])
            require(
                count == 30 and payload["converter_qualified"] is False,
                "Invalid fixture preparation claim",
            )
            prepared.append(
                {
                    "manifest_sha256": sha,
                    "fixture_count": count,
                    "evidence_class": "ledger_witness_only",
                    "current_bytes_revalidated": False,
                    "converter_qualified": False,
                }
            )
    return {
        "schema": 1,
        "status": "INCOMPLETE",
        "claim_scope": "Offline controls/input preparation only; upstream/runtime qualification not performed",
        "records": len(rows),
        "ledger_tip": text(rows[-1]["sha256"]) if rows else ZERO,
        "stopped": ledger.stopped(),
        "executed": (["C0 control-run initialization"] if rows else [])
        + (["synthetic input preparation"] if prepared else []),
        "prepared_inputs": prepared,
        "unqualified": [
            "A0 dependency resolution",
            "A1 installed profiles",
            "A2 document extraction/chunking",
            "A3 real model",
            "A4 full readiness",
        ],
        "full_readiness": False,
        "observed": {"ledger_consistency": True},
        "operator_attested": {},
        "containment": "Python-visible prevention where armed; bounded metadata detection, no OS sandbox",
    }

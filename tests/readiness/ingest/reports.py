"""Report only observed evidence; report rendering is never qualification."""

from __future__ import annotations

from ingest.ledger import Ledger


def report(ledger: Ledger) -> dict[str, object]:
    rows = ledger.records()
    return {
        "schema": 1,
        "status": "INCOMPLETE",
        "claim_scope": "C0 control-plane only; upstream/runtime qualification not performed",
        "records": len(rows),
        "ledger_tip": ledger.tip(),
        "stopped": ledger.stopped(),
        "executed": ["C0 controls"],
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

"""Content-first file classifier.

The classifier intentionally treats file names as weak evidence. Headers and
sample values are stronger signals, which makes renamed exports easier to
handle.
"""

from __future__ import annotations

import json
from pathlib import Path

from .io import read_table_preview
from .models import ClassifiedFile


DEFAULT_SIGNATURES: dict[str, dict[str, list[str]]] = {
    "inventory": {
        "headers": ["item_code", "item_name", "available_qty", "warehouse", "stock_qty", "storage_location"],
        "values": ["warehouse", "stock", "available", "inventory"],
    },
    "demand": {
        "headers": ["order_no", "order_id", "account", "customer", "item_code", "demand_qty", "required_date", "due_date"],
        "values": ["order", "demand", "account", "customer"],
    },
    "fulfillment": {
        "headers": ["fulfillment_id", "shipment_no", "invoice_no", "account", "ship_date", "fulfilled_qty"],
        "values": ["shipment", "fulfillment", "delivered", "completed"],
    },
    "replenishment": {
        "headers": ["partner", "supplier", "item_code", "material_code", "planned_qty", "promise_date"],
        "values": ["replenishment", "purchase", "supplier", "vendor"],
    },
    "work_output": {
        "headers": ["work_center", "line", "item_code", "completed_qty", "output_qty", "work_date"],
        "values": ["production", "assembly", "work center", "completed"],
    },
}


class FileClassifier:
    """Classify spreadsheets into configured operations source types."""

    def __init__(self, signatures: dict[str, dict[str, list[str]]] | None = None) -> None:
        self.signatures = signatures or DEFAULT_SIGNATURES

    @classmethod
    def from_json(cls, path: Path) -> "FileClassifier":
        with path.open("r", encoding="utf-8") as handle:
            return cls(json.load(handle))

    def classify(self, path: Path) -> ClassifiedFile:
        rows = read_table_preview(path)
        headers = list(rows[0].keys()) if rows else []
        header_text = " ".join(headers).lower()
        value_text = " ".join(
            str(value).lower()
            for row in rows[:15]
            for value in row.values()
            if value is not None
        )
        file_text = path.name.lower()

        best_type = "unknown"
        best_score = 0
        best_reasons: list[str] = []

        for source_type, signature in self.signatures.items():
            score = 0
            reasons: list[str] = []
            for token in signature.get("headers", []):
                if token.lower() in header_text:
                    score += 4
                    reasons.append(f"header:{token}")
            for token in signature.get("values", []):
                if token.lower() in value_text:
                    score += 2
                    reasons.append(f"value:{token}")
            for token in signature.get("filename", []):
                if token.lower() in file_text:
                    score += 1
                    reasons.append(f"filename:{token}")
            if score > best_score:
                best_type = source_type
                best_score = score
                best_reasons = reasons

        confidence = min(best_score / 12, 1.0)
        if best_type == "unknown":
            best_reasons = ["no configured signature matched"]

        return ClassifiedFile(
            path=path,
            source_type=best_type,
            confidence=round(confidence, 2),
            reasons=best_reasons,
            headers=headers,
        )

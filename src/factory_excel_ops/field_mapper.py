"""Map source headers into standard field names."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


DEFAULT_MAPPING: dict[str, list[str]] = {
    "item_code": ["item_code", "material_code", "product_code", "sku", "part_no"],
    "item_name": ["item_name", "material_name", "product_name", "description"],
    "available_qty": ["available_qty", "stock_qty", "inventory_qty", "qty_available"],
    "demand_qty": ["demand_qty", "order_qty", "required_qty", "qty"],
    "fulfilled_qty": ["fulfilled_qty", "shipment_qty", "ship_qty", "delivery_qty", "qty_fulfilled"],
    "replenishment_qty": ["replenishment_qty", "purchase_qty", "planned_qty", "po_qty", "qty_planned"],
    "output_qty": ["output_qty", "production_qty", "completed_qty", "assembly_qty"],
    "account": ["account", "customer", "customer_name", "sold_to", "client"],
    "partner": ["partner", "supplier", "supplier_name", "vendor"],
    "source_date": ["date", "ship_date", "required_date", "promise_date", "work_date", "due_date"],
}


class FieldMapper:
    """Normalize records with configurable aliases."""

    def __init__(self, mapping: dict[str, list[str]] | None = None) -> None:
        self.mapping = mapping or DEFAULT_MAPPING

    @classmethod
    def from_json(cls, path: Path) -> "FieldMapper":
        with path.open("r", encoding="utf-8") as handle:
            return cls(json.load(handle))

    def normalize(self, row: dict[str, Any]) -> dict[str, Any]:
        lower_lookup = {_normalize_header(str(key)): value for key, value in row.items()}
        normalized: dict[str, Any] = {}
        for standard, aliases in self.mapping.items():
            for alias in aliases:
                normalized_alias = _normalize_header(alias)
                if normalized_alias in lower_lookup:
                    normalized[standard] = lower_lookup[normalized_alias]
                    break
        return normalized


def _normalize_header(raw: str) -> str:
    value = str(raw or "").strip().casefold()
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"[\s_\-/\\.]+", "", value)
    return value

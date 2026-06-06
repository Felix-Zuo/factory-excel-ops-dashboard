"""Ingest files, normalize rows, and compute public-demo summaries."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from .classifier import FileClassifier
from .field_mapper import FieldMapper
from .io import read_table
from .models import DashboardSummary, SourceRef, StandardRecord


def ingest_paths(paths: Iterable[Path], classifier: FileClassifier, mapper: FieldMapper) -> tuple[list[StandardRecord], list[str]]:
    """Classify and normalize the given spreadsheet paths."""

    records: list[StandardRecord] = []
    warnings: list[str] = []
    for path in paths:
        classification = classifier.classify(path)
        if classification.source_type == "unknown":
            warnings.append(f"{path.name}: unknown file type")
            continue
        for row_index, row in enumerate(read_table(path), start=2):
            fields = mapper.normalize(row)
            if not fields:
                continue
            records.append(
                StandardRecord(
                    source_type=classification.source_type,
                    fields=fields,
                    source=SourceRef(source_file=path.name, row_number=int(row.get("_row_number", row_index) or row_index)),
                )
            )
    return records, warnings


def summarize(records: list[StandardRecord], file_count: int, warnings: list[str] | None = None) -> DashboardSummary:
    """Compute a compact operational summary for the dashboard."""

    by_source = Counter(record.source_type for record in records)
    inventory_by_item: dict[str, float] = defaultdict(float)
    order_demand = 0.0
    shipment_qty = 0.0
    purchase_qty = 0.0
    production_qty = 0.0

    for record in records:
        fields = record.fields
        item_code = str(fields.get("item_code", "")).strip()
        if record.source_type == "inventory" and item_code:
            inventory_by_item[item_code] += _to_float(fields.get("available_qty"))
        elif record.source_type == "sales_order":
            order_demand += _to_float(fields.get("demand_qty"))
        elif record.source_type == "shipment":
            shipment_qty += _to_float(fields.get("shipment_qty"))
        elif record.source_type == "purchase_plan":
            purchase_qty += _to_float(fields.get("purchase_qty"))
        elif record.source_type == "production":
            production_qty += _to_float(fields.get("production_qty"))

    return DashboardSummary(
        file_count=file_count,
        record_count=len(records),
        inventory_items=len(inventory_by_item),
        out_of_stock_items=sum(1 for qty in inventory_by_item.values() if qty <= 0),
        order_demand_qty=order_demand,
        shipment_qty=shipment_qty,
        purchase_qty=purchase_qty,
        production_qty=production_qty,
        by_source_type=dict(sorted(by_source.items())),
        warnings=warnings or [],
    )


def _to_float(value: object) -> float:
    if value in (None, ""):
        return 0.0
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return 0.0

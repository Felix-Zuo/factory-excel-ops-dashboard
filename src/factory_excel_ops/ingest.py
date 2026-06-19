"""Ingest files, normalize rows, and compute public-demo summaries."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable

from .classifier import FileClassifier
from .field_mapper import FieldMapper
from .io import read_table
from .metrics import DEFAULT_METRIC_SPECS, compute_metrics, metric_value
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


def summarize(
    records: list[StandardRecord],
    file_count: int,
    warnings: list[str] | None = None,
    metric_specs: list[dict[str, object]] | None = None,
) -> DashboardSummary:
    """Compute a compact operational summary for the dashboard."""

    by_source = Counter(record.source_type for record in records)
    metrics = compute_metrics(records, metric_specs or DEFAULT_METRIC_SPECS)

    return DashboardSummary(
        file_count=file_count,
        record_count=len(records),
        inventory_items=int(metric_value(metrics, "inventory_items")),
        out_of_stock_items=int(metric_value(metrics, "out_of_stock_items")),
        order_demand_qty=metric_value(metrics, "order_demand_qty"),
        shipment_qty=metric_value(metrics, "shipment_qty"),
        purchase_qty=metric_value(metrics, "purchase_qty"),
        production_qty=metric_value(metrics, "production_qty"),
        by_source_type=dict(sorted(by_source.items())),
        metrics=metrics,
        warnings=warnings or [],
    )

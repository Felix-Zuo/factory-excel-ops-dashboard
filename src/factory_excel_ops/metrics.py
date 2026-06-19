"""Configurable metric calculations for spreadsheet operations profiles."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .models import StandardRecord, SummaryMetric


DEFAULT_METRIC_SPECS: list[dict[str, Any]] = [
    {
        "key": "inventory_items",
        "label": "Tracked Items",
        "type": "distinct_count",
        "source_type": "inventory",
        "field": "item_code",
        "description": "Distinct items present in the inventory or asset snapshot.",
    },
    {
        "key": "out_of_stock_items",
        "label": "Zero / Negative Stock",
        "type": "count_group_lte",
        "source_type": "inventory",
        "group_by": "item_code",
        "value_field": "available_qty",
        "threshold": 0,
        "description": "Item groups whose summed available quantity is zero or below.",
    },
    {
        "key": "order_demand_qty",
        "label": "Demand Qty",
        "type": "sum",
        "source_type": ["demand", "sales_order"],
        "field": "demand_qty",
    },
    {
        "key": "shipment_qty",
        "label": "Fulfilled Qty",
        "type": "sum",
        "source_type": ["fulfillment", "shipment"],
        "field": "fulfilled_qty",
    },
    {
        "key": "purchase_qty",
        "label": "Replenishment Qty",
        "type": "sum",
        "source_type": ["replenishment", "purchase_plan"],
        "field": "replenishment_qty",
    },
    {
        "key": "production_qty",
        "label": "Work Output Qty",
        "type": "sum",
        "source_type": ["work_output", "production"],
        "field": "output_qty",
    },
]


def load_metric_specs(path: Path) -> list[dict[str, Any]]:
    """Load metric specs from JSON.

    Supported shapes:
    - ``{"metrics": [{...}]}``
    - ``[{...}]``
    - ``{"metric_key": {"type": "...", ...}}``
    """

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, dict) and isinstance(payload.get("metrics"), list):
        return [dict(metric) for metric in payload["metrics"]]
    if isinstance(payload, list):
        return [dict(metric) for metric in payload]
    if isinstance(payload, dict):
        metrics: list[dict[str, Any]] = []
        for key, spec in payload.items():
            if isinstance(spec, dict):
                metric = dict(spec)
                metric.setdefault("key", key)
                metrics.append(metric)
        if metrics:
            return metrics
    raise ValueError(f"Invalid metric config shape: {path}")


def compute_metrics(records: list[StandardRecord], specs: list[dict[str, Any]] | None = None) -> list[SummaryMetric]:
    """Compute configured summary metrics."""

    metric_specs = specs or DEFAULT_METRIC_SPECS
    metrics: list[SummaryMetric] = []

    for spec in metric_specs:
        metric_type = str(spec.get("type", "")).strip()
        if metric_type == "sum":
            value = _sum_field(records, spec)
        elif metric_type == "distinct_count":
            value = _distinct_count(records, spec)
        elif metric_type == "count":
            value = _count_records(records, spec)
        elif metric_type == "count_group_lte":
            value = _count_group_threshold(records, spec, operator="lte")
        elif metric_type == "count_group_gte":
            value = _count_group_threshold(records, spec, operator="gte")
        else:
            value = 0

        metrics.append(
            SummaryMetric(
                key=str(spec.get("key", "")),
                label=str(spec.get("label") or spec.get("key", "")),
                value=_clean_number(value),
                unit=str(spec.get("unit", "")),
                source_type=_source_label(spec.get("source_type")),
                description=str(spec.get("description", "")),
            )
        )

    return metrics


def metric_value(metrics: list[SummaryMetric], key: str, default: float = 0.0) -> float:
    """Return a numeric metric value by key."""

    for metric in metrics:
        if metric.key == key:
            return float(metric.value)
    return default


def _sum_field(records: list[StandardRecord], spec: dict[str, Any]) -> float:
    field = str(spec.get("field", ""))
    return sum(_to_float(record.fields.get(field)) for record in records if _matches_source(record, spec))


def _distinct_count(records: list[StandardRecord], spec: dict[str, Any]) -> int:
    field = str(spec.get("field", ""))
    values = {
        str(record.fields.get(field, "")).strip()
        for record in records
        if _matches_source(record, spec) and str(record.fields.get(field, "")).strip()
    }
    return len(values)


def _count_records(records: list[StandardRecord], spec: dict[str, Any]) -> int:
    return sum(1 for record in records if _matches_source(record, spec))


def _count_group_threshold(records: list[StandardRecord], spec: dict[str, Any], operator: str) -> int:
    group_by = str(spec.get("group_by", ""))
    value_field = str(spec.get("value_field", ""))
    threshold = _to_float(spec.get("threshold", 0))
    groups: dict[str, float] = defaultdict(float)

    for record in records:
        if not _matches_source(record, spec):
            continue
        group_key = str(record.fields.get(group_by, "")).strip()
        if not group_key:
            continue
        groups[group_key] += _to_float(record.fields.get(value_field))

    if operator == "gte":
        return sum(1 for value in groups.values() if value >= threshold)
    return sum(1 for value in groups.values() if value <= threshold)


def _matches_source(record: StandardRecord, spec: dict[str, Any]) -> bool:
    configured = spec.get("source_type")
    if not configured:
        return True
    if isinstance(configured, str):
        allowed = {configured}
    else:
        allowed = {str(value) for value in configured}
    return record.source_type in allowed


def _source_label(configured: object) -> str:
    if configured is None:
        return ""
    if isinstance(configured, str):
        return configured
    return ",".join(str(value) for value in configured)


def _to_float(value: object) -> float:
    if value in (None, ""):
        return 0.0
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return 0.0


def _clean_number(value: float | int) -> float | int:
    as_float = float(value)
    return int(as_float) if as_float.is_integer() else round(as_float, 4)

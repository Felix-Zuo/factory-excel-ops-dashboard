"""Shared data models for normalized factory spreadsheet records.

The workbench keeps the model intentionally small. Local projects can extend
these records through configuration instead of hard-coding sheet names or
internal identifiers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceRef:
    """Traceability metadata for one parsed row."""

    source_file: str
    source_sheet: str = ""
    row_number: int = 0


@dataclass(frozen=True)
class ClassifiedFile:
    """Result returned by the file classifier."""

    path: Path
    source_type: str
    confidence: float
    reasons: list[str] = field(default_factory=list)
    headers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class StandardRecord:
    """One normalized record used by the dashboard engine."""

    source_type: str
    fields: dict[str, Any]
    source: SourceRef


@dataclass(frozen=True)
class SummaryMetric:
    """One configured metric exported to dashboards and reporting payloads."""

    key: str
    label: str
    value: float | int
    unit: str = ""
    source_type: str = ""
    description: str = ""


@dataclass(frozen=True)
class DashboardSummary:
    """Computed result exported to JSON and HTML.

    The named quantity fields remain for compatibility with earlier sample
    versions. New profiles should read the configured ``metrics`` list.
    """

    file_count: int
    record_count: int
    inventory_items: int
    out_of_stock_items: int
    order_demand_qty: float
    shipment_qty: float
    purchase_qty: float
    production_qty: float
    by_source_type: dict[str, int]
    metrics: list[SummaryMetric] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

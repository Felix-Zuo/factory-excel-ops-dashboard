"""Shared data models for normalized factory spreadsheet records.

The public project keeps the model intentionally small. Company-specific
projects can extend these records through configuration instead of hard-coding
private sheet names or internal identifiers.
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
class DashboardSummary:
    """Minimal computed result exported to JSON and HTML."""

    file_count: int
    record_count: int
    inventory_items: int
    out_of_stock_items: int
    order_demand_qty: float
    shipment_qty: float
    purchase_qty: float
    production_qty: float
    by_source_type: dict[str, int]
    warnings: list[str] = field(default_factory=list)

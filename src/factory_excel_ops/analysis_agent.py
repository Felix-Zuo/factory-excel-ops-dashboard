"""Build structured context for an operations analysis agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_analysis_context(summary_path: Path, output_path: Path) -> dict[str, Any]:
    """Convert a dashboard summary into a compact analysis-agent payload."""

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    context = {
        "schema": "factory_excel_ops.analysis_context.v1",
        "role": "operations_analysis_agent",
        "objective": "Explain operational risk, summarize changes, and recommend follow-up checks.",
        "input_summary": summary,
        "analysis_sections": [
            {
                "id": "inventory_risk",
                "title": "Inventory Risk",
                "signals": ["inventory_items", "out_of_stock_items"],
                "expected_output": "Highlight out-of-stock exposure and suggest the next inventory validation step.",
            },
            {
                "id": "demand_fulfillment",
                "title": "Demand and Fulfillment",
                "signals": ["order_demand_qty", "shipment_qty", "production_qty"],
                "expected_output": "Compare demand, shipment, and production quantities at a high level.",
            },
            {
                "id": "procurement_pressure",
                "title": "Procurement Pressure",
                "signals": ["purchase_qty", "warnings"],
                "expected_output": "Identify purchase-plan pressure and incomplete source data.",
            },
        ],
        "guardrails": [
            "Use the supplied summary as the source of truth.",
            "Separate confirmed facts from suggested follow-up checks.",
            "Do not invent source rows that are not present in the summary.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
    return context

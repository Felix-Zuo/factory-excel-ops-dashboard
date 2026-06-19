"""Build structured context for an operations analysis agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_analysis_context(summary_path: Path, output_path: Path) -> dict[str, Any]:
    """Convert a dashboard summary into a compact analysis-agent payload."""

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    metrics = summary.get("metrics") or []
    metric_keys = [metric.get("key") for metric in metrics if metric.get("key")]
    context = {
        "schema": "factory_excel_ops.analysis_context.v1",
        "role": "operations_analysis_agent",
        "objective": "Explain operational signals, data quality risks, and recommended follow-up checks.",
        "input_summary": summary,
        "analysis_sections": [
            {
                "id": "data_coverage",
                "title": "Data Coverage",
                "signals": ["file_count", "record_count", "by_source_type", "warnings"],
                "expected_output": "Explain which source types were recognized and which inputs need validation.",
            },
            {
                "id": "configured_metrics",
                "title": "Configured Metrics",
                "signals": metric_keys,
                "expected_output": "Summarize the configured metrics without assuming a fixed industry workflow.",
            },
            {
                "id": "next_checks",
                "title": "Next Checks",
                "signals": ["warnings", "metrics"],
                "expected_output": "Recommend the next spreadsheet, mapping, or metric checks to improve confidence.",
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

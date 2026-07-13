"""Standalone HTML dashboard export."""

from __future__ import annotations

import html
import json
from dataclasses import asdict
from pathlib import Path

from .models import DashboardSummary


def export_dashboard(summary: DashboardSummary, output_path: Path) -> Path:
    """Write a self-contained HTML dashboard."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(asdict(summary), ensure_ascii=False, indent=2)
    cards = [("Files", summary.file_count), ("Records", summary.record_count)]
    if summary.metrics:
        cards.extend((metric.label, _format_metric_value(metric.value, metric.unit)) for metric in summary.metrics)
    else:
        cards.extend(
            [
                ("Tracked Items", summary.inventory_items),
                ("Zero / Negative Stock", summary.out_of_stock_items),
                ("Demand Qty", f"{summary.order_demand_qty:,.0f}"),
                ("Fulfilled Qty", f"{summary.shipment_qty:,.0f}"),
                ("Replenishment Qty", f"{summary.purchase_qty:,.0f}"),
                ("Work Output Qty", f"{summary.production_qty:,.0f}"),
            ]
        )
    card_html = "\n".join(
        f"<section class='card'><span>{html.escape(label)}</span><strong>{html.escape(str(value))}</strong></section>"
        for label, value in cards
    )
    source_rows = "\n".join(
        f"<tr><td>{html.escape(source)}</td><td>{count}</td></tr>"
        for source, count in summary.by_source_type.items()
    )
    warning_rows = "\n".join(f"<li>{html.escape(warning)}</li>" for warning in summary.warnings) or "<li>No warnings.</li>"

    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Excel Operations Data Workbench</title>
  <style>
    body {{ margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #f5f7fb; color: #172033; }}
    header {{ padding: 32px 44px; background: #10233f; color: white; }}
    header p {{ color: #b9c7dc; margin: 8px 0 0; }}
    main {{ padding: 28px 44px 44px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 16px; }}
    .card {{ background: white; border: 1px solid #d8e0ec; border-radius: 10px; padding: 18px; box-shadow: 0 6px 18px rgba(16,35,63,.07); }}
    .card span {{ display: block; color: #627089; font-size: 13px; }}
    .card strong {{ display: block; margin-top: 12px; font-size: 30px; color: #0f7dd7; }}
    .panel {{ margin-top: 24px; background: white; border: 1px solid #d8e0ec; border-radius: 10px; padding: 20px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #e7edf5; text-align: left; padding: 10px; }}
    code, pre {{ background: #0b1220; color: #d7e4f5; border-radius: 8px; padding: 14px; overflow: auto; }}
  </style>
</head>
<body>
  <header>
    <h1>Excel Operations Data Workbench</h1>
    <p>Local-first run using sample spreadsheet operations data.</p>
  </header>
  <main>
    <div class="grid">{card_html}</div>
    <section class="panel">
      <h2>Records by Source Type</h2>
      <table><thead><tr><th>Source type</th><th>Rows</th></tr></thead><tbody>{source_rows}</tbody></table>
    </section>
    <section class="panel">
      <h2>Warnings</h2>
      <ul>{warning_rows}</ul>
    </section>
    <section class="panel">
      <h2>Machine-readable Summary</h2>
      <pre>{html.escape(payload)}</pre>
    </section>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )
    return output_path


def _format_metric_value(value: float | int, unit: str = "") -> str:
    formatted = f"{value:,.0f}" if isinstance(value, (float, int)) else str(value)
    return f"{formatted} {unit}".strip()

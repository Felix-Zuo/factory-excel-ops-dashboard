"""Machine-readable integration contract for automation tools."""

from __future__ import annotations

import json
from pathlib import Path


def default_agent_interface() -> dict[str, object]:
    """Return the default contract exposed to external automation tools."""

    root = Path(__file__).resolve().parents[2]
    static_path = root / "agent_interface.json"
    if static_path.exists():
        return json.loads(static_path.read_text(encoding="utf-8"))
    return {
        "name": "Factory Excel Ops Dashboard",
        "version": "0.1.0",
        "entrypoints": [
            {
                "name": "run_pipeline",
                "command": "python -m factory_excel_ops.cli run --input <input_dir> --output <output_dir>",
            }
        ],
    }


def write_agent_interface(output_path: Path) -> Path:
    """Write the integration contract as JSON."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(default_agent_interface(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path

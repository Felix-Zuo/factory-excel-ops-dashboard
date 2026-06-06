"""Command line interface for the public demo."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .classifier import FileClassifier
from .agent_interface import write_agent_interface
from .dashboard import export_dashboard
from .field_mapper import FieldMapper
from .ingest import ingest_paths, summarize


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Factory Excel Ops demo pipeline.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    run = subcommands.add_parser("run", help="Ingest files and export dashboard.")
    run.add_argument("--input", required=True, type=Path, help="Input folder with CSV/XLSX files.")
    run.add_argument("--output", required=True, type=Path, help="Output folder.")
    run.add_argument("--file-types", type=Path, default=Path("config/sample_file_types.json"))
    run.add_argument("--field-mapping", type=Path, default=Path("config/sample_field_mapping.json"))

    spec = subcommands.add_parser("agent-spec", help="Export machine-readable integration contract.")
    spec.add_argument("--output", required=True, type=Path, help="JSON output path.")

    args = parser.parse_args()
    if args.command == "run":
        return _run(args)
    if args.command == "agent-spec":
        write_agent_interface(args.output)
        print(f"Agent interface: {args.output}")
        return 0
    return 2


def _run(args: argparse.Namespace) -> int:
    input_dir: Path = args.input
    output_dir: Path = args.output
    paths = sorted(
        path for path in input_dir.iterdir()
        if path.suffix.lower() in {".csv", ".xlsx", ".xlsm"}
    )
    classifier = FileClassifier.from_json(args.file_types) if args.file_types.exists() else FileClassifier()
    mapper = FieldMapper.from_json(args.field_mapping) if args.field_mapping.exists() else FieldMapper()
    records, warnings = ingest_paths(paths, classifier, mapper)
    summary = summarize(records, file_count=len(paths), warnings=warnings)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(asdict(summary), ensure_ascii=False, indent=2), encoding="utf-8")
    export_dashboard(summary, output_dir / "dashboard.html")

    print(f"Files: {len(paths)}")
    print(f"Records: {len(records)}")
    print(f"Dashboard: {output_dir / 'dashboard.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

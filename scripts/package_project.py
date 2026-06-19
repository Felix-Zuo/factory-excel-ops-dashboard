"""Create a clean portable package for handoff or internal reuse."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "backup",
    "dist",
    "diagnostics",
    "dropbox",
    "input",
    "output",
    "venv",
}

EXCLUDED_SUFFIXES = {
    ".7z",
    ".exe",
    ".rar",
    ".xls",
    ".xlsm",
    ".xlsx",
    ".log",
    ".pyc",
    ".pyo",
    ".tmp",
    ".tsv",
    ".zip",
}


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    return cleaned.strip("-") or "factory-excel-ops-dashboard"


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part.lower().startswith(".git") for part in rel.parts):
        return False
    if any(part.lower().startswith("output") for part in rel.parts):
        return False
    if any(part.lower().endswith(".egg-info") for part in rel.parts):
        return False
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return False
    if path.suffix.lower() == ".csv" and rel.parts[:1] != ("sample_data",):
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def build_package(root: Path, output_dir: Path, name: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    package_path = output_dir / f"{safe_name(name)}.zip"
    if package_path.exists():
        package_path.unlink()

    with ZipFile(package_path, "w", ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if should_include(path, root):
                archive.write(path, path.relative_to(root))

    return package_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Package the project without local cache/output folders.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--name", default="factory-excel-ops-dashboard")
    args = parser.parse_args()

    package_path = build_package(args.root.resolve(), args.output.resolve(), args.name)
    print(f"Package: {package_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Factory Excel Ops Dashboard

[![CI](https://github.com/Felix-Zuo/factory-excel-ops-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Felix-Zuo/factory-excel-ops-dashboard/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-0f766e)
![Mode](https://img.shields.io/badge/mode-local--first-334155)

Local-first spreadsheet operations workbench for teams that still run critical
processes through Excel, CSV exports, shared folders, and manual reporting.

The project classifies incoming files, maps noisy headers into a standard data
model, computes configurable metrics, and exports a standalone HTML dashboard
plus JSON summaries that automation agents can read. The public repository uses
synthetic data and generic operations terminology so it can be adapted beyond a
single factory, product line, or private workbook template.

## What It Does

- Classifies spreadsheet-like files by content, not only by filename.
- Normalizes headers with case, spacing, separator, and unit noise.
- Supports configurable source types, field aliases, and metric profiles.
- Computes stock, demand, fulfillment, replenishment, and work-output metrics.
- Exports a local HTML dashboard and machine-readable `summary.json`.
- Provides an agent interface for reporting bots or workflow assistants.
- Keeps private adapters, real exports, logs, and packages outside Git.

## Public Boundary

This repository is a sanitized showcase and reusable toolkit. It is informed by
private spreadsheet-operations work, but it does not contain private workbooks,
customer names, supplier names, BOMs, production logs, desktop binaries, or
company-specific adapter rules.

The version history documents public productization decisions and sanitized
capabilities that were folded into this generic toolkit. It is not meant to
pretend that every private feature, operator workflow, or internal deployment is
present in this public repository.

## Quick Start

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m factory_excel_ops.cli validate-config
.\.venv\Scripts\python -m factory_excel_ops.cli run --input sample_data --output output
```

If `py` is not available, use `python` instead.

Open the generated dashboard:

```powershell
start output\dashboard.html
```

For a quick Windows demo after installation:

```powershell
.\scripts\run_demo.cmd
```

## Configuration Profile

The default public profile is intentionally generic:

- `config/sample_file_types.json`: source signatures for `inventory`,
  `demand`, `fulfillment`, `replenishment`, and `work_output`.
- `config/sample_field_mapping.json`: header aliases such as `Item Code`,
  `Available Qty (EA)`, `Ship Qty`, and `Due-Date`.
- `config/sample_metrics.json`: metric definitions for dashboard cards and
  analysis context.

Run with a custom profile:

```powershell
python -m factory_excel_ops.cli run `
  --input sample_data `
  --output output `
  --file-types config\sample_file_types.json `
  --field-mapping config\sample_field_mapping.json `
  --metrics config\sample_metrics.json
```

## Agent Interface

Automation tools can inspect the project contract:

```powershell
python -m factory_excel_ops.cli agent-spec --output output\agent_interface.json
```

Generate structured context for an operations analysis assistant:

```powershell
python -m factory_excel_ops.cli analysis-context --summary output\summary.json --output output\analysis_context.json
```

The static interface file is also available at `agent_interface.json`.

## Validation

```powershell
python -m pytest -q
python -m factory_excel_ops.cli validate-config
python -m factory_excel_ops.cli run --input sample_data --output output
python -m factory_excel_ops.cli analysis-context --summary output\summary.json --output output\analysis_context.json
```

The test suite can run directly from a fresh checkout because `pyproject.toml`
adds `src` to the pytest import path.

## Product Materials

- [Public evolution](docs/product_evolution.md)
- [Architecture](docs/architecture.md)
- [Configuration cookbook](docs/configuration_cookbook.md)
- [Data safety checklist](docs/data_safety_checklist.md)
- [Quality gates](docs/quality_gates.md)
- [Threat model](docs/threat_model.md)
- [GitHub maintenance](docs/github_maintenance.md)
- [Roadmap](docs/roadmap.md)
- [Showcase design benchmark](docs/showcase_design_benchmark.md)
- [Private adapter guide](docs/private_adapter_guide.md)
- [Agent interface guide](docs/agent_interface.md)
- [Product showcase page](docs/showcase.html)

## Project Structure

```text
factory-excel-ops-dashboard/
  agent_interface.json     Machine-readable integration contract
  config/                 Example source, field, and metric profiles
  docs/                   Product, adapter, architecture, and safety notes
  sample_data/            Synthetic demo data only
  scripts/                Demo runner and clean package helper
  src/factory_excel_ops/  Reusable Python package
  tests/                  Regression tests for the public demo
```

## Packaging

Create a clean package for another workstation or adapter build:

```powershell
python scripts\package_project.py --name factory-excel-ops-dashboard --output output
```

Generated packages belong in `output/` or another ignored folder.

## Current Version

`0.2.1` adds config validation, CI, Dependabot, safer classification confidence
handling, richer project governance, and a cleaner GitHub maintenance surface.

## License

MIT.

# Changelog

All notable public changes to Factory Excel Ops Dashboard are recorded here.
The project uses semantic versions while it is still pre-1.0.

## [0.2.2] - 2026-06-24

### Added

- Upgraded the product page with a code-and-delivery workbench, including run
  path, profile shape, summary contract, release gate, key files, and generated
  artifact surface.
- Added a public product-page entry point for GitHub Pages.

### Changed

- Renamed the public integration surface to `integration_interface.json` and
  `integration-spec`.
- Reframed structured review output as reporting context for local workflow
  handoff.
- Removed public showcase wording that made the project look like a generated
  demo instead of a maintained data product.
- Reworked README data-boundary language so the public repository reads like a
  reusable toolkit instead of a private-project explanation.

### Verified

- `python -m pytest -q`
- `python -m factory_excel_ops.cli validate-config`
- `python -m factory_excel_ops.cli run --input sample_data --output output`
- `python -m factory_excel_ops.cli analysis-context --summary output\summary.json --output output\analysis_context.json`
- `python scripts\package_project.py --name factory-excel-ops-dashboard-v0.2.2 --output output`

## [0.2.1] - 2026-06-19

### Added

- Added `validate-config` CLI command for source, field, and metric profile
  validation.
- Added GitHub Actions CI for tests, config validation, demo generation,
  analysis-context generation, package creation, and package safety checks.
- Added Dependabot configuration for Python and GitHub Actions dependencies.
- Added `.editorconfig` and Python `dev` optional dependencies.

### Changed

- Classification now normalizes header tokens before scoring, so headers such
  as `Item Code` and `Available Qty (EA)` match public profile signatures.
- The run command now validates config before processing and prints data
  warnings directly in CLI output.
- File ingestion now skips low-confidence classifications by default.

### Fixed

- Unsupported metric types now fail explicitly instead of silently returning
  zero.

### Verified

- `python -m pytest -q`
- `python -m factory_excel_ops.cli validate-config`
- `python -m factory_excel_ops.cli run --input sample_data --output output`
- `python -m factory_excel_ops.cli analysis-context --summary output\summary.json --output output\analysis_context.json`
- `python scripts\package_project.py --name factory-excel-ops-dashboard-release-check --output output`

## [0.2.0] - 2026-06-19

### Added

- Added configurable metric profiles through `config/sample_metrics.json`.
- Added generic operations source types: `inventory`, `demand`,
  `fulfillment`, `replenishment`, and `work_output`.
- Added summary metric objects to `summary.json` for dashboards and reporting
  context.
- Added public product materials: evolution history, architecture,
  configuration cookbook, roadmap, and data safety checklist.
- Added GitHub issue templates and a pull request template.

### Changed

- Reframed the demo from a fixed manufacturing dashboard into a reusable
  spreadsheet operations workbench.
- Updated sample data to use synthetic SKU, account, partner, and work-center
  terminology instead of private-product-shaped examples.
- Updated dashboard cards to render configured metrics instead of fixed labels.
- Updated reporting context so it does not assume one industry workflow.
- Improved header matching for spacing, separators, casing, and unit suffixes.

### Fixed

- Prevented the packaging helper from including ignored private data folders,
  executable packages, Excel workbooks, or non-sample CSV files.
- Removed a risky default alias overlap where `completed_qty` could be treated
  as both fulfillment and work output in the public config.

### Verified

- `python -m pytest -q`
- `python -m factory_excel_ops.cli run --input sample_data --output output`
- `python -m factory_excel_ops.cli analysis-context --summary output\summary.json --output output\analysis_context.json`

## [0.1.1] - 2026-06-13

### Fixed

- Added `pythonpath = ["src"]` to pytest config so tests pass from a fresh
  checkout without requiring editable installation first.

### Verified

- `python -m pytest -q`

## [0.1.0] - 2026-06-09

### Added

- Initial sanitized public toolkit baseline.
- CSV/XLSX ingestion, content-based file classification, field mapping,
  summary generation, HTML dashboard export, and integration interface.
- Synthetic sample data and public privacy boundaries.

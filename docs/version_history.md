# Version History

This file keeps the product line readable from the beta releases onward. The
entries are written as product notes: what changed, why it mattered, and what
was checked before the next pass.

## 0.3.0-beta.1 - 2026-07-16

### Shipped

- Added `adapt`, a code-first profile builder for unfamiliar CSV/XLSX folders.
- Added optional model-assisted boundary handling for low-confidence tables.
- Added `adaptation_report.json` so generated configs are reviewable before
  they are used in a run.
- Refreshed the product page with stronger motion, more direct copy, and a
  clearer story around table adaptation.

### Checked

- `python -m pytest -q`
- `python -m factory_excel_ops.cli adapt --input sample_data --output output\adapted_profile`
- `python -m factory_excel_ops.cli validate-config --file-types output\adapted_profile\file_types.json --field-mapping output\adapted_profile\field_mapping.json --metrics output\adapted_profile\metrics.json`
- `python -m factory_excel_ops.cli run --input sample_data --output output`

## 0.2.2 - 2026-06-24

### Shipped

- Upgraded the GitHub Pages product page from a static note into a full product
  surface.
- Added product-page metadata, social preview image, and a clearer integration
  story.
- Reworked the README and docs so the project reads like a reusable operations
  workbench, not a one-off folder script.

### Checked

- Tests, config validation, sample run, analysis-context export, and package
  creation.

## 0.2.1 - 2026-06-19

### Shipped

- Added `validate-config`.
- Added GitHub Actions CI across Python 3.10, 3.11, and 3.12.
- Added package safety checks so generated output, workbooks, and runtime
  artifacts stay out of release packages.
- Improved header normalization before classification.

### Checked

- Tests, config validation, sample run, analysis-context export, and package
  safety.

## 0.2.0 - 2026-06-19

### Shipped

- Moved the workbench to configurable source, field, and metric profiles.
- Added generic operations source types: inventory, demand, fulfillment,
  replenishment, and work output.
- Added metric cards and structured review context.
- Added product docs, issue templates, and pull request template.

### Checked

- Tests, sample run, and analysis-context export.

## Beta 0.1.1 - 2026-06-13

### Shipped

- Fixed fresh-checkout test execution by adding `src` to the pytest import path.
- Kept the package usable without requiring editable install steps first.

### Checked

- `python -m pytest -q`

## Beta 0.1.0 - 2026-06-09

### Shipped

- Established the first reusable toolkit baseline.
- Added CSV/XLSX ingestion, source classification, field mapping, dashboard
  export, sample fixtures, and the first package boundary.

### Checked

- Local sample run and package review.

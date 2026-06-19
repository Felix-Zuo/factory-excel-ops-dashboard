# Quality Gates

This project treats the public repository as a reusable toolkit, not a one-off
demo. The gates below define what must pass before a release or GitHub-facing
update is considered ready.

## Required Gates

| Gate | Command | Purpose |
| --- | --- | --- |
| Unit tests | `python -m pytest -q` | Protect classifier, field mapping, metrics, packaging, and validation behavior. |
| Config validation | `python -m factory_excel_ops.cli validate-config` | Catch broken profiles before any spreadsheet is processed. |
| Demo run | `python -m factory_excel_ops.cli run --input sample_data --output output` | Confirm the public workflow still produces `summary.json` and `dashboard.html`. |
| Agent context | `python -m factory_excel_ops.cli analysis-context --summary output\summary.json --output output\analysis_context.json` | Confirm downstream automation payloads still work. |
| Package safety | `python scripts\package_project.py --name release-check --output output` | Confirm packages exclude private data, generated output, and local artifacts. |

## CI Coverage

The GitHub Actions workflow runs on:

- pushes to `main`
- pull requests targeting `main`
- manual `workflow_dispatch`

It tests Python `3.10`, `3.11`, and `3.12`, then checks package contents for:

- private input folders
- generated output folders
- Python egg-info metadata
- Excel workbooks
- executable packages
- nested zip/archive files
- non-sample CSV files

## Release Rule

Do not tag or push a release-style update if any required gate fails. Fix the
gate first, then update `CHANGELOG.md` with the validation evidence.

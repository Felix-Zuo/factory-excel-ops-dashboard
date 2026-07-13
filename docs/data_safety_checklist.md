# Data Safety Checklist

Run this checklist before publishing, packaging, or sharing the repository.

## Repository Check

```powershell
git status -sb
git ls-files
```

Look for:

- Real `.xls`, `.xlsx`, `.xlsm`, `.csv`, `.tsv`, `.zip`, `.7z`, `.rar`, `.exe`
  files outside approved fixtures.
- Customer, supplier, employee, order, BOM, shipment, finance, HR, or production
  identifiers.
- Logs, diagnostics, generated dashboards, screenshots, and packaged binaries.

## Search Check

```powershell
rg -n "customer|supplier|employee|invoice|password|secret|token|internal_brand" `
  --glob "!**/.git/**" `
  --glob "!**/.venv/**" `
  --glob "!output/**"
```

Expected result: only generic documentation language or intentionally sample
sample names.

## Package Check

```powershell
python scripts\package_project.py --name safety-check --output output
```

Open the generated zip and confirm it contains no:

- `input/`
- `dropbox/`
- `backup/`
- `diagnostics/`
- `output*`
- `*.egg-info`
- Excel workbooks
- executable packages
- non-sample CSV files

## GitHub Check

Before pushing:

- `python -m pytest -q`
- `python -m factory_excel_ops.cli validate-config`
- `python -m factory_excel_ops.cli run --input sample_data --output output`
- `python -m factory_excel_ops.cli analysis-context --summary output\summary.json --output output\analysis_context.json`
- `git status -sb`

Do not push if the working tree contains unrelated local files or if a command
generated sensitive artifacts outside ignored folders.

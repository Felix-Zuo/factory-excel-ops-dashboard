# Release Checklist

Use this checklist before tagging or pushing a GitHub-facing update.

## Version

- Update `VERSION`.
- Update `pyproject.toml`.
- Update `src/factory_excel_ops/__init__.py`.
- Update `integration_interface.json`.
- Add a `CHANGELOG.md` entry.

## Validation

```powershell
python -m pytest -q
python -m factory_excel_ops.cli validate-config
python -m factory_excel_ops.cli run --input sample_data --output output
python -m factory_excel_ops.cli adapt --input sample_data --output output\adapted_profile
python -m factory_excel_ops.cli validate-config `
  --file-types output\adapted_profile\file_types.json `
  --field-mapping output\adapted_profile\field_mapping.json `
  --metrics output\adapted_profile\metrics.json
python -m factory_excel_ops.cli analysis-context --summary output\summary.json --output output\analysis_context.json
python scripts\package_project.py --name factory-excel-ops-dashboard-release-check --output output
```

## Data Safety

```powershell
git status -sb
git ls-files
rg -n "password|secret|token|internal_brand" --glob "!**/.git/**" --glob "!output/**"
```

Review any hits before pushing.

## GitHub

- Commit only intended files.
- Push after tests and data-safety checks pass.
- Keep repository topics and description aligned with the current product
  boundary.
- Keep `docs/.nojekyll` in place for the static GitHub Pages site.
- Confirm the Pages source is `main` / `docs` and the product page returns 200.

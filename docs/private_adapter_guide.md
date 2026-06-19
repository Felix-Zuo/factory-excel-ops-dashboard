# Adapter Guide

Use adapters when a deployment has custom workbook names, field names, metrics,
or business rules. Adapters let the core engine stay generic while each team
keeps its own terminology and file layout outside the public repository.

Recommended adapter layout:

```text
factory-excel-ops-adapter/
  config/file_types.private.json
  config/field_mapping.private.json
  config/metrics.private.json
  fixtures/synthetic/
  tests/test_private_profile.py
```

An adapter can be copied into a packaged version of the app or loaded by an
automation tool before running the pipeline.

Example:

```powershell
python -m factory_excel_ops.cli run `
  --input C:\safe\demo_input `
  --output output `
  --file-types adapter\config\file_types.private.json `
  --field-mapping adapter\config\field_mapping.private.json `
  --metrics adapter\config\metrics.private.json
```

Keep the adapter repository private if it contains real source names,
workbook-specific rules, or customer-specific fields. Publish only synthetic
fixtures and generic examples.

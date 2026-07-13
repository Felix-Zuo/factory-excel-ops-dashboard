# Adapter Integration Guide

Use adapters when a deployment has custom workbook names, field names, metrics,
or business rules. Adapters let the core engine stay generic while each team
keeps its own terminology and file layout in its operating environment.

Recommended adapter layout:

```text
factory-excel-ops-adapter/
  config/file_types.local.json
  config/field_mapping.local.json
  config/metrics.local.json
  fixtures/sample/
  tests/test_local_profile.py
```

An adapter can be copied into a packaged version of the app or loaded by an
automation tool before running the pipeline.

Example:

```powershell
python -m factory_excel_ops.cli run `
  --input C:\safe\sample_input `
  --output output `
  --file-types adapter\config\file_types.local.json `
  --field-mapping adapter\config\field_mapping.local.json `
  --metrics adapter\config\metrics.local.json
```

Keep adapters in a controlled repository when they contain real source names,
workbook-specific rules, or customer-specific fields. Share only sample fixtures
and generic examples.

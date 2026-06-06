# Adapter Guide

Use adapters when a factory has custom workbook names, field names, or business
rules. Adapters let the core engine stay generic while each deployment keeps its
own terminology and file layout.

Recommended adapter layout:

```text
factory-excel-ops-adapter/
  config/file_types.private.json
  config/field_mapping.private.json
  rules/product_family.private.json
  rules/line_capacity.private.json
```

An adapter can be copied into a packaged version of the app or loaded by an
automation tool before running the pipeline.

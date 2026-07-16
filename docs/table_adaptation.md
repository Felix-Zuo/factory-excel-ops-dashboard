# Table Adaptation Guide

The workbench can now build a runnable profile from a folder of unfamiliar
spreadsheets. Use this when the source files are useful, but their headers,
file names, or quantity columns do not match the default profile yet.

## Code-First Flow

```powershell
python -m factory_excel_ops.cli adapt --input incoming_exports --output output\incoming_profile
```

The command inspects:

- file names
- headers
- column shapes such as number, date-like value, blank, and short text
- a small preview window for local classification only

It writes:

```text
output/incoming_profile/
  file_types.json
  field_mapping.json
  metrics.json
  adaptation_report.json
```

Validate the generated profile before running it:

```powershell
python -m factory_excel_ops.cli validate-config `
  --file-types output\incoming_profile\file_types.json `
  --field-mapping output\incoming_profile\field_mapping.json `
  --metrics output\incoming_profile\metrics.json
```

Run with the generated profile:

```powershell
python -m factory_excel_ops.cli run `
  --input incoming_exports `
  --output output\incoming_run `
  --file-types output\incoming_profile\file_types.json `
  --field-mapping output\incoming_profile\field_mapping.json `
  --metrics output\incoming_profile\metrics.json
```

## Boundary Help

Most folders should not need a model call. Use boundary help only when headers
are too vague for local rules, such as `Amount`, `Ref`, or `Status` columns
that need business context.

```powershell
$env:FACTORY_EXCEL_OPS_API_KEY = "<your key>"
$env:FACTORY_EXCEL_OPS_MODEL_ENDPOINT = "https://your-provider.example/v1/chat/completions"
$env:FACTORY_EXCEL_OPS_MODEL = "<model name>"

python -m factory_excel_ops.cli adapt `
  --input incoming_exports `
  --output output\incoming_profile `
  --enable-model-assist
```

The generated files never contain the API key. By default, the model request is
limited to headers and column-shape sketches, not raw business rows.

## Review Checklist

- Check `adaptation_report.json` for low confidence files.
- Keep generated profiles in `output/` until reviewed.
- Move reviewed configs into an adapter repository or a controlled deployment
  folder.
- Run `validate-config` before every package or handoff.
- Run the pipeline once and inspect `summary.json` warnings before relying on
  the dashboard.


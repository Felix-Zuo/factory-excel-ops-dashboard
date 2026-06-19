# Agent Interface

This project exposes a small integration contract for automation tools.

## Main Command

```powershell
python -m factory_excel_ops.cli run --input <input_dir> --output <output_dir>
```

Expected result:

```text
<output_dir>/summary.json
<output_dir>/dashboard.html
```

## Capability Discovery

```powershell
python -m factory_excel_ops.cli agent-spec --output output/agent_interface.json
```

The exported JSON describes supported file extensions, source types, standard
fields, config files, integration targets, and command entrypoints.

## Config Validation

```powershell
python -m factory_excel_ops.cli validate-config
```

This command validates source signatures, field aliases, metric types,
duplicate metric keys, and references between metric configs and the declared
profile. Run it before packaging a custom adapter.

## Analysis Context

```powershell
python -m factory_excel_ops.cli analysis-context --summary output/summary.json --output output/analysis_context.json
```

This command turns the computed summary into a structured payload for an
analysis agent, reporting assistant, or workflow orchestrator.

## Adapter Pattern

An external automation tool can prepare a folder with:

```text
config/sample_file_types.json
config/sample_field_mapping.json
config/sample_metrics.json
sample_data or real_input_folder
```

Then call the pipeline and read `summary.json` for downstream reporting or
packaging.

Custom configs can be passed directly:

```powershell
python -m factory_excel_ops.cli run `
  --input <input_dir> `
  --output <output_dir> `
  --file-types <file_types.json> `
  --field-mapping <field_mapping.json> `
  --metrics <metrics.json> `
  --min-confidence 0.2 `
  --max-file-mb 25
```

## Packaging

Create a clean handoff package:

```powershell
python scripts/package_project.py --name factory-excel-ops-dashboard --output output
```

The package excludes local cache, generated output, virtual environments, and
runtime artifacts.

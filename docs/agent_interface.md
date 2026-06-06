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
fields, and command entrypoints.

## Adapter Pattern

An external automation tool can prepare a folder with:

```text
config/sample_file_types.json
config/sample_field_mapping.json
sample_data or real_input_folder
```

Then call the pipeline and read `summary.json` for downstream reporting or
packaging.

## Packaging

Create a clean handoff package:

```powershell
python scripts/package_project.py --name factory-excel-ops-dashboard --output output
```

The package excludes local cache, generated output, virtual environments, and
runtime artifacts.

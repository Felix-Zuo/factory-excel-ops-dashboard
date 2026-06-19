## Summary

-

## Changed

-

## Validation

- [ ] `python -m pytest -q`
- [ ] `python -m factory_excel_ops.cli run --input sample_data --output output`
- [ ] `python -m factory_excel_ops.cli analysis-context --summary output\summary.json --output output\analysis_context.json`
- [ ] Packaging check, if packaging behavior changed

## Data Safety

- [ ] No real customer, supplier, employee, order, BOM, shipment, finance, HR, production, or procurement data.
- [ ] No private workbook names, logs, diagnostics, packaged executables, or local output artifacts.
- [ ] Any new fixtures are synthetic and documented.

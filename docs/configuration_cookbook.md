# Configuration Cookbook

Use this guide when adapting the public toolkit to a new spreadsheet workflow.

## 1. Define Source Types

Create source types based on the role a file plays, not the exact private
workbook name.

Good:

```json
{
  "maintenance_demand": {
    "headers": ["ticket_id", "asset_id", "required_qty", "due_date"],
    "values": ["maintenance", "request"],
    "filename": ["maintenance", "demand"]
  }
}
```

Avoid:

```json
{
  "line_3_private_june_file": {
    "headers": ["private_internal_header"],
    "filename": ["real_customer_file_name"]
  }
}
```

## 2. Map Headers To Standard Fields

Use neutral standard fields that can survive template changes:

```json
{
  "item_code": ["Item Code", "SKU", "Material Code"],
  "demand_qty": ["Required Qty", "Order Qty", "Request Qty"],
  "source_date": ["Due Date", "Required Date", "Plan Date"]
}
```

Header matching ignores common casing, spaces, underscores, hyphens, slashes,
dots, and parenthesized units.

## 3. Define Metrics

Metrics should be small, auditable, and easy to explain:

```json
{
  "key": "maintenance_demand_qty",
  "label": "Maintenance Demand",
  "type": "sum",
  "source_type": "maintenance_demand",
  "field": "demand_qty",
  "unit": "units"
}
```

## 4. Run With Explicit Config

```powershell
python -m factory_excel_ops.cli run `
  --input demo_input `
  --output output `
  --file-types config\maintenance_file_types.json `
  --field-mapping config\maintenance_field_mapping.json `
  --metrics config\maintenance_metrics.json
```

## 5. Review Output

Check:

- `summary.json` source counts.
- `summary.json` warnings.
- Dashboard cards.
- `analysis_context.json` signals.
- Test fixtures that reproduce the adapter rules.

## Adapter Review Checklist

- Source type names are generic.
- No real customer, supplier, employee, order, or workbook names are committed.
- Sample data is synthetic.
- Metrics have clear source fields and units.
- Unknown files produce warnings instead of being forced into a type.
- Packaging excludes private input folders and non-sample spreadsheets.

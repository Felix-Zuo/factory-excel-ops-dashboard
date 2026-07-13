# Roadmap

This roadmap keeps reusable core work separate from local adapter work.

## Now: 0.2.x Stabilization

- Keep the default profile generic and based on sample fixtures.
- Add tests for any new metric type.
- Improve source audit visibility for unknown or low-confidence files.
- Keep package safety checks strict.
- Document adapter patterns instead of committing local adapter files.

## Next: 0.3.x Profile Maturity

- Export a source audit table that shows matched headers and missing fields.
- Add optional CSV export for metric cards and source counts.
- Add a small HTML table explorer based only on normalized sample records.

## Later: 0.4.x Workflow Readiness

- Add an adapter test harness with generated fixture data.
- Support multi-sheet workbook selection rules.
- Add local-only dashboard serving for environments that block `file://` links.
- Add bounded run logs that avoid storing raw row values by default.
- Add a release checklist command that runs tests, packaging, and leak scans.

## Out Of Scope For The Reusable Core

- ERP/WMS/MES credentials.
- Company-specific workbook templates.
- Desktop binaries and bundled Python runtimes.
- Remote upload or SaaS synchronization.
- Customer, supplier, employee, order, BOM, shipment, finance, or HR data.

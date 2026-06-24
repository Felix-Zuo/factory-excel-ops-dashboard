# Public Product Evolution

This file records the sanitized product story behind the public showcase. It is
written as public documentation, not as a fabricated commit history. Private
customer data, workbook names, operator logs, and company-specific adapter rules
are intentionally excluded.

## Stage 1: Manual Spreadsheet Flow

The starting point was a common operations problem: teams had several daily
exports, inconsistent filenames, changing headers, and a dashboard that still
depended on manual copy-paste work.

Public carry-over:

- Treat spreadsheet exports as operational inputs, not as one-off files.
- Keep a clear boundary between source files, normalized records, summaries,
  and dashboards.
- Never overwrite or publish original business exports.

## Stage 2: Content-First Recognition

Filename matching was not enough. Real exports often arrive as `data.xlsx`,
`data (1).xlsx`, or renamed copies. The public project therefore classifies
files through headers, sample values, and weak filename evidence.

Public carry-over:

- `FileClassifier` scores headers, values, and filename hints.
- File signatures live in JSON config.
- Unknown files produce warnings instead of silent assumptions.

## Stage 3: Field Mapping And Source Contracts

Headers vary across systems, languages, templates, and user-edited workbooks.
The private workflow needed resilient mapping rules before any dashboard could
be trusted.

Public carry-over:

- `FieldMapper` uses configurable aliases.
- Header matching ignores common whitespace, separator, case, and unit noise.
- Standard fields stay small and adapter-friendly.
- Private adapters can extend config without changing the public package.

## Stage 4: Summary, Dashboard, And Review Loop

The useful output is not a perfect replica of every workbook. It is a compact
set of metrics, warnings, and traceable source counts that a reviewer can
review quickly.

Public carry-over:

- `summary.json` is the source of truth for dashboard and reporting context.
- The HTML dashboard is standalone and local-first.
- `analysis-context` creates a bounded payload for reporting workflows.

## Stage 5: Generalized Operations Profile

The public v0.2.0 release moves away from one product category or one factory
template. The default profile now uses generic operations source types:

- `inventory`: what is available.
- `demand`: what is requested.
- `fulfillment`: what has moved or been completed for demand.
- `replenishment`: what is planned to restore capacity or stock.
- `work_output`: what the team or process has produced.

These names work for manufacturing, maintenance parts, warehouse operations,
field service, project delivery, sample rooms, repair queues, and other
spreadsheet-heavy workflows.

## What Is Deliberately Not Public

- Real ERP/WMS/MES exports.
- Customer, supplier, employee, order, BOM, shipment, finance, or HR records.
- Private workbook templates and proprietary field rules.
- Desktop binaries and local runtime packages.
- Internal issue logs, operator names, or deployment records.

## Maintenance Model

The public repository is maintained like a small product:

- Changelog entries explain user-facing changes.
- Issue templates collect reproducible bugs and adapter requests.
- The roadmap separates core engine work from private adapter work.
- Packaging scripts are tested so ignored private files do not leak.

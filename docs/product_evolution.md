# Product Evolution

This file records the product decisions behind the reusable spreadsheet
operations workbench. It focuses on stable behavior, boundaries, and extension
points rather than customer-specific workbook history.

## Stage 1: Manual Spreadsheet Flow

The starting point is a common operations problem: teams have several daily
exports, inconsistent filenames, changing headers, and dashboards that still
depend on manual copy-paste work.

Design decisions:

- Treat spreadsheet exports as operational inputs, not one-off files.
- Keep a clear boundary between source files, normalized records, summaries,
  and dashboards.
- Never overwrite or publish original business exports.

## Stage 2: Content-First Recognition

Filename matching is not enough. Exports often arrive as `data.xlsx`,
`data (1).xlsx`, or renamed copies. The workbench classifies files through
headers, sample values, and weak filename evidence.

Design decisions:

- `FileClassifier` scores headers, values, and filename hints.
- File signatures live in JSON config.
- Unknown files produce warnings instead of silent assumptions.

## Stage 3: Field Mapping And Source Contracts

Headers vary across systems, languages, templates, and user-edited workbooks.
The workflow needs resilient mapping rules before any dashboard can be trusted.

Design decisions:

- `FieldMapper` uses configurable aliases.
- Header matching ignores common whitespace, separator, case, and unit noise.
- Standard fields stay small and adapter-friendly.
- Local adapters can extend config without changing the reusable package.

## Stage 4: Summary, Dashboard, And Review Loop

The useful output is not a perfect replica of every workbook. It is a compact
set of metrics, warnings, and traceable source counts that a reviewer can check
quickly.

Design decisions:

- `summary.json` is the source of truth for dashboard and reporting context.
- The HTML dashboard is standalone and local-first.
- `analysis-context` creates a bounded payload for reporting workflows.

## Stage 5: Generalized Operations Profile

The v0.2.0 profile moved away from one product category or one fixed workbook
template. The default profile now uses generic operations source types:

- `inventory`: what is available.
- `demand`: what is requested.
- `fulfillment`: what has moved or been completed for demand.
- `replenishment`: what is planned to restore capacity or stock.
- `work_output`: what the team or process has produced.

These names work for manufacturing, maintenance parts, warehouse operations,
field service, project delivery, sample rooms, repair queues, and other
spreadsheet-heavy workflows.

## Data Boundary

- Real ERP/WMS/MES exports.
- Customer, supplier, employee, order, BOM, shipment, finance, or HR records.
- Workbook templates and proprietary field rules.
- Desktop binaries and local runtime packages.
- Internal issue logs, operator names, or deployment records.

## Maintenance Model

The repository is maintained like a small product:

- Changelog entries explain user-facing changes.
- Issue templates collect reproducible bugs and adapter requests.
- The roadmap separates core engine work from local adapter work.
- Packaging scripts are tested so ignored source files do not leak.

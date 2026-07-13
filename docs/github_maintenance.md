# GitHub Maintenance

This repository uses GitHub as a lightweight product surface. The goal is to
make the project easy to evaluate from the outside and easy to maintain later.

## Labels

Recommended labels:

| Label | Use |
| --- | --- |
| `bug` | Reproducible broken behavior. |
| `ci` | GitHub Actions, packaging checks, or release validation. |
| `dependencies` | Dependency updates from Dependabot. |
| `documentation` | README, docs, examples, or product copy. |
| `enhancement` | User-facing improvement. |
| `maintenance` | Internal cleanup or quality work. |
| `profile` | Source, field, or metric profile changes. |
| `security` | Data safety, packaging safety, or local file exposure risk. |

## Milestones

Use milestones to group work into product-ready themes:

- `v0.2.x Stabilization`: polish current default profile, CI, validation, and
  data safety.
- `v0.3 Profile Maturity`: source audit, profile validator expansion, and
  richer metrics.
- `v0.4 Workflow Readiness`: adapter test harness, local dashboard serving, and
  release automation.

## Issue Style

Good issues are small and outcome-focused:

- "Add source audit table to summary output"
- "Warn when two source signatures tie"
- "Add CSV export for metric cards"

Avoid issues that require sensitive source data:

- real workbook names
- real customer or supplier examples
- screenshots with sensitive rows
- deployment paths from a local machine

## Release Hygiene

Before closing a milestone:

1. Run the quality gates.
2. Confirm docs describe the current behavior.
3. Confirm package safety checks still pass.
4. Update `CHANGELOG.md`.
5. Keep GitHub topics and description aligned with the current scope.

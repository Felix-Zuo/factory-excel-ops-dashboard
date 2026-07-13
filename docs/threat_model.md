# Threat Model

The project is local-first and processes spreadsheet files supplied by the user.
The main security goal is to avoid leaking sensitive data and to avoid presenting
untrusted spreadsheet content as executable or trusted UI content.

## Assets

- Local spreadsheet exports.
- Generated summaries and dashboards.
- Local adapter configs.
- Packaged handoff archives.
- GitHub repository history.

## Trust Boundaries

| Boundary | Risk | Current control |
| --- | --- | --- |
| Input folder to parser | Unexpected, malformed, or oversized files | Supported suffix allowlist, explicit unsupported-file errors, and default 25 MB per-file limit. |
| Spreadsheet headers to config | Misclassification or wrong metrics | Config validation, normalized header matching, and classification confidence threshold. |
| Parsed values to HTML | HTML/script injection | Dashboard output escapes labels, values, source types, warnings, and JSON payloads. |
| Local repo to package zip | Sensitive data leakage | Package helper excludes local input folders, generated outputs, egg-info, archives, executables, Excel files, and non-sample CSV files. |
| GitHub issues and PRs | Accidental sensitive details | Issue and PR templates require sample or anonymized data. |

## Non-Goals

- The reusable core does not authenticate users.
- The reusable core does not upload files.
- The reusable core does not execute workbook macros.
- The reusable core does not store credentials.

## Security Checks

Before pushing:

```powershell
python -m pytest -q
python -m factory_excel_ops.cli validate-config
python scripts\package_project.py --name security-check --output output
rg -n "password|secret|token|internal_brand" --glob "!**/.git/**" --glob "!output/**"
```

## Residual Risks

- Extremely large allowed files can still consume local CPU or memory if the
  caller disables `--max-file-mb` or sets it too high.
- A local adapter can weaken safety if it commits real identifiers or broad
  filename rules.
- Downstream tools that read `summary.json` must apply their own access controls.

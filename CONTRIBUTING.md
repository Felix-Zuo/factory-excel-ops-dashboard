# Contributing

Contributions are welcome when they keep the project generic, local-first, and
safe for public use.

## Rules

- Do not commit real company exports.
- Do not commit customer, supplier, order, BOM, shipment, or production data.
- Add synthetic fixtures for tests.
- Keep private adapters outside this public repository.
- Add a regression test when changing classification or field mapping behavior.

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m unittest discover -s tests
```

# Contributing

Contributions are welcome when they keep the project generic, local-first, and
safe to share.

## Rules

- Do not commit real company exports.
- Do not commit customer, supplier, employee, order, BOM, shipment, finance,
  HR, production, procurement, or service data.
- Add sample fixtures for tests.
- Keep local adapters and sensitive source rules outside this repository.
- Add a regression test when changing classification or field mapping behavior.

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m unittest discover -s tests
```

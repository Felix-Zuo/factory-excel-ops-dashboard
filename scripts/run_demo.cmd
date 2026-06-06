@echo off
setlocal
cd /d "%~dp0\.."
set PYTHONPATH=%CD%\src
python -m factory_excel_ops.cli run --input sample_data --output output
echo.
echo Dashboard written to output\dashboard.html
pause

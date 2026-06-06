@echo off
setlocal
cd /d "%~dp0\.."
python scripts\package_project.py --name factory-excel-ops-dashboard --output output
echo.
echo Package written to output
pause

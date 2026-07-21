@echo off
REM Start the portfolio local development server (Python stdlib, no Node/npm).
cd /d "%~dp0"
python -u dev_server.py %*

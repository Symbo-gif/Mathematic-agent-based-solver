@echo off
title Symbo Math CLI

REM Enable ANSI color support in Windows 10+ (required for gold/teal colors)
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

REM Set UTF-8 code page for Unicode support
chcp 65001 >nul 2>&1

REM Force enable colors via environment variable
set FORCE_COLOR=1
set PYTHONIOENCODING=utf-8

cd /d "%~dp0"

REM Ensure colorama is installed
python -c "import colorama" 2>nul || (
    echo Installing colorama for terminal colors...
    pip install colorama -q
)

REM Start the CLI
python -m symbo_agentic_reasoners.cli

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start CLI. Make sure Python and dependencies are installed.
    echo Run: pip install -r requirements.txt
    pause
)

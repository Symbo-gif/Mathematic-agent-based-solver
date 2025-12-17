@echo off
title SYMBO Math Solver

REM Enable ANSI color support in Windows 10+
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

REM Set UTF-8 code page for Unicode support
chcp 65001 >nul 2>&1

REM Force enable colors via environment variable
set FORCE_COLOR=1
set PYTHONIOENCODING=utf-8

echo.
echo +============================================================+
echo ^|           SYMBO MATH SOLVER - Starting UI...              ^|
echo +============================================================+
echo.

cd /d "%~dp0"
python scripts/math_solver_ui.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start. Make sure Python is installed.
    pause
)

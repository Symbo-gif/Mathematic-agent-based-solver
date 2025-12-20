@echo off
title SYMBO Math Solver
echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║           SYMBO MATH SOLVER - Starting UI...              ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"
python scripts/math_solver_ui.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start. Make sure Python is installed.
    pause
)

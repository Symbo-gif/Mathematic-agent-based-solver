@echo off
title Symbo Math - Native Solver Mode

REM Enable ANSI color support in Windows 10+
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

REM Set UTF-8 code page
chcp 65001 >nul 2>&1

REM Environment settings
set SYMPY_DISABLED=1
set FORCE_COLOR=1
set PYTHONIOENCODING=utf-8

REM Set default console colors (black background, gold text)
color 06

cd /d "%~dp0"

REM Print colored banner using Python
python -c "from symbo_agentic_reasoners.utils.terminal_colors import gold, teal, green, red; print(); print(gold('+' + '='*60 + '+')); print(gold('|') + teal('      SYMBO MATH') + gold(' - Native Solver Mode                  |')); print(gold('+' + '='*60 + '+')); print(); print(teal('SYMPY_DISABLED=1')); print(gold('SymPy fallbacks are BLOCKED. Only native domain solvers run.')); print(red('If a problem cannot be solved natively, an exception is raised.')); print(); print(gold('+' + '='*60 + '+'))"

REM Launch GUI in background, keep terminal open
start "Symbo Math GUI" python scripts/math_solver_ui.py

echo.
python -c "from symbo_agentic_reasoners.utils.terminal_colors import green, teal; print(green('[OK]') + teal(' GUI launched in separate window')); print(teal('This terminal stays open for debugging/monitoring')); print()"

REM Keep terminal open for interaction
cmd /k "python -c \"from symbo_agentic_reasoners.utils.terminal_colors import gold, teal; print(gold('Terminal ready.') + teal(' Type Python commands or close when done.'))\""

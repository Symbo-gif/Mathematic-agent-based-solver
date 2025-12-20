@echo off
REM Start SYMBO with SYMPY_DISABLED mode - native solvers only, no SymPy fallbacks
REM Any attempt to fall back to SymPy will raise SympyDisabledException

set SYMPY_DISABLED=1
set PYTHONIOENCODING=utf-8

echo ============================================================
echo SYMBO - Native Solver Mode (SYMPY_DISABLED=1)
echo ============================================================
echo SymPy fallbacks are BLOCKED. Only native domain solvers run.
echo If a problem cannot be solved natively, an exception is raised.
echo ============================================================
echo.

cd /d "%~dp0"
python scripts/math_solver_ui.py %*

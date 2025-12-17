@echo off
title Claude Code - Symbo Math

REM Enable ANSI color support in Windows 10+
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

REM Set UTF-8 code page
chcp 65001 >nul 2>&1

REM Environment settings
set FORCE_COLOR=1
set PYTHONIOENCODING=utf-8

REM Set default console colors (black background, gold text)
color 06

cd /d "c:\dev\Mathematic agent based solver"

REM Print colored banner using Python (guaranteed to work)
python -c "from symbo_agentic_reasoners.utils.terminal_colors import gold, teal, green, red, C; print(); print(gold('+' + '='*60 + '+')); print(gold('|') + teal('      CLAUDE CODE') + gold(' - Symbo Math Project              |')); print(gold('+' + '='*60 + '+')); print(); print(teal('Color Theme: ') + gold('Gold') + teal(' / ') + C.TEAL + 'Teal' + C.RESET + teal(' / ') + green('Green') + teal(' / ') + red('Blood Red')); print()"

REM Start Claude Code
"C:\Users\there\.local\bin\claude.exe"

pause

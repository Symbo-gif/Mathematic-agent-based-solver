@echo off
REM Claude Code Symbo Math UI Launcher
REM Launches the desktop UI for Claude Code

cd /d "c:\dev\Mathematic agent based solver"

REM Set title
title Claude Code Symbo Math UI

REM Launch the UI (use pythonw for no console window)
start "" pythonw "claude-code-launcher\claude_code_ui.py"

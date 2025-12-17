@echo off
REM Claude Code Symbo Math Launcher
REM Launches Claude Code with project context pre-loaded

cd /d "c:\dev\Mathematic agent based solver"

REM Set title and colors for Windows command prompt
title Claude Code - Symbo Math
color 06

REM Clear screen with styled header
cls
echo.
echo  ========================================================
echo   SYMBO MATH - Claude Code Session
echo   Multi-Agent Mathematical Discovery Engine
echo  ========================================================
echo.
echo  Project: c:\dev\Mathematic agent based solver
echo  Version: 0.6.0
echo.
echo  Tip: Ask Claude to read claude-code-launcher/PROJECT_CONTEXT.md
echo       for full context about recent changes and next steps.
echo.
echo  Starting Claude Code...
echo.

REM Launch Claude Code in the project directory
REM The .claude/CLAUDE.md file provides automatic context
REM For additional context, ask Claude to read PROJECT_CONTEXT.md
claude

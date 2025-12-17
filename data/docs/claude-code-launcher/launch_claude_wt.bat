@echo off
REM Claude Code Symbo Math Launcher - Windows Terminal Version
REM Launches Claude Code in Windows Terminal with custom color scheme

cd /d "c:\dev\Mathematic agent based solver"

REM Check if Windows Terminal is available
where wt >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Windows Terminal not found. Falling back to CMD...
    call claude-code-launcher\launch_claude_symbo.bat
    exit /b
)

REM Launch in Windows Terminal with custom title
wt -w 0 new-tab --title "Claude Code Symbo Math" -d "c:\dev\Mathematic agent based solver" cmd /k "claude-code-launcher\launch_claude_symbo.bat"

# PowerShell script to create desktop shortcut for Claude Code Symbo Math UI
# Run this script once to create the shortcut

$WshShell = New-Object -ComObject WScript.Shell

# Get desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Claude Code Symbo Math UI.lnk"

# Create shortcut
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

# Configure shortcut - use pythonw to avoid console window
$Shortcut.TargetPath = "pythonw.exe"
$Shortcut.Arguments = '"c:\dev\Mathematic agent based solver\claude-code-launcher\claude_code_ui.py"'
$Shortcut.WorkingDirectory = "c:\dev\Mathematic agent based solver"
$Shortcut.IconLocation = "c:\dev\Mathematic agent based solver\claude-code-launcher\symbo_math_icon.ico,0"
$Shortcut.Description = "Launch Claude Code Symbo Math Desktop UI"
$Shortcut.WindowStyle = 1  # Normal window

# Save shortcut
$Shortcut.Save()

Write-Host "Desktop shortcut created: $ShortcutPath" -ForegroundColor Green
Write-Host ""
Write-Host "Shortcut Details:" -ForegroundColor Cyan
Write-Host "  Name: Claude Code Symbo Math UI"
Write-Host "  Icon: symbo_math_icon.ico"
Write-Host "  Target: claude_code_ui.py"
Write-Host ""
Write-Host "Double-click the shortcut to launch the desktop UI!" -ForegroundColor Yellow

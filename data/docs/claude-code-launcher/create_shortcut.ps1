# PowerShell script to create desktop shortcut for Claude Code Symbo Math
# Run this script once to create the shortcut

$WshShell = New-Object -ComObject WScript.Shell

# Get desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Claude Code Symbo Math.lnk"

# Create shortcut
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

# Configure shortcut
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = '/k "cd /d c:\dev\Mathematic agent based solver && claude-code-launcher\launch_claude_symbo.bat"'
$Shortcut.WorkingDirectory = "c:\dev\Mathematic agent based solver"
$Shortcut.IconLocation = "c:\dev\Mathematic agent based solver\claude-code-launcher\symbo_math_icon.ico,0"
$Shortcut.Description = "Launch Claude Code with Symbo Math project context"
$Shortcut.WindowStyle = 1  # Normal window

# Save shortcut
$Shortcut.Save()

Write-Host "Desktop shortcut created: $ShortcutPath" -ForegroundColor Green
Write-Host ""
Write-Host "Shortcut Details:" -ForegroundColor Cyan
Write-Host "  Name: Claude Code Symbo Math"
Write-Host "  Icon: symbo_math_icon.ico"
Write-Host "  Target: launch_claude_symbo.bat"
Write-Host ""
Write-Host "To use the custom terminal color scheme:" -ForegroundColor Yellow
Write-Host "  1. Open Windows Terminal Settings (Ctrl+,)"
Write-Host "  2. Click 'Open JSON file' at bottom left"
Write-Host "  3. Add the color scheme from symbo_math_terminal_scheme.json to the 'schemes' array"
Write-Host "  4. Optionally add the profile from symbo_math_terminal_profile.json to 'profiles.list'"

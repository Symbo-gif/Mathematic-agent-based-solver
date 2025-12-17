$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\OneDrive\Desktop\Symbo Math.lnk")
$Shortcut.TargetPath = "C:\dev\Mathematic agent based solver\start_no_sympy.bat"
$Shortcut.IconLocation = "C:\dev\Mathematic agent based solver\Symbo Math Logo.ico,0"
$Shortcut.WorkingDirectory = "C:\dev\Mathematic agent based solver"
$Shortcut.Save()
Write-Host "Shortcut created: Symbo Math.lnk with custom lion icon"

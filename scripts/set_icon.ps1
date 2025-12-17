$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("C:\Users\there\OneDrive\Desktop\Claude Code Symbo Math UI.lnk")
$shortcut.IconLocation = "c:\dev\Mathematic agent based solver\claude_code_teal.ico,0"
$shortcut.Save()
Write-Host "Icon applied successfully!"

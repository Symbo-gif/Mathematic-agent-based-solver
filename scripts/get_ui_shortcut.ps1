$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("C:\Users\there\OneDrive\Desktop\Claude Code Symbo Math UI.lnk")
Write-Host "TargetPath:" $shortcut.TargetPath
Write-Host "Arguments:" $shortcut.Arguments
Write-Host "WorkingDirectory:" $shortcut.WorkingDirectory
Write-Host "IconLocation:" $shortcut.IconLocation

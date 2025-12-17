$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("C:\Users\there\OneDrive\Desktop\Start Claude Code.lnk")
Write-Host "IconLocation:" $shortcut.IconLocation
Write-Host "TargetPath:" $shortcut.TargetPath

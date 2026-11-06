$wsh = New-Object -ComObject WScript.Shell

$startupFolder = [Environment]::GetFolderPath('Startup')
$startupShortcut = $wsh.CreateShortcut("$startupFolder\PCController.lnk")
$startupShortcut.TargetPath = 'wscript.exe'
$startupShortcut.Arguments = '"E:\personal AI\PCController\run_silent.vbs"'
$startupShortcut.WorkingDirectory = 'E:\personal AI\PCController'
$startupShortcut.Description = 'Personal AI PC Controller Auto-Start'
$startupShortcut.Save()
Write-Host "Startup shortcut created successfully."

$desktop = [Environment]::GetFolderPath('Desktop')
$desktopStart = $wsh.CreateShortcut("$desktop\Start PC Controller.lnk")
$desktopStart.TargetPath = 'wscript.exe'
$desktopStart.Arguments = '"E:\personal AI\PCController\run_silent.vbs"'
$desktopStart.WorkingDirectory = 'E:\personal AI\PCController'
$desktopStart.Description = 'Start Personal AI PC Controller in background'
$desktopStart.Save()
Write-Host "Desktop Start shortcut created successfully."

$desktopStop = $wsh.CreateShortcut("$desktop\Stop PC Controller.lnk")
$desktopStop.TargetPath = 'E:\personal AI\PCController\stop_controller.bat'
$desktopStop.WorkingDirectory = 'E:\personal AI\PCController'
$desktopStop.Description = 'Stop Personal AI PC Controller'
$desktopStop.Save()
Write-Host "Desktop Stop shortcut created successfully."


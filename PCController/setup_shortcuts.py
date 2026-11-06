import os
import win32com.client if False else None

# PowerShell script to create shortcuts safely without escaping bugs
ps_script = r"""
$wsh = New-Object -ComObject WScript.Shell

# 1. Windows Startup Shortcut (Runs silently when PC boots)
$startupFolder = [Environment]::GetFolderPath('Startup')
$startupShortcut = $wsh.CreateShortcut("$startupFolder\PCController.lnk")
$startupShortcut.TargetPath = 'wscript.exe'
$startupShortcut.Arguments = '""" + r'"E:\personal AI\PCController\run_silent.vbs"' + r"""'
$startupShortcut.WorkingDirectory = 'E:\personal AI\PCController'
$startupShortcut.Description = 'Personal AI PC Controller Auto-Start'
$startupShortcut.Save()
Write-Host "Startup shortcut created successfully."

# 2. Desktop Start Shortcut
$desktop = [Environment]::GetFolderPath('Desktop')
$desktopStart = $wsh.CreateShortcut("$desktop\Start PC Controller.lnk")
$desktopStart.TargetPath = 'wscript.exe'
$desktopStart.Arguments = '""" + r'"E:\personal AI\PCController\run_silent.vbs"' + r"""'
$desktopStart.WorkingDirectory = 'E:\personal AI\PCController'
$desktopStart.Description = 'Start Personal AI PC Controller in background'
$desktopStart.Save()
Write-Host "Desktop Start shortcut created successfully."

# 3. Desktop Stop Shortcut
$desktopStop = $wsh.CreateShortcut("$desktop\Stop PC Controller.lnk")
$desktopStop.TargetPath = 'E:\personal AI\PCController\stop_controller.bat'
$desktopStop.WorkingDirectory = 'E:\personal AI\PCController'
$desktopStop.Description = 'Stop Personal AI PC Controller'
$desktopStop.Save()
Write-Host "Desktop Stop shortcut created successfully."
"""

with open("e:\\personal AI\\PCController\\create_shortcuts.ps1", "w", encoding="utf-8") as f:
    f.write(ps_script)

print("PowerShell script written.")


Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "E:\personal AI\PCController"
WshShell.Run """E:\personal AI\PCController\.venv\Scripts\python.exe"" ""E:\personal AI\PCController\main.py""", 0, False

Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "E:\personal AI\PCController"
Dim ret
ret = WshShell.Run("""E:\personal AI\PCController\.venv\Scripts\python.exe"" ""E:\personal AI\PCController\main.py""", 0, True)
WScript.Echo "Exit code: " & ret


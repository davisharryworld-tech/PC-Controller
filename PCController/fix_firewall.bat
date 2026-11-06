@echo off
echo ============================================
echo   Adding Firewall Rule for PC Controller
echo ============================================
netsh advfirewall firewall add rule name="PC Controller Server" dir=in action=allow protocol=TCP localport=8000,8443 profile=private,public
echo.
echo DONE! Ab doosre mobile se bhi connect ho jayega.
echo.
pause


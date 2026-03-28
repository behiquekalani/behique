@echo off
REM ============================================================
REM  Behike Web Server Deployment for Naboria (Windows)
REM  Serves: Storefront, BIOS Dashboard, VR War Room, PR Dashboard
REM  Port: 8080 (0.0.0.0)
REM ============================================================

echo ============================================================
echo  BEHIKE WEB SERVER - NABORIA DEPLOYMENT
echo ============================================================
echo.

REM --- Create directory structure ---
echo [1/6] Creating directories...
if not exist "C:\behique\webserver" mkdir "C:\behique\webserver"
if not exist "C:\behique\logs" mkdir "C:\behique\logs"
if not exist "C:\behique\storefront" mkdir "C:\behique\storefront"
if not exist "C:\behique\bios\dashboard" mkdir "C:\behique\bios\dashboard"
echo       Done.
echo.

REM --- Install Python dependencies ---
echo [2/6] Installing Python dependencies...
pip install fastapi uvicorn --quiet 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo       WARNING: pip install failed. Trying with py -m pip...
    py -m pip install fastapi uvicorn --quiet 2>nul
)
echo       Done.
echo.

REM --- Copy server file ---
echo [3/6] Deploying server...
copy /Y "%~dp0webserver.py" "C:\behique\webserver\webserver.py" >nul
echo       Copied webserver.py to C:\behique\webserver\
echo.

REM --- Create the restart wrapper ---
echo [4/6] Creating auto-restart wrapper...
(
echo @echo off
echo :loop
echo echo [%%date%% %%time%%] Starting Behike Web Server... ^>^> "C:\behique\logs\webserver_restarts.log"
echo cd /d "C:\behique\webserver"
echo py webserver.py
echo echo [%%date%% %%time%%] Server crashed. Restarting in 5 seconds... ^>^> "C:\behique\logs\webserver_restarts.log"
echo timeout /t 5 /nobreak ^>nul
echo goto loop
) > "C:\behique\webserver\run_server.bat"
echo       Created C:\behique\webserver\run_server.bat
echo.

REM --- Create startup shortcut via scheduled task ---
echo [5/6] Creating startup task...
schtasks /query /tn "BehikeWebServer" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo       Removing old task...
    schtasks /delete /tn "BehikeWebServer" /f >nul 2>&1
)
schtasks /create /tn "BehikeWebServer" /tr "C:\behique\webserver\run_server.bat" /sc onlogon /rl highest /f >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo       Scheduled task created: BehikeWebServer (runs on logon)
) else (
    echo       WARNING: Could not create scheduled task.
    echo       You can manually add C:\behique\webserver\run_server.bat to startup.
    REM Fallback: copy to startup folder
    copy /Y "C:\behique\webserver\run_server.bat" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\behike_webserver.bat" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo       Fallback: Copied to Startup folder instead.
    )
)
echo.

REM --- Start the server now ---
echo [6/6] Starting server...
echo.
echo ============================================================
echo  Server starting on http://0.0.0.0:8080
echo.
echo  Routes:
echo    /           - Storefront (home)
echo    /store/     - Storefront
echo    /bios/      - BIOS Dashboard
echo    /vr/        - VR War Room
echo    /pr/        - PR Dashboard
echo    /health     - Health Check
echo.
echo  Logs: C:\behique\logs\webserver.log
echo  To stop: Ctrl+C or close this window
echo ============================================================
echo.

cd /d "C:\behique\webserver"
py webserver.py

REM If we get here, server exited
echo.
echo Server stopped. Press any key to restart...
pause >nul
goto :eof

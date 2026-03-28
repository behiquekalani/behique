@echo off
:: ============================================================
:: status.bat - Check Behike tunnel status
:: ============================================================

echo.
echo ============================================================
echo   Behike Tunnel Status
echo ============================================================
echo.

:: Check if cloudflared is installed
where cloudflared >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] cloudflared is not installed.
    echo         Run install_cloudflared.bat first.
    pause
    exit /b 1
)

:: Version
echo --- cloudflared version ---
cloudflared --version
echo.

:: Windows service status
echo --- Service Status ---
sc query cloudflared >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3,4" %%a in ('sc query cloudflared ^| findstr "STATE"') do (
        set "STATE=%%a %%b"
    )
    sc query cloudflared | findstr "STATE"
) else (
    echo Service not installed. Using manual mode or not set up yet.
)
echo.

:: Check if process is running
echo --- Process Status ---
tasklist /fi "imagename eq cloudflared.exe" 2>nul | findstr /i "cloudflared" >nul
if %errorlevel% equ 0 (
    echo cloudflared is RUNNING
    tasklist /fi "imagename eq cloudflared.exe" /fo table
) else (
    echo cloudflared is NOT RUNNING
)
echo.

:: List tunnels
echo --- Registered Tunnels ---
cloudflared tunnel list 2>nul
if %errorlevel% neq 0 (
    echo Could not list tunnels. May need to run: cloudflared tunnel login
)
echo.

:: Check config
echo --- Configuration ---
set "CF_DIR=C:\behique\cloudflare"
if exist "%CF_DIR%\config.yml" (
    echo Config found: %CF_DIR%\config.yml
    echo.
    echo Contents:
    echo --------
    type "%CF_DIR%\config.yml"
) else if exist "%USERPROFILE%\.cloudflared\config.yml" (
    echo Config found: %USERPROFILE%\.cloudflared\config.yml
) else (
    echo No config.yml found. Run setup_tunnel.bat.
)
echo.

:: Check metrics endpoint
echo --- Metrics ---
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:2000/ready' -TimeoutSec 2 -UseBasicParsing; Write-Host 'Tunnel health endpoint: OK (HTTP' $r.StatusCode')' } catch { Write-Host 'Tunnel health endpoint: NOT RESPONDING (tunnel may be down)' }"
echo.

echo ============================================================
echo   Dashboard: https://one.dash.cloudflare.com
echo ============================================================
echo.
pause

@echo off
:: ============================================================
:: stop_tunnel.bat - Stop the Behike tunnel
:: ============================================================

echo.
echo [*] Stopping Behike tunnel...
echo.

:: Check for admin privileges (needed for service control)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Not running as Administrator.
    echo        Service commands may fail. Run as admin if needed.
    echo.
)

:: Try stopping the Windows service
sc query cloudflared >nul 2>&1
if %errorlevel% equ 0 (
    echo [*] Stopping cloudflared service...
    net stop cloudflared 2>nul
    if %errorlevel% equ 0 (
        echo [OK] Tunnel service stopped.
    ) else (
        echo [INFO] Service may not be running.
    )
) else (
    echo [INFO] No cloudflared service found.
)

:: Kill any manual cloudflared processes
tasklist /fi "imagename eq cloudflared.exe" 2>nul | findstr /i "cloudflared" >nul
if %errorlevel% equ 0 (
    echo [*] Killing cloudflared processes...
    taskkill /f /im cloudflared.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] cloudflared processes terminated.
    ) else (
        echo [WARN] Could not kill cloudflared. May need admin privileges.
    )
) else (
    echo [INFO] No cloudflared processes running.
)

echo.
echo [OK] Tunnel stopped.
pause

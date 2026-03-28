@echo off
:: ============================================================
:: start_tunnel.bat - Start the Behike tunnel manually
:: Use this if the Windows service isn't running
:: ============================================================

echo.
echo [*] Starting Behike tunnel...
echo.

:: Try starting the Windows service first
sc query cloudflared >nul 2>&1
if %errorlevel% equ 0 (
    echo [*] Windows service found. Starting via service...
    net start cloudflared 2>nul
    if %errorlevel% equ 0 (
        echo [OK] Tunnel service started.
        echo     Check status with: status.bat
        pause
        exit /b 0
    )
    if %errorlevel% equ 2 (
        echo [OK] Tunnel service is already running.
        pause
        exit /b 0
    )
    echo [WARN] Service start failed. Falling back to manual run...
    echo.
)

:: Manual run - check for config in both locations
set "CF_DIR=C:\behique\cloudflare"
set "CF_HOME=%USERPROFILE%\.cloudflared"

if exist "%CF_DIR%\config.yml" (
    set "CONFIG=%CF_DIR%\config.yml"
) else if exist "%CF_HOME%\config.yml" (
    set "CONFIG=%CF_HOME%\config.yml"
) else (
    echo [ERROR] No config.yml found.
    echo         Expected at: %CF_DIR%\config.yml
    echo         Run setup_tunnel.bat first.
    pause
    exit /b 1
)

echo [*] Using config: %CONFIG%
echo [*] Tunnel will run in this window. Close window or Ctrl+C to stop.
echo.
echo ============================================================

cloudflared tunnel --config "%CONFIG%" run behike

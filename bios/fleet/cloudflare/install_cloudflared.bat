@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: install_cloudflared.bat - Cloudflare Tunnel installer for Naboria (Windows)
:: Downloads and installs cloudflared, creates config directory
:: ============================================================

echo.
echo ============================================================
echo   Cloudflare Tunnel Installer - Naboria
echo ============================================================
echo.

:: Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] This script must be run as Administrator.
    echo         Right-click CMD and select "Run as administrator"
    pause
    exit /b 1
)

:: Create behique cloudflare config directory
set "CF_DIR=C:\behique\cloudflare"
if not exist "%CF_DIR%" (
    echo [*] Creating config directory: %CF_DIR%
    mkdir "%CF_DIR%"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create directory %CF_DIR%
        pause
        exit /b 1
    )
    echo [OK] Directory created.
) else (
    echo [OK] Config directory already exists: %CF_DIR%
)

:: Check if cloudflared is already installed
where cloudflared >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] cloudflared is already installed.
    cloudflared --version
    echo.
    echo Run setup_tunnel.bat next to configure the tunnel.
    pause
    exit /b 0
)

:: Download cloudflared
set "DOWNLOAD_URL=https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.msi"
set "INSTALLER=%TEMP%\cloudflared.msi"

echo [*] Downloading cloudflared from GitHub...
echo     URL: %DOWNLOAD_URL%
echo.

powershell -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%INSTALLER%' -UseBasicParsing; Write-Host '[OK] Download complete.' } catch { Write-Host '[ERROR] Download failed:' $_.Exception.Message; exit 1 }"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to download cloudflared.
    echo         Check your internet connection and try again.
    pause
    exit /b 1
)

:: Install cloudflared
echo [*] Installing cloudflared...
msiexec /i "%INSTALLER%" /quiet /norestart
if %errorlevel% neq 0 (
    echo [ERROR] Installation failed. Trying interactive install...
    msiexec /i "%INSTALLER%"
)

:: Wait a moment for PATH to update
timeout /t 3 /nobreak >nul

:: Verify installation
where cloudflared >nul 2>&1
if %errorlevel% neq 0 (
    :: Try common install path
    if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" (
        echo [*] Adding cloudflared to PATH...
        setx PATH "%PATH%;C:\Program Files (x86)\cloudflared" /M
        echo [OK] Added to PATH. You may need to restart your terminal.
    ) else if exist "C:\Program Files\cloudflared\cloudflared.exe" (
        echo [*] Adding cloudflared to PATH...
        setx PATH "%PATH%;C:\Program Files\cloudflared" /M
        echo [OK] Added to PATH. You may need to restart your terminal.
    ) else (
        echo [WARN] cloudflared installed but not found in PATH.
        echo        Restart your terminal and run: cloudflared --version
    )
) else (
    echo [OK] cloudflared installed successfully.
    cloudflared --version
)

:: Cleanup
del "%INSTALLER%" 2>nul

echo.
echo ============================================================
echo   Installation complete.
echo   Next step: run setup_tunnel.bat
echo ============================================================
echo.
pause

@echo off
setlocal enabledelayedexpansion
title Cobo Gaming Toggle
color 0A

:: Mode file path
set "MODE_FILE=C:\behique\mode.json"

:: Ensure directory exists
if not exist "C:\behique" mkdir "C:\behique"

:: Read current mode from mode.json
set "CURRENT_MODE=normal"
if exist "%MODE_FILE%" (
    for /f "tokens=2 delims=:}" %%a in ('type "%MODE_FILE%" ^| findstr /i "mode"') do (
        set "RAW=%%a"
        set "RAW=!RAW: =!"
        set "RAW=!RAW:"=!"
        set "CURRENT_MODE=!RAW!"
    )
)

:: Toggle
if /i "!CURRENT_MODE!"=="normal" (
    set "NEW_MODE=gaming"
    echo {> "%MODE_FILE%"
    echo   "mode": "gaming">> "%MODE_FILE%"
    echo }>> "%MODE_FILE%"
    color 0C
    echo.
    echo  ============================================
    echo       COBO - GAMING MODE ACTIVATED
    echo  ============================================
    echo.
    echo   Mode: GAMING
    echo   BIOS tasks: PAUSED
    echo.
    echo   Written to: %MODE_FILE%
    echo  ============================================
    echo.
) else (
    set "NEW_MODE=normal"
    echo {> "%MODE_FILE%"
    echo   "mode": "normal">> "%MODE_FILE%"
    echo }>> "%MODE_FILE%"
    color 0A
    echo.
    echo  ============================================
    echo       COBO - WORK MODE ACTIVATED
    echo  ============================================
    echo.
    echo   Mode: WORK
    echo   BIOS tasks: ACTIVE
    echo.
    echo   Written to: %MODE_FILE%
    echo  ============================================
    echo.
)

echo  Press any key to close...
pause >nul

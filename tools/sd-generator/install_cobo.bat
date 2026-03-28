@echo off
REM ============================================================
REM  Stable Diffusion WebUI (AUTOMATIC1111) Auto-Installer
REM  Target: Cobo (Windows, GTX 1080 Ti 11GB)
REM  Installs to: C:\behique\stable-diffusion\
REM ============================================================

echo.
echo ===================================================
echo   Stable Diffusion Auto-Installer for Cobo
echo   GTX 1080 Ti 11GB - SD 1.5 Base Model
echo ===================================================
echo.

set SD_DIR=C:\behique\stable-diffusion
set PYTHON_VERSION=3.10.11
set MODEL_URL=https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors
set MODEL_NAME=v1-5-pruned-emaonly.safetensors

REM --- Check for Git ---
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git is not installed. Install Git for Windows first:
    echo         https://git-scm.com/download/win
    pause
    exit /b 1
)

REM --- Check for Python 3.10 ---
echo [1/6] Checking Python 3.10...
python --version 2>nul | findstr "3.10" >nul
if %ERRORLEVEL% neq 0 (
    echo Python 3.10 not found. Downloading installer...

    curl -L -o "%TEMP%\python-3.10.11.exe" "https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"

    if not exist "%TEMP%\python-3.10.11.exe" (
        echo [ERROR] Failed to download Python. Download manually:
        echo         https://www.python.org/downloads/release/python-31011/
        pause
        exit /b 1
    )

    echo Installing Python %PYTHON_VERSION%...
    "%TEMP%\python-3.10.11.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    echo Python installed. You may need to restart this script.
    echo Close this window and run install_cobo.bat again.
    pause
    exit /b 0
) else (
    echo Python 3.10 found.
)

REM --- Create directory ---
echo [2/6] Creating directory structure...
if not exist "%SD_DIR%" mkdir "%SD_DIR%"
cd /d "%SD_DIR%"

REM --- Clone AUTOMATIC1111 ---
echo [3/6] Cloning AUTOMATIC1111 Stable Diffusion WebUI...
if exist "%SD_DIR%\stable-diffusion-webui" (
    echo WebUI already cloned. Pulling latest...
    cd /d "%SD_DIR%\stable-diffusion-webui"
    git pull
) else (
    git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
)

cd /d "%SD_DIR%\stable-diffusion-webui"

REM --- Download SD 1.5 model ---
echo [4/6] Downloading Stable Diffusion 1.5 model (~4.2GB)...
set MODEL_DIR=%SD_DIR%\stable-diffusion-webui\models\Stable-diffusion
if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"

if exist "%MODEL_DIR%\%MODEL_NAME%" (
    echo Model already downloaded.
) else (
    echo This will take a while depending on your connection...
    curl -L -o "%MODEL_DIR%\%MODEL_NAME%" "%MODEL_URL%"

    if not exist "%MODEL_DIR%\%MODEL_NAME%" (
        echo [ERROR] Model download failed. Download manually from:
        echo         %MODEL_URL%
        echo Place it in: %MODEL_DIR%
        pause
        exit /b 1
    )
    echo Model downloaded successfully.
)

REM --- Create start script ---
echo [5/6] Creating start script...
(
echo @echo off
echo echo Starting Stable Diffusion WebUI with API enabled...
echo echo.
echo echo Access WebUI at: http://localhost:7860
echo echo API docs at:     http://localhost:7860/docs
echo echo.
echo cd /d "%SD_DIR%\stable-diffusion-webui"
echo call webui.bat --api --xformers --medvram
) > "%SD_DIR%\start_sd.bat"

REM --- Create API-only start script (headless) ---
(
echo @echo off
echo echo Starting Stable Diffusion WebUI in API-only mode...
echo echo.
echo echo API available at: http://localhost:7860
echo echo API docs at:      http://localhost:7860/docs
echo echo.
echo cd /d "%SD_DIR%\stable-diffusion-webui"
echo call webui.bat --api --nowebui --xformers --medvram
) > "%SD_DIR%\start_sd_api.bat"

REM --- Done ---
echo [6/6] Installation complete!
echo.
echo ===================================================
echo   Installation Summary
echo ===================================================
echo   Location:    %SD_DIR%\stable-diffusion-webui
echo   Model:       SD 1.5 (pruned, ema-only)
echo   VRAM mode:   --medvram (safe for 11GB)
echo.
echo   To start:    Run C:\behique\stable-diffusion\start_sd.bat
echo   API-only:    Run C:\behique\stable-diffusion\start_sd_api.bat
echo   WebUI:       http://localhost:7860
echo   API docs:    http://localhost:7860/docs
echo ===================================================
echo.
pause

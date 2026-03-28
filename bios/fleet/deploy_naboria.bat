@echo off
REM ================================================================
REM  BIOS Fleet - Naboria Deploy Script
REM  Paste this on Naboria (192.168.0.152)
REM  Creates directory structure and starts always-on task loops
REM  No gaming mode - this machine runs 24/7
REM ================================================================

echo [BIOS] Setting up Naboria node...

REM Create directory structure
if not exist "C:\behique\bios\storage" mkdir "C:\behique\bios\storage"
if not exist "C:\behique\bios\logs" mkdir "C:\behique\bios\logs"
if not exist "C:\behique\bios\scripts" mkdir "C:\behique\bios\scripts"

REM Create news ingestion runner (30-min loop)
echo [BIOS] Creating news ingestion runner...
(
echo @echo off
echo :LOOP
echo echo [%%date%% %%time%%] Running news ingestion... >> "C:\behique\bios\logs\news_runner.log"
echo if exist "C:\behique\bios\scripts\news_ingestion.py" (
echo     python "C:\behique\bios\scripts\news_ingestion.py" >> "C:\behique\bios\logs\news_ingestion.log" 2>&1
echo ^) else (
echo     echo [%%date%% %%time%%] news_ingestion.py not found, skipping >> "C:\behique\bios\logs\news_runner.log"
echo ^)
echo echo [%%date%% %%time%%] News ingestion cycle done >> "C:\behique\bios\logs\news_runner.log"
echo timeout /t 1800 /nobreak > nul
echo goto LOOP
) > "C:\behique\bios\run_news.bat"

REM Create signal processing runner (1-hour loop)
echo [BIOS] Creating signal processing runner...
(
echo @echo off
echo :LOOP
echo echo [%%date%% %%time%%] Running signal processing... >> "C:\behique\bios\logs\signal_runner.log"
echo if exist "C:\behique\bios\scripts\signal_processor.py" (
echo     python "C:\behique\bios\scripts\signal_processor.py" >> "C:\behique\bios\logs\signal_processor.log" 2>&1
echo ^) else (
echo     echo [%%date%% %%time%%] signal_processor.py not found, skipping >> "C:\behique\bios\logs\signal_runner.log"
echo ^)
echo echo [%%date%% %%time%%] Signal processing cycle done >> "C:\behique\bios\logs\signal_runner.log"
echo timeout /t 3600 /nobreak > nul
echo goto LOOP
) > "C:\behique\bios\run_signals.bat"

echo.
echo ================================================================
echo  Naboria node ready. Always-on, no gaming mode.
echo.
echo  To start tasks:
echo    start "BIOS-News" "C:\behique\bios\run_news.bat"
echo    start "BIOS-Signals" "C:\behique\bios\run_signals.bat"
echo.
echo  Logs at: C:\behique\bios\logs\
echo.
echo  Place your task scripts in:
echo    C:\behique\bios\scripts\news_ingestion.py
echo    C:\behique\bios\scripts\signal_processor.py
echo ================================================================

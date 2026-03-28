@echo off
REM ================================================================
REM  BIOS Fleet - Cobo Deploy Script
REM  Paste this on Cobo (192.168.0.151)
REM  Creates directory structure and starts task loops
REM ================================================================

echo [BIOS] Setting up Cobo node...

REM Create directory structure
if not exist "C:\behique\bios\storage" mkdir "C:\behique\bios\storage"
if not exist "C:\behique\bios\logs" mkdir "C:\behique\bios\logs"
if not exist "C:\behique\bios\scripts" mkdir "C:\behique\bios\scripts"

REM Create the gaming mode check script
echo [BIOS] Creating gaming mode checker...
(
echo import json, sys, os
echo mode_file = r"C:\behique\mode.json"
echo if os.path.exists(mode_file^):
echo     try:
echo         with open(mode_file, "r"^) as f:
echo             data = json.load(f^)
echo         if data.get("mode"^) == "gaming":
echo             print("GAMING"^)
echo             sys.exit(1^)
echo     except: pass
echo print("WORK"^)
echo sys.exit(0^)
) > "C:\behique\bios\scripts\check_mode.py"

REM Create the task runner
echo [BIOS] Creating task runner...
(
echo @echo off
echo :LOOP
echo echo [%%date%% %%time%%] Checking gaming mode... >> "C:\behique\bios\logs\runner.log"
echo python "C:\behique\bios\scripts\check_mode.py" > nul 2>&1
echo if errorlevel 1 (
echo     echo [%%date%% %%time%%] Gaming mode active, skipping tasks >> "C:\behique\bios\logs\runner.log"
echo     timeout /t 1800 /nobreak > nul
echo     goto LOOP
echo ^)
echo.
echo echo [%%date%% %%time%%] Running social scraper... >> "C:\behique\bios\logs\runner.log"
echo if exist "C:\behique\bios\scripts\social_scraper.py" (
echo     python "C:\behique\bios\scripts\social_scraper.py" >> "C:\behique\bios\logs\social_scraper.log" 2>&1
echo ^)
echo.
echo echo [%%date%% %%time%%] Social scraper cycle done >> "C:\behique\bios\logs\runner.log"
echo timeout /t 1800 /nobreak > nul
echo goto LOOP
) > "C:\behique\bios\run_scraper.bat"

REM Create the blueprint generator runner (2-hour loop)
(
echo @echo off
echo :LOOP
echo echo [%%date%% %%time%%] Checking gaming mode... >> "C:\behique\bios\logs\blueprint_runner.log"
echo python "C:\behique\bios\scripts\check_mode.py" > nul 2>&1
echo if errorlevel 1 (
echo     echo [%%date%% %%time%%] Gaming mode active, skipping blueprint gen >> "C:\behique\bios\logs\blueprint_runner.log"
echo     timeout /t 7200 /nobreak > nul
echo     goto LOOP
echo ^)
echo.
echo echo [%%date%% %%time%%] Running blueprint generator... >> "C:\behique\bios\logs\blueprint_runner.log"
echo if exist "C:\behique\bios\scripts\blueprint_generator.py" (
echo     python "C:\behique\bios\scripts\blueprint_generator.py" >> "C:\behique\bios\logs\blueprint_generator.log" 2>&1
echo ^)
echo.
echo echo [%%date%% %%time%%] Blueprint cycle done >> "C:\behique\bios\logs\blueprint_runner.log"
echo timeout /t 7200 /nobreak > nul
echo goto LOOP
) > "C:\behique\bios\run_blueprint.bat"

REM Create a default mode.json if none exists
if not exist "C:\behique\mode.json" (
    echo {"mode": "work", "updated": "%date% %time%"} > "C:\behique\mode.json"
    echo [BIOS] Created default mode.json (work mode^)
)

echo.
echo ================================================================
echo  Cobo node ready.
echo.
echo  To start tasks:
echo    start "BIOS-Scraper" "C:\behique\bios\run_scraper.bat"
echo    start "BIOS-Blueprint" "C:\behique\bios\run_blueprint.bat"
echo.
echo  To switch to gaming mode:
echo    echo {"mode": "gaming"} ^> C:\behique\mode.json
echo.
echo  To switch back to work mode:
echo    echo {"mode": "work"} ^> C:\behique\mode.json
echo.
echo  Logs at: C:\behique\bios\logs\
echo ================================================================

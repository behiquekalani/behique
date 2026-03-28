@echo off
REM Start BIOS scheduler daemon on Cobo
REM Runs continuously, checking for due jobs every minute

cd C:\Users\kalan\behique
python bios\scheduler\scheduler.py --daemon

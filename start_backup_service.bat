@echo off
title Star Space Backup Service
cd /d C:\Users\User1\starspace

echo ========================================
echo   STAR SPACE BACKUP SERVICE
echo ========================================
echo.

:: Check if virtual environment exists and activate it
if exist venv\Scripts\activate (
    echo Activating virtual environment...
    call venv\Scripts\activate
)

:: Start the backup service
echo Starting backup service...
echo Backups will run every 24 hours
echo Log file: backup_service.log
echo.

:: Run in background (minimized window)
start /MIN python manage.py auto_backup_service --interval 24 --daemon

echo Service started successfully!
echo.
echo The service is running in the background.
echo To stop it, use: stop_backup_service.bat
echo.
pause
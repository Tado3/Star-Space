@echo off
title Stop Star Space Backup Service
cd /d C:\Users\User1\starspace

echo ========================================
echo   STOP STAR SPACE BACKUP SERVICE
echo ========================================
echo.

:: Find and kill the backup service process
for /f "tokens=2" %%a in ('tasklist ^| findstr python.exe ^| findstr auto_backup_service') do (
    taskkill /F /PID %%a
    echo Backup service stopped.
)

if %errorlevel% neq 0 (
    echo No backup service found running.
)

echo.
pause
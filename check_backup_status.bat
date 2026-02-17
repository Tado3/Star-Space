@echo off
title Backup Service Status
cd /d C:\Users\User1\starspace

echo ========================================
echo   BACKUP SERVICE STATUS
echo ========================================
echo.

:: Check if service is running
tasklist | findstr python.exe | findstr auto_backup_service > nul
if %errorlevel% equ 0 (
    echo ✅ Backup service is RUNNING
) else (
    echo ❌ Backup service is NOT running
)

echo.
echo Recent backups:
echo ========================================
if exist backups (
    dir /od /b backups\*.sqlite3 2>nul | findstr /v /c:" " > nul
    if %errorlevel% equ 0 (
        echo Most recent database backups:
        dir /od /tc backups\*.sqlite3 2>nul | findstr /v /c:" " | findstr /v /c:"Directory" | findstr /v /c:"Volume"
    ) else (
        echo No database backups found
    )
    
    echo.
    echo Most recent media backups:
    dir /od /tc backups\*.dump 2>nul | findstr /v /c:" " | findstr /v /c:"Directory" | findstr /v /c:"Volume"
) else (
    echo No backups directory found
)

echo.
pause
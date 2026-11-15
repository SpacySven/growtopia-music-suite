@echo off
title Growtopia Music Suite
cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel%==0 (
    python growtopia_music_suite.py
) else (
    py growtopia_music_suite.py
)
if %errorlevel% neq 0 (
    echo.
    echo Something went wrong. Did you run install.bat first?
    pause
)

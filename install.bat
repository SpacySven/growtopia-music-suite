@echo off
title Growtopia Music Suite - Installer
cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel%==0 goto usepython
where py >nul 2>&1
if %errorlevel%==0 goto usepy
goto nopython

:usepython
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
goto done

:usepy
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
goto done

:nopython
echo.
echo Python was not found on this computer.
echo Install it from https://www.python.org/downloads/
echo IMPORTANT: tick "Add python.exe to PATH" in the installer!
echo.
pause
exit /b 1

:done
echo.
echo ===============================================
echo  Done! Now double-click run.bat to start.
echo ===============================================
pause

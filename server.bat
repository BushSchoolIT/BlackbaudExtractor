@echo off
setlocal enabledelayedexpansion

set LOGDIR=C:\Users\Install\Logs
set TODAY=%DATE:~10,4%-%DATE:~4,2%-%DATE:~7,2%
set LOGFILE=%LOGDIR%\prefect-server-%TODAY%.log

if not exist "%LOGDIR%" (
    mkdir "%LOGDIR%"
)

call "C:\ProgramData\miniconda3\Scripts\activate.bat"

echo. >> "%LOGFILE%"
echo ==================================================== >> "%LOGFILE%"
echo Starting Prefect Flow at %DATE% %TIME% >> "%LOGFILE%"
echo ==================================================== >> "%LOGFILE%"

prefect server start >> "%LOGFILE%" 2>&1

exit /b %ERRORLEVEL%

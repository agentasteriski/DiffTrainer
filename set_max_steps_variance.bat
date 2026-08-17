@echo off
setlocal enabledelayedexpansion
cd %~dp0

set "CONFIG=DiffSinger\configs\variance.yaml"
set "NEW_VALUE="

if not "%~1"=="" set "NEW_VALUE=%~1"

if not defined NEW_VALUE set /p "NEW_VALUE=Enter new max_updates value: "
if not defined NEW_VALUE (
    echo No value entered. Aborting.
    pause
    exit /b 1
)

echo Editing: %CONFIG%
echo Current max_updates value:
findstr /n "max_updates" "%CONFIG%"

(for /f "usebackq delims=" %%l in ("%CONFIG%") do (
    set "LINE=%%l"
    if "!LINE:~0,11!"=="max_updates" (
        echo max_updates: %NEW_VALUE%
    ) else (
        echo %%l
    )
)) > "%CONFIG%.tmp"

move /y "%CONFIG%.tmp" "%CONFIG%" >nul

echo.
echo Updated max_updates to %NEW_VALUE% in %CONFIG%
findstr /n "max_updates" "%CONFIG%"
pause
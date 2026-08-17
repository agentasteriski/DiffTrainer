@echo off
setlocal enabledelayedexpansion
cd %~dp0

set "DICTDIR=DiffSinger\dictionaries"
if not exist "%DICTDIR%" (
    echo [ERROR] Dictionary folder not found: %DICTDIR%
    pause
    exit /b 1
)

:menu
cls
echo ============================================
echo  DiffTrainer - Phoneme List Viewer / Editor
echo ============================================
echo.
echo Available language phoneme files:
echo.

set "idx=0"
for %%f in ("%DICTDIR%\-phonemes.txt" "%DICTDIR%\*-phonemes.txt") do (
    if exist "%%f" (
        set /a idx+=1
        set "file_!idx!=%%f"
        echo   !idx!. %%~nxf
    )
)
if exist "%DICTDIR%\opencpop-extension.txt" (
    set /a idx+=1
    set "file_!idx!=%DICTDIR%\opencpop-extension.txt"
    echo   !idx!. opencpop-extension.txt
)

echo   A. Open ALL phoneme files
echo   Q. Quit
echo.
set /p "choice=Select a file to view/edit (number, A, or Q): "

if /i "%choice%"=="Q" exit /b 0
if /i "%choice%"=="A" (
    echo Opening all phoneme files in Notepad...
    for /l %%i in (1,1,!idx!) do (
        start "" notepad "!file_%%i!"
        timeout /t 1 >nul
    )
    goto menu
)

set "selected="
set "n=%choice%"
for /l %%i in (1,1,!idx!) do (
    if "%%i"=="%n%" set "selected=!file_%%i!"
)
if not defined selected (
    echo Invalid choice: %choice%
    timeout /t 2 >nul
    goto menu
)

echo Opening !selected! in Notepad...
start "" /wait notepad "!selected!"

echo.
echo Press any key to return to the menu...
pause >nul
goto menu
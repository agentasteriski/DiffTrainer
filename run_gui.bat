@echo off

rem check for python and its version for 3."10" lmao
for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set python_ver=%%i
for /f "tokens=1-3 delims=." %%a in ("%python_ver%") do (
    set maj=%%a
    set min=%%b
)
if not "%maj%"=="3" (
    echo you do not have python installed, please install 3.10
    goto end
)
if not "%min%"=="10" (
    if %min% gtr 10 (
        echo you have a version of python greater than 3.10 installed, please downgrade to python 3.10
    ) else (
        echo you have a version of python less than 3.10 installed, please upgrade to python 3.10
    )
    goto end
)

%cd%\python\python.exe check_update.py

pause

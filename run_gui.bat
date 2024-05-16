@echo off

if exist "%cd%\python" (
    set "python_exe=%cd%\python\python.exe"
) else (
    set "python_exe=python"
)

%python_exe% check_update.py

pause

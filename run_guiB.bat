@echo off

if exist "%cd%\python" (
    set "pip_exe=%cd%\python\Scripts\pip"
    set "python_exe=%cd%\python\python.exe"
) else if exist "%cd%\.env" (
    set "pip_exe=%cd%\.env\Scripts\pip"
    set "python_exe=%cd%\.env\Scripts\python"
) else if exist "%cd%\.venv" (
    set "pip_exe=%cd%\.venv\Scripts\pip"
    set "python_exe=%cd%\.venv\Scripts\python"
) else if exist "%cd%\env" (
    set "pip_exe=%cd%\env\Scripts\pip"
    set "python_exe=%cd%\env\Scripts\python"
) else if exist "%cd%\venv" (
    set "pip_exe=%cd%\venv\Scripts\pip"
    set "python_exe=%cd%\venv\Scripts\python"
) else (
    set "pip_exe=pip"
    set "python_exe=python"
)

call conda activate difftrainerB
%python_exe% check_update.py

pause

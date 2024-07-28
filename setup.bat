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

%python_exe% -m pip install --upgrade pip --no-warn-script-location
%pip_exe% install -r requirements.txt --no-warn-script-location

echo Setup complete!
echo Launching gui...
call run_gui.bat




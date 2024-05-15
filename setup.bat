@echo off

if exist "%cd%\python" (
    set "pip_exe=%cd%\python\Scripts\pip"
    set "python_exe=%cd%\python\python.exe"
) else (
    set "pip_exe=pip"
    set "python_exe=python"
)

%python_exe% -m pip install --upgrade pip --no-warn-script-location
%pip_exe% install -r requirements.txt --no-warn-script-location

echo Setup complete!
echo Launching gui...
call run_gui.bat




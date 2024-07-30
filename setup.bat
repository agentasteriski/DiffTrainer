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
call conda env create -f assets\environmentA.yml
call conda env create -f assets\environmentB.yml
call conda activate difftrainerA
%python_exe% torchdropA.py
call conda activate difftrainerB
%python_exe% torchdropB.py

echo Setup complete!
echo Launching gui...
%python_exe% check_update.py




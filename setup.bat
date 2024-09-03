@echo off

if exist "%cd%\python" (
	set "conda_hook=%cd%\condabin\conda_hook.bat"
	set "pip_exe=%cd%\python\Scripts\pip"
	set "python_exe=%cd%\python\python.exe"
) else if exist "C:\Users\%username%\anaconda3" (
	set "conda_hook=C:\Users\%username%\anaconda3\condabin\conda_hook.bat"
	set "pip_exe=C:\Users\%username%\anaconda3\Scripts\pip"
	set "python_exe=C:\Users\%username%\anaconda3\python.exe"
) else if exist "C:\Users\%username%\miniconda3" (
	set "conda_hook=C:\Users\%username%\miniconda3\condabin\conda_hook.bat"
	set "pip_exe=C:\Users\%username%\miniconda3\Scripts\pip"
	set "python_exe=C:\Users\%username%\miniconda3\python.exe"
) else if exist "C:\ProgramData\anaconda3" (
	set "conda_hook=C:\ProgramData\anaconda3\condabin\conda_hook.bat"
	set "pip_exe=C:\ProgramData\anaconda3\Scripts\pip"
	set "python_exe=C:\ProgramData\anaconda3\python.exe"
) else if exist "C:\ProgramData\miniconda3" (
	set "conda_hook=C:\ProgramData\miniconda3\condabin\conda_hook.bat"
	set "pip_exe=C:\ProgramData\miniconda3\Scripts\pip"
	set "python_exe=C:\ProgramData\miniconda3\python.exe"
) else (
	echo Conda not located, proceeding anyways...
	set "pip_exe=pip"
	set "python_exe=python"
)

%python_exe% -m pip install --upgrade pip==23.0.1 --no-warn-script-location
echo Installing base requirements...
%pip_exe% install -r requirements.txt --no-warn-script-location
call %conda_hook%
echo Creating environments...
call conda env create -f assets\environmentA.yml
call conda env create -f assets\environmentB.yml
call conda activate difftrainerA
python torchdropA.py
call conda activate difftrainerB
python torchdropB.py
call conda activate difftrainerA

echo Setup complete!
echo Launching GUI in environment A...
python check_update.py




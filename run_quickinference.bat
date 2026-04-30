@echo off
cd %~dp0
if exist "%~dp0\miniconda" (
	set "conda_hook=%~dp0\miniconda\condabin\conda_hook.bat"
) else if exist "C:\Users\%username%\anaconda3" (
	set "conda_hook=C:\Users\%username%\anaconda3\condabin\conda_hook.bat"
) else if exist "C:\Users\%username%\miniconda3" (
	set "conda_hook=C:\Users\%username%\miniconda3\condabin\conda_hook.bat"
) else if exist "C:\ProgramData\anaconda3" (
	set "conda_hook=C:\ProgramData\anaconda3\condabin\conda_hook.bat"
) else if exist "C:\ProgramData\miniconda3" (
	set "conda_hook=C:\ProgramData\miniconda3\condabin\conda_hook.bat"
) else (
	echo Conda not located, proceeding anyways...
)

echo Activating environment A...
call %conda_hook% & conda activate difftrainerA && python quickinference.py
pause

@echo off
if exist "%cd%\miniconda" (
	set "conda_hook=%cd%\miniconda\condabin\conda_hook.bat"
) else if exist "C:\Users\%username%\anaconda3" (
	set "conda_hook=C:\Users\%username%\anaconda3\condabin\conda_hook.bat"
) else if exist "C:\Users\%username%\miniconda3" (
	set "conda_hook=C:\Users\%username%\miniconda3\condabin\conda_hook.bat"
) else if exist "C:\Users\%username%\anaconda" (
	set "conda_hook=C:\Users\%username%\anaconda\condabin\conda_hook.bat"
) else if exist "C:\Users\%username%\miniconda" (
	set "conda_hook=C:\Users\%username%\miniconda\condabin\conda_hook.bat"
) else if exist "C:\ProgramData\anaconda3" (
	set "conda_hook=C:\ProgramData\anaconda3\condabin\conda_hook.bat"
) else if exist "C:\ProgramData\miniconda3" (
	set "conda_hook=C:\ProgramData\miniconda3\condabin\conda_hook.bat"
) else if exist "C:\ProgramData\anaconda" (
	set "conda_hook=C:\ProgramData\anaconda\condabin\conda_hook.bat"
) else if exist "C:\ProgramData\miniconda" (
	set "conda_hook=C:\ProgramData\miniconda\condabin\conda_hook.bat"
) else (
	echo Conda not located, proceeding anyways...
)

call %conda_hook%

echo Activating environment...
call conda activate difftrainer && python check_update.py
pause

@echo off
if exist "%cd%\miniconda" (
	set "conda_hook=%cd%\miniconda\scripts\activate.bat"
) else if exist "C:\Users\%username%\anaconda3" (
	set "conda_hook=C:\Users\%username%\anaconda3\scripts\activate.bat"
) else if exist "C:\Users\%username%\miniconda3" (
	set "conda_hook=C:\Users\%username%\miniconda3\scripts\activate.bat"
) else if exist "C:\Users\%username%\anaconda" (
	set "conda_hook=C:\Users\%username%\anaconda\scripts\activate.bat"
) else if exist "C:\Users\%username%\miniconda" (
	set "conda_hook=C:\Users\%username%\miniconda\scripts\activate.bat"
) else if exist "C:\ProgramData\anaconda3" (
	set "conda_hook=C:\ProgramData\anaconda3\scripts\activate.bat"
) else if exist "C:\ProgramData\miniconda3" (
	set "conda_hook=C:\ProgramData\miniconda3\scripts\activate.bat"
) else if exist "C:\ProgramData\anaconda" (
	set "conda_hook=C:\ProgramData\anaconda\scripts\activate.bat"
) else if exist "C:\ProgramData\miniconda" (
	set "conda_hook=C:\ProgramData\miniconda\scripts\activate.bat"
) else (
	echo Conda not located, proceeding anyways...
)

call %conda_hook%

echo Activating environment...
call conda activate difftrainer && tensorboard --logdir=DiffSinger\checkpoints
pause

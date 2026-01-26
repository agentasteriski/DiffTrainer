@echo off

set "download_url=https://repo.anaconda.com/miniconda/Miniconda3-py310_24.5.0-0-Windows-x86_64.exe" #exact version needed instead of the latest python
set "installer_name=miniconda_installer.exe"
set "install_path=%cd%\miniconda"
set "conda_python=%cd%\miniconda\python.exe"
set "conda_hook=%cd%\miniconda\scripts\activate.bat"

echo downloading miniconda installer...
powershell -ExecutionPolicy Bypass -command "invoke-webrequest -uri %download_url% -outfile %installer_name%"


echo installing miniconda...
%installer_name% /InstallationType=JustMe /RegisterPython=0 /S /D=%install_path%

echo cleaning up...
del %installer_name%

call %conda_hook%

echo installing requirements...
call conda env create --file %cd%\assets\environment.yml

:: continuing everything else in python <333
call conda activate difftrainer && python auto_torch.py

echo miniconda setup complete.

pause

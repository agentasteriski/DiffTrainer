@echo off
cd %~dp0
set "download_url=https://repo.anaconda.com/miniconda/Miniconda3-py310_24.5.0-0-Windows-x86_64.exe" #exact version needed instead of the latest python
set "installer_name=miniconda_installer.exe"
set "install_path=%~dp0\miniconda"
set "conda_python=%~dp0\miniconda\python.exe"
set "conda_pip=%~dp0\miniconda\Scripts\pip.exe"

echo downloading miniconda installer...
powershell -ExecutionPolicy Bypass -command "invoke-webrequest -uri %download_url% -outfile %installer_name%"


echo installing miniconda...
%installer_name% /InstallationType=JustMe /RegisterPython=0 /S /D=%install_path%

echo cleaning up...
del %installer_name%

echo installing GUI's requirements...
%conda_pip% install -r requirements.txt --no-warn-script-location

:: continuing everything else in python <333
%conda_python% setup_conda_envs.py

echo miniconda setup complete.

pause

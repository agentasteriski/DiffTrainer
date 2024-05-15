@echo off

echo Downloading python installer
curl -o %cd%\assets\python-3.10.11-amd64.exe https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe

echo Granting write permissions to current user's directory... (for installing python)
set dir=.
for /f "tokens=*" %%a in ('whoami') do set current=%%a
icacls "%dir%" /grant "%current%:(oi)(ci)f" /t

echo Installing python....
assets\python-3.10.11-amd64.exe InstallAllUsers=0 DefaultJustForMeTargetDir=%cd%\python

%cd%\python\python.exe -m pip install --upgrade pip --no-warn-script-location
%cd%\python\Scripts\pip install customtkinter tk tdqm pyyaml requests pillow --no-warn-script-location

echo Setup complete!
echo Launching gui...
call run_gui.bat




@echo off

echo Downloading python installer(s)
curl -o %cd%\assets\python-3.10.11.exe https://www.python.org/ftp/python/3.10.11/python-3.10.11.exe
curl -o %cd%\assets\python-3.10.11-amd64.exe https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe

echo Granting write permissions to current user for directory... (for installing python)
set dir=.
for /f "tokens=*" %%a in ('whoami') do set current=%%a
icacls "%dir%" /grant "%current%:(oi)(ci)f" /t

set "arch="
for /f "tokens=2 delims==" %%a in ('wmic os get OSArchitecture /value') do set "arch=%%a"
if "%arch%"=="32-bit" (
    echo Installing python....
    assets\python-3.10.11.exe InstallAllUsers=0 DefaultJustForMeTargetDir=%cd%\python
    echo Python installed successfully!
) else if "%arch%"=="64-bit" (
    echo Installing python....
    assets\python-3.10.11-amd64.exe InstallAllUsers=0 DefaultJustForMeTargetDir=%cd%\python
    echo Python installed successfully!
) else (
    echo Unable to determine system architecture. Your system might not be compatible with python.
)

%cd%\python\python.exe -m pip install --upgrade pip --no-warn-script-location
%cd%\python\Scripts\pip install customtkinter tk tdqm pyyaml requests pillow --no-warn-script-location

pause

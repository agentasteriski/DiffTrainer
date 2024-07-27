@echo off

echo Downloading Miniconda installer
curl -o %cd%\assets\Miniconda3-latest-Windows-x86_64.exe https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe

echo Granting write permissions to current user's directory... (for installing python)
set dir=.
for /f "tokens=*" %%a in ('whoami') do set current=%%a
icacls "%dir%" /grant "%current%:(oi)(ci)f" /t

echo Installing Miniconda....
assets\Miniconda3-latest-Windows-x86_64.exe /S /D=%cd%\python

pause

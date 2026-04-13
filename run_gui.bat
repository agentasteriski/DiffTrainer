@echo off
cd %~dp0
set "conda_python=%~dp0\miniconda\python.exe"

if exist %conda_python% (
	%conda_python% check_update.py
) else (
	python check_update.py
)

pause
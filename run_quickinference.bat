@echo off
cd %~dp0
set "conda_python=%~dp0\miniconda\python.exe"

if exist %conda_python% (
	%conda_python% quickinference.py
) else (
	python quickinference.py
)

pause

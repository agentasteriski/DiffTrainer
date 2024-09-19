@echo off

set "conda_python=%cd%\miniconda\python.exe"

if exist %conda_python% (
	%conda_python% check_update.py
) else (
	python check_update.py
)

pause
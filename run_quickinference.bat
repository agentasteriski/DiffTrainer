@echo off

set "conda_python=%cd%\miniconda\python.exe"

if exist %conda_python% (
	%conda_python% quickinference.py
) else (
	python quickinference.py
)

pause

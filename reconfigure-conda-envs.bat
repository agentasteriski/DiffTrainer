@echo off

set "conda_python=%cd%\miniconda\python.exe"

if exist %conda_python% (
	%conda_python% setup_conda_envs.py
) else (
	python setup_conda_envs.py
)

pause
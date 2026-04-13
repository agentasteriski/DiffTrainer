@echo off
cd %~dp0
set "conda_python=%~dp0\miniconda\python.exe"

if exist %conda_python% (
	%conda_python% setup_conda_envs.py
) else (
	python setup_conda_envs.py
)

pause
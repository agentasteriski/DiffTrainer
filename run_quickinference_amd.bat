@echo off
cd %~dp0
echo Running Quick Inference with AMD ROCm venv (Python 3.12)...
"%~dp0venv\Scripts\python.exe" quickinference.py
pause
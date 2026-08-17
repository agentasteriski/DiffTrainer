@echo off
cd %~dp0
if not exist "%~dp0venv\Scripts\python.exe" (
    echo [ERROR] venv not found. Run setup_amd.bat first.
    pause
    exit /b 1
)
echo Running DiffTrainer GUI with AMD ROCm venv (Python 3.12)...
"%~dp0venv\Scripts\python.exe" difftrainer.py
pause
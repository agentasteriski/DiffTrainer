@echo off
setlocal
cd %~dp0

echo ============================================
echo  DiffTrainer - AMD GPU (ROCm) Setup
echo ============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python launcher 'py' not found on PATH.
    echo Install Python 3.12 from python.org and enable the launcher.
    pause
    exit /b 1
)

py -3.12 -c "import sys" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python 3.12 not found. Install it from python.org.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo Creating venv with Python 3.12...
    py -3.12 -m venv venv
    if errorlevel 1 goto :fail
) else (
    echo venv already exists, skipping creation.
)

set "PY=%~dp0venv\Scripts\python.exe"

echo Upgrading pip/setuptools/wheel...
"%PY%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :fail

echo.
echo Installing AMD ROCm SDK 7.2.1 (large download, ~1.3 GB)...
"%PY%" -m pip install --no-cache-dir ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/rocm_sdk_core-7.2.1-py3-none-win_amd64.whl ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/rocm_sdk_devel-7.2.1-py3-none-win_amd64.whl ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/rocm_sdk_libraries_custom-7.2.1-py3-none-win_amd64.whl ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/rocm-7.2.1.tar.gz
if errorlevel 1 goto :fail

echo.
echo Installing PyTorch for ROCm (torch 2.9.1, large download ~1.5 GB)...
"%PY%" -m pip install --no-cache-dir ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/torch-2.9.1%%2Brocm7.2.1-cp312-cp312-win_amd64.whl ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/torchvision-0.24.1%%2Brocm7.2.1-cp312-cp312-win_amd64.whl ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/torchaudio-2.9.1%%2Brocm7.2.1-cp312-cp312-win_amd64.whl
if errorlevel 1 goto :fail

echo.
echo Installing DiffTrainer requirements...
if not exist "requirements_win_amd.txt" (
    echo [ERROR] requirements_win_amd.txt not found.
    goto :fail
)
"%PY%" -m pip install -r requirements_win_amd.txt
if errorlevel 1 goto :fail

echo.
echo Verifying GPU...
"%PY%" -c "import torch; print('torch', torch.__version__); print('GPU available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0))"
if errorlevel 1 goto :fail

echo.
echo ============================================
echo  Setup complete! Launch with run_gui_amd.bat
echo ============================================
pause
exit /b 0

:fail
echo.
echo [ERROR] A setup step failed. Check the output above.
pause
exit /b 1
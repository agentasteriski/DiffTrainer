@echo off
cd %~dp0
echo Launching TensorBoard (AMD ROCm venv)...
"%~dp0venv\Scripts\python.exe" -m tensorboard.main --logdir=DiffSinger\checkpoints
pause
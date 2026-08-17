@echo off
cd %~dp0
echo Preparing Variance TensorBoard view...
"%~dp0venv\Scripts\python.exe" make_tb_views.py variance
echo Launching TensorBoard (Variance)...
"%~dp0venv\Scripts\python.exe" -m tensorboard.main --logdir=DiffSinger\tb_views\variance --port 6006
pause
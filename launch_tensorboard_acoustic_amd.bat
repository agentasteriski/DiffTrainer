@echo off
cd %~dp0
echo Preparing Acoustic TensorBoard view...
"%~dp0venv\Scripts\python.exe" make_tb_views.py acoustic
echo Launching TensorBoard (Acoustic)...
"%~dp0venv\Scripts\python.exe" -m tensorboard.main --logdir=DiffSinger\tb_views\acoustic --port 6007
pause
import subprocess, os

main_path = os.getcwd()
if os.path.exists(f"{main_path}/python"):
    pip_exe = f"{main_path}/python/Scripts/pip"
    python_exe = f"{main_path}/python/python.exe"
elif os.path.exists(f"{main_path}/.env"):
    pip_exe = f"{main_path}/.env/Scripts/pip"
    python_exe = f"{main_path}/.env/Scripts/python"
elif os.path.exists(f"{main_path}/.venv"):
    pip_exe = f"{main_path}/.venv/Scripts/pip"
    python_exe = f"{main_path}/.venv/Scripts/python"
elif os.path.exists(f"{main_path}/env"):
    pip_exe = f"{main_path}/env/Scripts/pip"
    python_exe = f"{main_path}/env/Scripts/python"
elif os.path.exists(f"{main_path}/venv"):
    pip_exe = f"{main_path}/venv/Scripts/pip"
    python_exe = f"{main_path}/venv/Scripts/python"
else:
    pip_exe = "pip"
    python_exe = "python"
try:
    output = subprocess.check_output(["nvcc", "--version"], stderr=subprocess.STDOUT).decode()
    lines = output.split("\n")
    for line in lines:
        if "release" in line.lower():
            version = line.split()[-1]
            print("CUDA version:", version)
            subprocess.check_call([pip_exe, "install", "torch==1.13.1+cu117", "torchvision==0.14.1+cu117", "torchaudio==0.13.1", "--extra-index-url", "https://download.pytorch.org/whl/cu117", "--no-warn-script-location"])
            subprocess.check_call([pip_exe, "install", "protobuf", "--no-warn-script-location"])
            subprocess.check_call([pip_exe, "install", "onnxruntime", "--no-warn-script-location"])
            subprocess.check_call([pip_exe, "install", "click", "--no-warn-script-location"])
            break
    else:
        print("CUDA version not found")
        subprocess.check_call([pip_exe, "install", "torch==1.13.1", "torchvision==0.14.1", "torchaudio==0.13.1", "--no-warn-script-location"])
        subprocess.check_call([pip_exe, "install", "protobuf", "--no-warn-script-location"])
        subprocess.check_call([pip_exe, "install", "onnxruntime", "--no-warn-script-location"])
        subprocess.check_call([pip_exe, "install", "click", "--no-warn-script-location"])
except (FileNotFoundError, subprocess.CalledProcessError):
    print("CUDA is not available")
    subprocess.check_call([pip_exe, "install", "torch==1.13.1", "torchvision==0.14.1", "torchaudio==0.13.1", "--no-warn-script-location"])
    subprocess.check_call([pip_exe, "install", "protobuf", "--no-warn-script-location"])
    subprocess.check_call([pip_exe, "install", "onnxruntime", "--no-warn-script-location"])
    subprocess.check_call([pip_exe, "install", "click", "--no-warn-script-location"])
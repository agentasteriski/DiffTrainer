#doing this with python instead of cmd cus it stops running after 1 env setup????
import os, subprocess, sys


def is_linux():
    return sys.platform.startswith("linux")
def is_windows():
    return sys.platform.startswith("win")
def is_macos():
    return sys.platform.startswith("darwin")

mainpath = os.path.dirname(__file__)
if is_windows():
    username = os.environ.get('USERNAME')
    if os.path.exists(os.path.join(mainpath, "miniconda")):
        conda_path = os.path.join(mainpath, "miniconda", "condabin", "conda.bat")
    elif os.path.exists(os.path.join("C:", os.sep, "ProgramData", "anaconda3")):
        conda_path = os.path.join("C:", os.sep, "ProgramData", "anaconda3", "condabin", "conda.bat")
    elif os.path.exists(os.path.join("C:", os.sep, "ProgramData", "miniconda3")):
        conda_path = os.path.join("C:", os.sep, "ProgramData", "miniconda3", "condabin", "conda.bat")
    elif os.path.exists(os.path.join("C:", os.sep, "Users", username, "anaconda3")):
        conda_path = os.path.join("C:", os.sep, "Users", username, "anaconda3", "condabin", "conda.bat")
    elif os.path.exists(os.path.join("C:", os.sep, "Users", username, "miniconda3")):
        conda_path = os.path.join("C:", os.sep, "Users", username, "miniconda3", "condabin", "conda.bat")
    else: 
        conda_path = "conda"
elif is_macos():
    if os.path.exists(os.path.join("opt", "miniconda3")):
        conda_path = os.path.join("opt", "miniconda3", "etc", "profile.d", "conda.sh")
    elif os.path.exists(os.path.join("opt", "anaconda3")):
        conda_path = os.path.join("opt", "anaconda3", "etc", "profile.d", "conda.sh")
    else: 
        conda_path = "conda"
elif is_linux():
    username = os.environ.get('USER')
    if os.path.exists(os.path.join("home", username, "anaconda3")):
        conda_path = os.path.join("home", username, "anaconda3", "etc", "profile.d", "conda.sh")
    elif os.path.exists(os.path.join("home", username, "miniconda3")):
        conda_path = os.path.join("home", username, "miniconda3", "etc", "profile.d", "conda.sh")
    else: 
        conda_path = "conda"
###create envs###

def run_cmd(cmd):
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

def run_cmdA(cmd):
    if is_windows():
        cmd = f'"{conda_path}" activate difftrainerA >nul && {cmd}'
    elif is_linux() or is_macos():
        cmd = f'eval "$(conda shell.bash hook)" && {conda_path} activate difftrainerA && {cmd}'
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

def run_cmdB(cmd):
    if is_windows():
        cmd = f'"{conda_path}" activate difftrainerB >nul && {cmd}'
    elif is_linux() or is_macos():
        cmd = f'eval "$(conda shell.bash hook)" && {conda_path} activate difftrainerB && {cmd}'
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

def run_cmdBase(cmd):
    if is_windows():
        cmd = cmd
    elif is_linux() or is_macos():
        cmd = f'eval "$(conda shell.bash hook)" && {cmd}'
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

print("Creating environment for DiffSinger...")
try:
    output = subprocess.check_output([conda_path, "env", "list"], stderr=subprocess.STDOUT).decode()
    lines = output.split("\n")
    for line in lines:
        if "difftrainerA" in line:
                command = [conda_path, "remove", "-n", "difftrainerA", "--all", "--yes"]
                yeet = " ".join(command)
                run_cmdBase(yeet)
    envtxt = os.path.join(mainpath, "assets", "environmentA.yml")
except:
    print("Error removing old environment")
run_cmdBase(f'"{conda_path}" env create -f {envtxt}')


print("Creating environment for ONNX...")
try:
    output = subprocess.check_output([conda_path, "env", "list"], stderr=subprocess.STDOUT).decode()
    lines = output.split("\n")
    for line in lines:
        if "difftrainerB" in line:
            command = [conda_path, "remove", "-n", "difftrainerB", "--all", "--yes"]
            yeet = " ".join(command)
            run_cmdBase(yeet)
except:
    print("Error removing old environment")
envtxt = os.path.join(mainpath, "assets", "environmentB.yml")
run_cmdBase(f'"{conda_path}" env create -f {envtxt}')


###setup envs###

print("Setting up training environment...")
try:
    output = subprocess.check_output(["nvcc", "--version"], stderr=subprocess.STDOUT).decode()
    lines = output.split("\n")
    for line in lines:
        if "release" in line.lower():
            release = line.split(',')[-2]
            version = release.split()[1]
            print("CUDA version:", version)
            if "11.8" <= version < "12.1":
                torch = ["pip", "install", "torch==2.4.0+cu118", "torchvision==0.19.0+cu118", "torchaudio==2.4.0", "--extra-index-url", "https://download.pytorch.org/whl/cu118", "--no-warn-script-location"]
                nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmdA(command1)
                run_cmdA(command2)
                break
            elif "12.1" <= version < "12.4":
                torch = ["pip", "install", "torch==2.4.0+cu121", "torchvision==0.19.0+cu121", "torchaudio==2.4.0", "--extra-index-url", "https://download.pytorch.org/whl/cu121", "--no-warn-script-location"]
                nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmdA(command1)
                run_cmdA(command2)
                break
            elif "12.4" <= version < "12.6":
                torch = ["pip", "install", "torch==2.4.0+cu124", "torchvision==0.19.0+cu124", "torchaudio==2.4.0", "--extra-index-url", "https://download.pytorch.org/whl/cu124", "--no-warn-script-location"]
                nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmdA(command1)
                run_cmdA(command2)
                break
            elif "12.6" <= version < "12.8":
                print("Preferred Torch version not available for this CUDA version, installing latest")
                torch = ["pip", "install", "torch", "torchvision", "torchaudio", "--extra-index-url", "https://download.pytorch.org/whl/cu126", "--no-warn-script-location"]
                nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmdA(command1)
                run_cmdA(command2)
                break
            elif version == "12.8":
                print("Preferred Torch version not available for this CUDA version, installing latest")
                torch = ["pip", "install", "torch", "torchvision", "torchaudio", "--extra-index-url", "https://download.pytorch.org/whl/cu128", "--no-warn-script-location"]
                nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmdA(command1)
                run_cmdA(command2)
                break
            elif version > "12.8":
                print("CUDA version not supported as of 05/27/25, trying 12.8")
                torch = ["pip", "install", "torch", "torchvision", "torchaudio", "--extra-index-url", "https://download.pytorch.org/whl/cu128", "--no-warn-script-location"]
                nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmdA(command1)
                run_cmdA(command2)
                break
            else:
                print("Unsupported CUDA version detected! Installing CPU Torch")
                torch = ["pip", "install", "torch==2.4.0", "torchvision==0.19.0", "torchaudio==2.4.0", "--no-warn-script-location"]
                nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmdA(command1)
                run_cmdA(command2)
                break
    else:
        print("CUDA version not found")
        torch = ["pip", "install", "torch==2.4.0", "torchvision==0.19.0", "torchaudio==2.4.0", "--no-warn-script-location"]
        nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
        command1 = " ".join(torch)
        command2 = " ".join(nottorch)
        run_cmdA(command1)
        run_cmdA(command2)
except (FileNotFoundError, subprocess.CalledProcessError):
    print("CUDA is not available")
    if is_macos():
        print("Mac detected! Installing latest available for this CPU")
        torch = ["pip", "install", "torch", "torchvision", "torchaudio", "--no-warn-script-location"]
        nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
        command1 = " ".join(torch)
        command2 = " ".join(nottorch)
        run_cmdA(command1)
        run_cmdA(command2)
    else:
        torch = ["pip", "install", "torch==2.4.0", "torchvision==0.19.0", "torchaudio==2.4.0", "--no-warn-script-location"]
        nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
        command1 = " ".join(torch)
        command2 = " ".join(nottorch)
        run_cmdA(command1)
        run_cmdA(command2)
deac = [conda_path, "deactivate"]
deactivate = " ".join(deac)
run_cmdBase(deactivate)

print("Setting up ONNX environment...")
if is_macos:
    torch = ["pip", "install", "torch==1.13.1", "torchvision==0.14.1", "torchaudio==0.13.1", "--no-warn-script-location"]
else: 
    torch = ["pip", "install", "torch==1.13.1+cpu", "torchvision==0.14.1+cpu", "torchaudio==0.13.1", "--extra-index-url", "https://download.pytorch.org/whl/cpu", "--no-warn-script-location"]
nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
command1 = " ".join(torch)
command2 = " ".join(nottorch)
run_cmdB(command1)
run_cmdB(command2)
run_cmdBase(deactivate)
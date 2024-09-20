#doing this with python instead of cmd cus it stops running after 1 env setup????
import os, subprocess, sys

username = os.environ.get('USERNAME')
def is_linux():
    return sys.platform.startswith("linux")
def is_windows():
    return sys.platform.startswith("win")
def is_macos():
    return sys.platform.startswith("darwin")

mainpath = os.getcwd()
if os.path.exists(os.path.join(mainpath, "miniconda")):
    conda_path = os.path.join(mainpath, "miniconda", "condabin", "conda.bat")
elif os.path.exists(os.path.join("C:", "ProgramData", "anaconda3")):
    conda_path = os.path.join("C:", "ProgramData", "anaconda3", "condabin", "conda.bat")
elif os.path.exists(os.path.join("C:", "ProgramData", "miniconda3")):
    conda_path = os.path.join("C:", "ProgramData", "miniconda3", "condabin", "conda.bat")
elif os.path.exists(os.path.join("C:", "Users", username, "anaconda3")):
    conda_path = os.path.join("C:", "Users", username, "anaconda3", "condabin", "conda.bat")
elif os.path.exists(os.path.join("C:", "Users", username, "miniconda3")):
    conda_path = os.path.join("C:", "Users", username, "miniconda3", "condabin", "conda.bat")
elif os.path.exists(os.path.join("opt", "miniconda3")):
    conda_path = os.path.join("opt", "miniconda3", "etc", "profile.d", "conda.sh")
elif os.path.exists(os.path.join("opt", "anaconda3")):
    conda_path = os.path.join("opt", "anaconda3", "etc", "profile.d", "conda.sh")
elif os.path.exists(os.path.join("Users", username, "anaconda3")):
    conda_path = os.path.join("Users", username, "anaconda3", "etc", "profile.d", "conda.sh")
elif os.path.exists(os.path.join("Users", username, "miniconda3")):
    conda_path = os.path.join("Users", username, "miniconda3", "etc", "profile.d", "conda.sh")
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
        cmd = f'. "{conda_path}" && conda activate difftrainerA && {cmd}'
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

def run_cmdB(cmd):
    if is_windows():
        cmd = f'"{conda_path}" activate difftrainerB >nul && {cmd}'
    elif is_linux() or is_macos():
        cmd = f'. "{conda_path}" && conda activate difftrainerB && {cmd}'
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

print("Creating environment for DiffSinger...")
output = subprocess.check_output([conda_path, "env", "list"], stderr=subprocess.STDOUT).decode()
lines = output.split("\n")
for line in lines:
    if "difftrainerA" in line:
        command = [conda_path, "remove", "-n", "difftrainerA", "--all", "--yes"]
        yeet = " ".join(command)
        run_cmd(yeet)
run_cmd(f'"{conda_path}" env create -f assets/environmentA.yml')


print("Creating environment for ONNX...")
try:
    output = subprocess.check_output([conda_path, "env", "list"], stderr=subprocess.STDOUT).decode()
    lines = output.split("\n")
    for line in lines:
        if "difftrainerb" in line.lower():
            command = [conda_path, "remove", "-n", "difftrainerB", "--all", "--yes"]
            yeet = " ".join(command)
            run_cmd(yeet)
except:
    print("Error removing old environment")
run_cmd(f'"{conda_path}" env create -f assets/environmentB.yml')


###setup envs###

print("Setting up training environment...")
try:
    output = subprocess.check_output(["nvcc", "--version"], stderr=subprocess.STDOUT).decode()
    lines = output.split("\n")
    for line in lines:
        if "release" in line.lower():
            version = line.split()[-1]
            print("CUDA version:", version)
            torch = ["pip", "install", "torch==2.3.1+cu118", "torchvision==0.18.1+cu118", "torchaudio==2.3.1", "--extra-index-url", "https://download.pytorch.org/whl/cu118", "--no-warn-script-location"]
            nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
            command1 = " ".join(torch)
            command2 = " ".join(nottorch)
            run_cmdA(command1)
            run_cmdA(command2)
            break
    else:
        print("CUDA version not found")
        torch = ["pip", "install", "torch==2.3.1", "torchvision==0.18.1", "torchaudio==2.3.1", "--no-warn-script-location"]
        nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
        command1 = " ".join(torch)
        command2 = " ".join(nottorch)
        run_cmdA(command1)
        run_cmdA(command2)
except (FileNotFoundError, subprocess.CalledProcessError):
    print("CUDA is not available")
    torch = ["pip", "install", "torch==2.3.1", "torchvision==0.18.1", "torchaudio==2.3.1", "--no-warn-script-location"]
    nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
    command1 = " ".join(torch)
    command2 = " ".join(nottorch)
    run_cmdA(command1)
    run_cmdA(command2)
deac = [conda_path, "deactivate"]
deactivate = " ".join(deac)
run_cmd(deactivate)

print("Setting up ONNX environment...")
try:
    output = subprocess.check_output(["nvcc", "--version"], stderr=subprocess.STDOUT).decode()
    lines = output.split("\n")
    for line in lines:
        if "release" in line.lower():
            version = line.split()[-1]
            print("CUDA version:", version)
            torch = ["pip", "install", "torch==1.13.1+cu117", "torchvision==0.14.1+cu117", "torchaudio==0.13.1", "--extra-index-url", "https://download.pytorch.org/whl/cu117", "--no-warn-script-location"]
            nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
            command1 = " ".join(torch)
            command2 = " ".join(nottorch)
            run_cmdB(command1)
            run_cmdB(command2)
            break
    else:
        print("CUDA version not found")
        torch = ["pip", "install", "torch==1.13.1", "torchvision==0.14.1", "torchaudio==0.13.1", "--no-warn-script-location"]
        nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
        command1 = " ".join(torch)
        command2 = " ".join(nottorch)
        run_cmdB(command1)
        run_cmdB(command2)
except (FileNotFoundError, subprocess.CalledProcessError):
    print("CUDA is not available")
    torch = ["pip", "install", "torch==1.13.1", "torchvision==0.14.1", "torchaudio==0.13.1", "--no-warn-script-location"]
    nottorch = ["pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
    command1 = " ".join(torch)
    command2 = " ".join(nottorch)
    run_cmdB(command1)
    run_cmdB(command2)
run_cmd(deactivate)
run_cmd("pause")
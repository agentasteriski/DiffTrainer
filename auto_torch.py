import os, subprocess, sys, platform


def is_linux():
    return sys.platform.startswith("linux")
def is_windows():
    return sys.platform.startswith("win")
def is_macos():
    return sys.platform.startswith("darwin")
def is_mchip():
    return platform.processor('arm')

mainpath = os.path.dirname(__file__)

realpython = sys.executable

def run_cmd(cmd):
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

def run_cmd_noshell(cmd):
    try:
        subprocess.run(cmd, check=True, shell=False)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

def has_amd_gpu():
    if is_windows():
        try:
            output = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command",
                 "(Get-CimInstance win32_VideoController | Select-Object -ExpandProperty Name) -join ' '"],
                stderr=subprocess.STDOUT).decode(errors="ignore").upper()
            return ("AMD" in output) or ("RADEON" in output)
        except Exception:
            return False
    elif is_linux():
        try:
            output = subprocess.check_output(["lspci"], stderr=subprocess.DEVNULL).decode(errors="ignore").upper()
            return (("AMD" in output) or ("RADEON" in output)) and ("NVIDIA" not in output)
        except Exception:
            return False
    return False

def install_rocm_windows():
    print("AMD GPU detected on Windows! Installing ROCm-enabled PyTorch...")
    if sys.version_info[:2] != (3, 12):
        print("WARNING: AMD ROCm on Windows wheels require Python 3.12. This environment is Python %d.%d and installation will likely fail." % sys.version_info[:2])
    sdk = ["https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/" + f for f in [
        "rocm_sdk_core-7.2.1-py3-none-win_amd64.whl",
        "rocm_sdk_devel-7.2.1-py3-none-win_amd64.whl",
        "rocm_sdk_libraries_custom-7.2.1-py3-none-win_amd64.whl",
        "rocm-7.2.1.tar.gz"]]
    print("Installing ROCm SDK (large download, ~1.3 GB)...")
    run_cmd_noshell([realpython, "-m", "pip", "install", "--no-cache-dir"] + sdk)
    torch = ["https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/" + f for f in [
        "torch-2.9.1%2Brocm7.2.1-cp312-cp312-win_amd64.whl",
        "torchvision-0.24.1%2Brocm7.2.1-cp312-cp312-win_amd64.whl",
        "torchaudio-2.9.1%2Brocm7.2.1-cp312-cp312-win_amd64.whl"]]
    print("Installing PyTorch for ROCm (large download, ~1.5 GB)...")
    run_cmd_noshell([realpython, "-m", "pip", "install", "--no-cache-dir"] + torch)
    run_cmd(" ".join([realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]))

def install_rocm_linux():
    print("AMD GPU detected on Linux! Installing ROCm-enabled PyTorch...")
    torch = [realpython, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/rocm6.2", "--no-warn-script-location"]
    nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
    run_cmd(" ".join(torch))
    run_cmd(" ".join(nottorch))


print("Selecting the right Torch for your system...")
try:
    output = subprocess.check_output(["nvcc", "--version"], stderr=subprocess.STDOUT).decode()
    lines = output.split("\n")
    for line in lines:
        if "release" in line.lower():
            release = line.split(',')[-2]
            version = release.split()[1]
            print("CUDA version:", version)
            if "11.8" <= version < "12.1":
                torch = [realpython, "-m", "pip", "install", "torch==2.4.0+cu118", "torchvision==0.19.0+cu118", "torchaudio==2.4.0", "--extra-index-url", "https://download.pytorch.org/whl/cu118", "--no-warn-script-location"]
                nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmd(command1)
                run_cmd(command2)
                break
            elif "12.1" <= version < "12.4":
                torch = [realpython, "-m", "pip", "install", "torch==2.4.0+cu121", "torchvision==0.19.0+cu121", "torchaudio==2.4.0", "--extra-index-url", "https://download.pytorch.org/whl/cu121", "--no-warn-script-location"]
                nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmd(command1)
                run_cmd(command2)
                break
            elif "12.4" <= version < "12.6":
                torch = [realpython, "-m", "pip", "install", "torch==2.4.0+cu124", "torchvision==0.19.0+cu124", "torchaudio==2.4.0", "--extra-index-url", "https://download.pytorch.org/whl/cu124", "--no-warn-script-location"]
                nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmd(command1)
                run_cmd(command2)
                break
            elif "12.6" <= version < "12.8":
                #print("Preferred Torch version not available for this CUDA version, installing latest")
                torch = [realpython, "-m", "pip", "install", "torch==2.8.0+cu126", "torchvision==0.23.0+cu126", "torchaudio==2.8.0", "--extra-index-url", "https://download.pytorch.org/whl/cu126", "--no-warn-script-location"]
                nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmd(command1)
                run_cmd(command2)
                break
            elif version == "12.8":
                #print("Preferred Torch version not available for this CUDA version, installing latest")
                torch = [realpython, "-m", "pip", "install", "torch==2.8.0+cu128", "torchvision==0.23.0+cu128", "torchaudio==2.8.0", "--extra-index-url", "https://download.pytorch.org/whl/cu128", "--no-warn-script-location"]
                nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmd(command1)
                run_cmd(command2)
                break
            elif version == "12.9":
                #print("Preferred Torch version not available for this CUDA version, installing latest")
                torch = [realpython, "-m", "pip", "install", "torch==2.8.0+cu129", "torchvision==0.23.0+cu129", "torchaudio==2.8.0", "--extra-index-url", "https://download.pytorch.org/whl/cu129", "--no-warn-script-location"]
                nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmd(command1)
                run_cmd(command2)
                break
            elif "13.0" <= version <= "13.1":
                print("Preferred Torch version not available for this CUDA version, installing 2.11")
                torch = [realpython, "-m", "pip", "install", "torch==2.11.0", "torchvision==0.26.0", "torchaudio==2.11.0", "--extra-index-url", "https://download.pytorch.org/whl/cu130", "--no-warn-script-location"]
                nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmd(command1)
                run_cmd(command2)
                break
            elif version == "13.2":
                print("Preferred Torch version not available for this CUDA version, installing latest")
                torch = [realpython, "-m", "pip", "install", "torch", "torchvision", "--extra-index-url", "https://download.pytorch.org/whl/cu132", "--no-warn-script-location"]
                nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmd(command1)
                run_cmd(command2)
                break
            elif version > "13.2":
                print("CUDA version not officially supported at time of writing, installing latest for 13.2")
                torch = [realpython, "-m", "pip", "install", "torch", "torchvision", "--extra-index-url", "https://download.pytorch.org/whl/cu132", "--no-warn-script-location"]
                nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmd(command1)
                run_cmd(command2)
                break
            else:
                print("Unsupported CUDA version detected! Installing generic Torch")
                torch = [realpython, "-m", "pip", "install", "torch==2.4.0", "torchvision==0.19.0", "torchaudio==2.4.0", "--no-warn-script-location"]
                nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
                command1 = " ".join(torch)
                command2 = " ".join(nottorch)
                run_cmd(command1)
                run_cmd(command2)
                break
    else:
        print("CUDA version not found")
        torch = [realpython, "-m", "pip", "install", "torch==2.4.0", "torchvision==0.19.0", "torchaudio==2.4.0", "--no-warn-script-location"]
        nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
        command1 = " ".join(torch)
        command2 = " ".join(nottorch)
        run_cmd(command1)
        run_cmd(command2)
except (FileNotFoundError, subprocess.CalledProcessError):
    print("CUDA is not available")
    if has_amd_gpu():
        if is_windows():
            install_rocm_windows()
        elif is_linux():
            install_rocm_linux()
    elif is_macos():
        if is_mchip():
            print("M-series Mac detected! Installing possible candidate Torch")
            torch = [realpython, "-m", "pip", "install", "torch<=2.11.0", "torchvision<=0.26.0", "torchaudio<=2.11.0", "--no-warn-script-location"]
            nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
            command1 = " ".join(torch)
            command2 = " ".join(nottorch)
            run_cmd(command1)
            run_cmd(command2)
        else:
            print("Intel Mac detected! good luck lol")
            torch = [realpython, "-m", "pip", "install", "torch<=2.8.0", "torchvision<=0.23.0", "torchaudio<=2.8.0", "--no-warn-script-location"]
            nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
            command1 = " ".join(torch)
            command2 = " ".join(nottorch)
            run_cmd(command1)
            run_cmd(command2)
    else:
        torch = [realpython, "-m", "pip", "install", "torch==2.4.0", "torchvision==0.19.0", "torchaudio==2.4.0", "--no-warn-script-location"]
        nottorch = [realpython, "-m", "pip", "install", "protobuf", "onnxruntime", "click", "--no-warn-script-location"]
        command1 = " ".join(torch)
        command2 = " ".join(nottorch)
        run_cmd(command1)
        run_cmd(command2)
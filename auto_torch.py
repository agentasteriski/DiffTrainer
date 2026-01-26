import os, subprocess, sys


def is_linux():
    return sys.platform.startswith("linux")
def is_windows():
    return sys.platform.startswith("win")
def is_macos():
    return sys.platform.startswith("darwin")

mainpath = os.path.dirname(__file__)

realpython = sys.executable

def run_cmd(cmd):
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")


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
                torch = realpython, "-m", ["pip", "install", "torch==2.8.0+cu128", "torchvision==0.23.0+cu128", "torchaudio==2.8.0", "--extra-index-url", "https://download.pytorch.org/whl/cu128", "--no-warn-script-location"]
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
            elif version > "12.9":
                print("CUDA version not supported, trying 12.9")
                torch = [realpython, "-m", "pip", "install", "torch==2.8.0+cu129", "torchvision==0.23.0+cu129", "torchaudio==2.8.0", "--extra-index-url", "https://download.pytorch.org/whl/cu129", "--no-warn-script-location"]
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
    if is_macos():
        print("Mac detected! Installing latest available for this CPU")
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
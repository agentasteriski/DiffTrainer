# a CustomTkInter GUI for processing and training DiffSinger models
DiffTrainer brings together the most useful tools for DiffSinger in one easy, graphical package.
- [corpus_segmenter](https://github.com/MLo7Ghinsan/ghin_shenanigans/blob/main/scripts/corpus_segmenter.py) to shorten long wav/lab pairs
- [liteconvert](https://github.com/agentasteriski/liteconvert) for converting wav+lab data to wav/csv
- [SOME](https://github.com/openvpi/SOME) for estimating pitch
- [DiffSinger](https://github.com/openvpi/DiffSinger)'s primary training
- OpenUtau export scripts

### Installation:
- Easy Mode(Windows):
    - make sure a compatible version of [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit-archive) is installed
        - compatible versions: 11.8, 12.1, 12.4, 12.6, 12.8, 12.9
    - install [miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main) (full conda works but comes with tons of stuff not needed, waste of space)
    - reconfigure_conda_env.bat
    - run_gui.bat
    - Update Tools button to finish
    - in future usage, run_gui.bat will check for DiffTrainer updates before launching(updater not yet activated)
- Easy-ish Mode(Linux)
    - make sure a compatible version of [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit-archive) is installed
        - compatible versions: 11.8, 12.1, 12.4, 12.6, 12.8, 12.9
    - install [miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main) (full conda works but comes with tons of stuff not needed, waste of space)
    - `conda env create --file assets/environment_LINUX.yml`
    - always activate newly created `difftrainer` environment before running any python files
    - run auto_torch.py
    - run difftrainer.py 
    - Update Tools button to finish
    - in future usage, check_update.py checks for DiffTrainer updates before running difftrainer.py(updater not yet activated)
- Normal Mode(Windows/Linux)
    - make sure a compatible version of [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit-archive) is installed
        - compatible versions: 11.8, 12.1, 12.4, 12.6, 12.8, 12.9
    - bring your environment manager of choice(or don't, if you live dangerously)
    - python 3.10
    - install requirements.txt (less tested than the conda equivalent `assets/environment.yml`)
    - always activate your environment before running any python files
    - run auto_torch.py OR add a compatible version of PyTorch yourself (>=2.4, <=2.8, CUDA enabled)
    - run difftrainer.py
    - Update Tools button to finish
    - in future usage, check_update.py checks for DiffTrainer updates before running difftrainer.py(updater not yet activated)
- ??? Mode(Mac)
    - see Linux instructions, but use the non-Linux environment.yml for conda
    - auto_torch should install Torch 2.11 for M-series, 2.8 for anything else
    - honestly you're on your own in general but in theory it's supposed to run
    - I'm willing to try to make it work better but my tester Mac is Intel(a lost cause)


### on environment management and .bats
Starting from DiffTrainer 0.4, environments will be once again self-manageable. All .py files will act using the environment that is active when the file is run. However, all .bat files will still be written to activate a Conda environment(specifically named `difftrainer`) and run the file from that environment. If you want to use a different environment manager or different environment name, you will need to run the .py files directly from the command line or write your own automated activation scripts. **No .bats are strictly required, they are purely for convenience.**

1. reconfigure_conda_env.bat:
    - Attempts to locate conda at either the custom location installed with the old conda_installer.bat or one of the default install locations. If it is not found at any of these locations, it will still attempt to call Conda with the system PATH.
    - Attempts to remove the difftrainer environment from the identified Conda. Continues if not found.
    - Recreates the difftrainer environment under the identified Conda
    - Runs auto_torch.py within the new difftrainer environment to finish environment setup
2. run_gui.bat:
    - Attempts to locate conda at either the custom location installed with the old conda_installer.bat or one of the default install locations. If it is not found at any of these locations, it will still attempt to call Conda with the system PATH.
    - Activates the difftrainer environment before running check_update.py(which then runs difftrainer.py)
3. launch_tensorboard.bat:
    - Attempts to locate conda at either the custom location installed with the old conda_installer.bat or one of the default install locations. If it is not found at any of these locations, it will still attempt to call Conda with the system PATH.
    - Activates the difftrainer environment before running Tensorboard pointed at the main checkpoints folder.
4. run_quickinference.bat:
    - Attempts to locate conda at either the custom location installed with the old conda_installer.bat or one of the default install locations. If it is not found at any of these locations, it will still attempt to call Conda with the system PATH.
    - Activates the difftrainer environment before running quickinference.py.

### Known issues:
- langloader editor sometimes hides behind main window
- if you type in the save interval or batch size boxes, an error appears in the terminal window
  - no actual impact, just enter your number and ignore it
- do not name checkpoint folders just "acoustic" or "variance", it conflicts with the onnx export cleanup

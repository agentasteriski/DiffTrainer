# EXPERIMENTAL BRANCH. IF THIS IS STILL HERE, USE AT YOUR OWN RISK
might have new bugs, might bring old bugs back bc I fixed them in the main branch and forgot to port it. don't bother complaining about them until this readme is gone.
## Current status: actually pretty close
### Key features:
- moves most of the big functions into separate files
- generates base dsdicts that actually work *most of the time*(direct phoneme input only for non-G2P phonemizers)
- new database conversion tool with fewer restrictions
### Goals:
- ~~add vlabeler format(separate wav/lab folder) compatibility~~
- clean up translation strings
- add translation strings for all errors and random terminal bits
- ~~add check for diffsinger updates~~
- ~~get liteconvert(in the files but unused) to work~~
- ~~implement Ghin's segmenter instead~~
- ~~target Mix_LN branch due to single environment required~~
- ~~un-Conda everything (much harder than it sounds)~~

### wait this is good, why isn't it recommended yet
- onnx export on torch 2 breaks wavenet and something on macs and the devs insist on keeping the terrible conflicting environment setup instead of deprecating wavenet/fixing the mac thing
- this difftrainer downloads a copy of diffsinger with the torch 1.13 check disabled
- I do not want users relying on something like that as part of the main branch
- I also do not want to try to put auto-management back
- absolutely no way am I releasing a main version where the user has to manually select the right environment again. we had that briefly and none of y'all remembered to use the export env.
- this was supposed to be prep for v3 but that was supposed to happen months ago and yet here we are

### on environment management and .bats
Starting from DiffTrainer 0.4, environments will be once again self-manageable. All .py files will act using the environment that is active when the file is run. However, all .bat files will still be written to activate a Conda environment(specifically named `difftrainer`) and run the file from that environment. If you want to use a different environment manager or different environment name, you will need to run the .py files directly from the command line or write your own automated activation scripts. **No .bats are strictly required, they are purely for convenience.**

~~1. conda_installer.bat:~~ removed, encourages too much technical illiteracy and is way less necessary on this branch
    ~~- Installs a copy of Miniconda specific to the DiffTrainer folder. This copy will not be used automatically by other programs. This copy will be preferred by all DiffTrainer .bat files, even if another copy is installed at a higher level. **This is prone to failing due to Windows security settings. Support for general Windows settings will not be provided.**~~
    ~~- Proceeds to configure the difftrainer Conda environment within that specific folder~~
    ~~- Runs auto_torch.py within the new difftrainer environment to finish environment setup~~
2. reconfigure_conda_env.bat:
    - Attempts to locate conda at either the custom location installed with conda_installer.bat or one of the default install locations. If it is not found at any of these locations, it will still attempt to call Conda with the system PATH.
    - Attempts to remove the difftrainer environment from the identified Conda. Continues if not found.
    - Recreates the difftrainer environment under the identified Conda
    - Runs auto_torch.py within the new difftrainer environment to finish environment setup
3. run_gui.bat:
    - Attempts to locate conda at either the custom location installed with conda_installer.bat or one of the default install locations. If it is not found at any of these locations, it will still attempt to call Conda with the system PATH.
    - Activates the difftrainer environment before running check_update.py(which then runs difftrainer.py)
4. launch_tensorboard.bat:
    - Attempts to locate conda at either the custom location installed with conda_installer.bat or one of the default install locations. If it is not found at any of these locations, it will still attempt to call Conda with the system PATH.
    - Activates the difftrainer environment before running Tensorboard pointed at the main checkpoints folder.
5. run_quickinference.bat:
    - Attempts to locate conda at either the custom location installed with conda_installer.bat or one of the default install locations. If it is not found at any of these locations, it will still attempt to call Conda with the system PATH.
    - Activates the difftrainer environment before running quickinference.py.
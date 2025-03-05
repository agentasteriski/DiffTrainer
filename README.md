# [IMPORTANT UPDATE INFORMATION](https://github.com/agentasteriski/DiffTrainer/blob/main/ANNOUNCEMENT.md)
![DiffTrainer](https://github.com/agentasteriski/DiffTrainer/blob/main/assets/difftrainerlogo.png?raw=true)

**English** *[中文（正體）](./README-zh.md)*

# a CustomTkInter GUI for processing and training DiffSinger models
DiffTrainer brings together the most useful tools for DiffSinger in one easy, graphical package.
- [nnsvs-db-converter](https://github.com/UtaUtaUtau/nnsvs-db-converter) for converting wav+lab data to wav/ds+csv
- [SOME](https://github.com/openvpi/SOME) for estimating pitch
- [DiffSinger](https://github.com/openvpi/DiffSinger)'s primary training
- OpenUtau export scripts
## setup options
### If you have an NVIDIA GPU:
- make sure [CUDA Toolkit](https://developer.nvidia.com/cuda-11-8-0-download-archive) is installed
- proceed to next 'if'
### If you have never used Python:
- run conda_installer.bat
- "Update Tools" once DiffTrainer is running
- use run_gui.bat to launch after that
### If you have used Python:
- DiffTrainer by default uses Miniconda to manage conflicting package requirements.
- To use an existing conda installation:
  - install requirements.txt to base environment(3.10 strongly recommended, other versions may still work for the base environment)
  - run setup_conda_envs.py to configure the required environments
  - "Update Tools" on the first tab to complete the install
- As of v0.2.1, the names of the environments are hardcoded requirements.

## known bug on Linux
- if the text and buttons appear jagged:
  - in the base environment, `conda install --channel=conda-forge tk[build=xft_*]`

## language support
DiffTrainer uses [ez-localizr](https://github.com/spicytigermeat/ez-localizr/tree/main) to allow GUI language selection. All users are welcome to translate the text found in [en_US](/strings/en_US.yaml) to other languages and submit a pull request.

## to do
soon
- better readme

eventually
- more translations
- an icon that isn't amogus

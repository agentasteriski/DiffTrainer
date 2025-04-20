# soon to be main branch!
Known issues:
- langloader editor usually hides behind main window
- ~~honestly langloader is just ugly and bad~~ improved as of 0.3.14(01/16/25)
- if you type in the save interval or batch size boxes, an error appears in the terminal window
  - no actual impact, just enter your number and ignore it
- if you load one dataset, change your mind and load another, it fails to write the config
- do not name checkpoint folders just "acoustic" or "variance", it conflicts with the onnx export cleanup
- (Linux only) if the text and buttons appear jagged:
  - in the base environment, `conda install --channel=conda-forge tk[build=xft_*]`
- (Mac only) dependency of a dependency `libcst` no longer packaged for x86
  - add `libcst` to upper half of environmentA/B.yml before running setup_conda_envs.py(unsure if this will continue to work or what other impacts the outdated version has)

**English** *[中文（正體）](./README-zh.md)*

# a CustomTkInter GUI for processing and training DiffSinger models
DiffTrainer brings together the most useful tools for DiffSinger in one easy, graphical package.
- [nnsvs-db-converter](https://github.com/UtaUtaUtau/nnsvs-db-converter) for converting wav+lab data to wav/ds+csv
- [SOME](https://github.com/openvpi/SOME) for estimating pitch
- [DiffSinger](https://github.com/openvpi/DiffSinger)'s primary training
- OpenUtau export scripts
## setup options
### If you have an NVIDIA GPU:
- make sure a compatible version of [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit-archive) is installed
  - current compatible versions: 11.8, 12.1, 12.4, 12.6
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
- ~~advanced export~~
- more translations
- ~~an icon that isn't amogus~~

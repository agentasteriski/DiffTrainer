# MULTIDICT BETA
Very rough. 
Known issues:
- not even sure we're doing this right
- langloader editor usually hides behind main window

**English** *[中文（正體）](./README-zh.md)*

# a CustomTkInter GUI for processing and training DiffSinger models
DiffTrainer brings together the most useful tools for DiffSinger in one easy, graphical package.
- [nnsvs-db-converter](https://github.com/UtaUtaUtau/nnsvs-db-converter) for converting wav+lab data to wav/ds+csv
- [SOME](https://github.com/openvpi/SOME) for estimating pitch
- [DiffSinger](https://github.com/openvpi/DiffSinger)'s primary training
- OpenUtau export scripts
## setup options
### If you have never used Python:
- run conda_installer.bat
- run setup.bat
- use run_guiA.bat for preprocessing and training
- use run_guiB.bat for exporting onnx

### If you have used Python:
- DiffTrainer by default uses Miniconda to manage conflicting package requirements.
- To use an existing conda installation:
  - run setup.bat to automatically create the required environments
  - OR create two environments using the requirements files in /assets/
    - run torchdropA.py in one and torchdropB.py in the other
  - run_guiA.bat and run_guiB.bat launch Difftrainer in environments DifftrainerA and DifftrainerB respectively


## language support
DiffTrainer uses [ez-localizr](https://github.com/spicytigermeat/ez-localizr/tree/main) to allow GUI language selection. All users are welcome to translate the text found in [en_US](/strings/en_US.yaml) to other languages and submit a pull request.

## to do
soon
- better readme

eventually
- advanced export
- more translations
- an icon that isn't amogus

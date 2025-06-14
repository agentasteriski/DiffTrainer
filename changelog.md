# Changelog

## 0.3.33
- fix extra_phonemes creating a fake phoneme `['']`

## 0.3.32
- muon_lynxnet2
  - redirect DiffSinger download
  - change alt. backbone toggle to dropdown selection(defaults to lynxnet2)
  - using lynxnet2 requires updating tools, can be used on older versions if lynxnet/wavenet is manually selected

## 0.3.31
- better main path(possibly fixing "amnesia" bug)
- conda path fix for Linux
- support CUDA 12.8, try 12.8 if higher
  
## 0.3.30
- move use_note_rest to correct stage in advanced OU export
  
## 0.3.29
- fix reloading datasets during configuration
  
## 0.3.28
- add custom error when selecting samples so I don't have to explain ValueError every day

## 0.3.27
- fix OU exports only using first speaker for pitch
  
## 0.3.26
- multidict -> main

## 0.3.25
- added CUDA 12.4 to detection in setup
- redirect DiffSinger download to v2-backport backup

## 0.3.24
- moved set config edits to setup rather than configuration
  - now if you edit things like smooth_width in the default config files, it won't be overwritten the next time you save that config
 
## 0.3.23
- redirect DiffSinger download to main branch
- download pc-nsf-hifigan in addition to previous nsf-hifigan
- split breathiness/energy toggle
- added kitchen sink config

## 0.3.18
- automatic update will update core dependencies if needed
- configs come out in the same order they went in

## 0.3.17-ish
- QuickInference overhaul

## 0.3.14
- added config strings to match DiffSinger update(requires running update tools)
- updated langloader window
  - still uses langloader/merged.yaml, just has a nicer editor
  - it still usually pops up hidden behind the main window, sorry

## 0.3.13
- sorry I always forget to update this section
- there's probably a few changes that should be mentioned but I forgot
- should actually work on Linux/Mac now
- automates merging speakers in spk_map.json

## 0.3.0(multidict beta)
- new config format for multidict setup
- new settings files: langloader.yaml and merged.yaml
  - langloader: fixed file name/location. editable directly in DiffTrainer. lists dictionary files and global phonemes
  - merged: flexible file name/location(specified in langloader.yaml). lists groups of phonemes to merge

## 0.2.11
- automatic update will update dependencies if needed
- configs come out in the same order they went in

## 0.2.10
- automatic update will require editing the old version number to 0.2.0(sorry, won't be necessary again)
- revised basic OU export

## 0.2.4
- added backbone toggle(requires Diffsinger update 11/16/24)

## 0.2.1
- automated environment activation(environment names are now hardcoded, all users must use conda)

## 0.2.0
- started official changelog
- switch all users to conda or self-management
- implement split environments
- implement SOME for pitch estimation
- revert to main fork of Uta's converter
- CONVERTER: all labels MUST begin and end with [SP] (sorry for the inconvenience)
- switch default diff_accelerator to unipc
- implement advanced export(buggy)

# Changelog

## 0.3.14
- added config strings to match Diffsinger update(requires running update tools)
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
  - langloader: fixed file name/location. editable directly in difftrainer. lists dictionary files and global phonemes
  - merged: flexible file name/location(specified in langloader.yaml). lists groups of phonemes to merge
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

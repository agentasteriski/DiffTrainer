# Changelog

## 0.2.0
- started official changelog
- switch all users to conda or self-management
- implement split environments
- implement SOME for pitch estimation
- revert to main fork of Uta's converter
- CONVERTER: all labels MUST begin and end with [SP] (sorry for the inconvenience)
- switch default diff_accelerator to unipc
- implement advanced export(buggy)

## 0.3.0(multidict beta)
- new config format for multidict setup
- new settings files: langloader.yaml and merged.yaml
  - langloader: fixed file name/location. editable directly in difftrainer. lists dictionary files and global phonemes
  - merged: flexible file name/location(specified in langloader.yaml). lists groups of phonemes to merge

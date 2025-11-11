# EXPERIMENTAL BRANCH. IF THIS IS STILL HERE, USE AT YOUR OWN RISK
might have new bugs, might bring old bugs back bc I fixed them in the main branch and forgot to port it. don't bother complaining about them until this readme is gone.
## Current status: mostly de-Conda'd except for bats and setup
### Key features:
- moves most of the big functions into separate files
- generates base dsdicts that actually work most of the time(direct phoneme input only for non-G2P phonemizers)
### Known bugs:
- basic OU export just randomly fails to get some of the variables for no obvious reason(advanced seems to be fine)
### Goals:
- get liteconvert(in the files but unused) to work
- implement Ghin's segmenter instead
- ~~target Mix_LN branch due to single environment required~~
- un-Conda everything~~(much harder than it sounds)~~ (mostly done)
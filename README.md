# a CustomTkInter GUI for processing and training DiffSinger models (AMD / ROCm edition/Port)

(og made by agentasteriski: https://github.com/agentasteriski/DiffTrainer)
DiffTrainer brings together the most useful tools for DiffSinger in one easy, graphical package.
- [corpus_segmenter](https://github.com/MLo7Ghinsan/ghin_shenanigans/blob/main/scripts/corpus_segmenter.py) to shorten long wav/lab pairs
- [liteconvert](https://github.com/agentasteriski/liteconvert) for converting wav+lab data to wav/csv
- [SOME](https://github.com/openvpi/SOME) for estimating pitch
- [DiffSinger](https://github.com/openvpi/DiffSinger)'s primary training
- OpenUtau export scripts

> This edition is written for **AMD GPUs on Windows** using the ROCm stack. It uses a self-contained `venv` (Python 3.12 + PyTorch 2.9.1 for ROCm 7.2.1) instead of Conda. CUDA/NVIDIA instructions are not covered here.

# [News for existing users](https://github.com/agentasteriski/DiffTrainer/blob/main/ANNOUNCEMENT.md)

## > [!WARNING]
> **Always run the Update Tools button before using DiffTrainer.**
> DiffSinger, SOME, and the other bundled tools are downloaded separately and are NOT updated automatically. Starting preprocessing, binarization, or training with outdated tools can cause errors, incompatible model files, or silently wrong results.
> - After any fresh install, run **Update Tools** on the main tab to finish setup.
> - Whenever you update DiffTrainer, or after long periods without use, run **Update Tools** again before training.
> - Do not skip Update Tools just because training worked before — new data or config formats may require the latest tool versions.
>
> On this AMD edition, the launcher does NOT auto-check for updates, so it is up to you to run **Update Tools** manually.

### Requirements (AMD / Windows)
- AMD GPU supported by ROCm (Radeon RX 6000/7000 series or newer, or Instinct) with up-to-date AMD drivers
- [Python 3.12](https://www.python.org/downloads/) installed with the **Python launcher (`py`)** enabled
  - the setup script checks for `py -3.12`, so install from python.org and tick "Install launcher for all users"
  - Amd gpus With Pytorch support will most likely only work here

### Installation (AMD / Windows):
1. run `setup_amd.bat`
    - creates a `venv` in the project folder using Python 3.12 (skips if it already exists)
    - upgrades pip/setuptools/wheel
    - installs the **AMD ROCm SDK 7.2.1** wheels (large download, ~1.3 GB)
    - installs **PyTorch 2.9.1 + torchvision + torchaudio** built for ROCm 7.2.1 (large download, ~1.5 GB)
    - installs `requirements_win_amd.txt`
    - verifies the GPU at the end (`torch.cuda.is_available()` and device name should print your AMD card)
2. run `run_gui_amd.bat` to launch DiffTrainer
3. click **Update Tools** on the main tab to finish setup (do not skip - see warning above)
4. in future usage, just run `run_gui_amd.bat` again (always run **Update Tools** after updating DiffTrainer)

### Troubleshooting / Known issues:
- (Windows) PyTorch fails to extract during environment setup
    - try [enabling long paths](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=registry#enable-long-paths-in-windows-10-version-1607-and-later)
- if `setup_amd.bat` reports Python 3.12 not found, install it from python.org and make sure the `py` launcher is enabled, then rerun
- if the verification step fails to find the GPU, update your AMD drivers and confirm your card is ROCm-supported
- langloader editor sometimes hides behind main window
- if you type in the save interval or batch size boxes, an error appears in the terminal window
  - no actual impact, just enter your number and ignore it
- do not name checkpoint folders just "acoustic" or "variance", it conflicts with the onnx export cleanup
- if the OU export says "Acoustic/Variance/Duration ONNX export missing", you either selected the wrong checkpoint folder for that slot or never ran the **onnx** export for that model — use the acoustic/variance folder buttons so the export knows which model each folder contains

### Exporting a voicebank for OpenUtau (Export Singer)
DiffTrainer ships two OpenUtau export tabs: **Export Singer (basic)** (one acoustic + one combined variance model) and **Export Singer (advanced)** (acoustic + separate duration/variance/pitch folders).

**Before the OU export, both models must be exported to ONNX** using the **onnx** button on the ONNX export tab:
1. Pick the model type with the **aco/var** radio, then set the checkpoint folder.
2. The ONNX button now uses the folder you picked with the **Acoustic folder** / **Variance folder** buttons when they are set (falling back to the "Select checkpoint folder" picker otherwise), so exporting the wrong model type by accident is avoided. It prints `ONNX export using folder: ...` so you can always see which model is being exported.
3. After export, `dsconfig.yaml` is rewritten automatically to point at the renamed files (`acoustic.onnx`, `dur.onnx`, `phonemes.json`, ...), so the config is usable as-is — no manual editing.

**Then, in the Export Singer tab:**
- **Basic:** set the **Acoustic folder**, **Variance folder**, singer name, and **Save folder**, then click the export button.
- **Advanced:** set the **Acoustic folder**, **Duration folder**, and optionally **Variance** / **Pitch** folders (all three can point to the same ONNX-exported `checkpoints` folder when you did a combined variance export), plus singer name and **Save folder**.

Before writing anything, the export validates that the required `onnx` subfolders exist (`acoustic.onnx` for the acoustic folder, `dur.onnx`/`dsconfig.yaml` for the variance/duration folder). If a model was never ONNX-exported (or the wrong folder is selected) it prints a clear error and writes nothing, instead of producing a broken voicebank. Re-exporting into an existing singer folder is safe — all subfolders are created idempotently.

### What does "Binarize data" do?
Binarization is the mandatory preprocessing step between raw recordings and training. The GUI's **Binarize** button runs `DiffSinger\scripts\binarize.py` using the selected config (acoustic or variance).

For each raw dataset (`raw_data_dir` containing `wavs\*.wav` + `transcriptions.csv`, or `.ds` files when `prefer_ds` is set) it processes every utterance and:
- encodes the phoneme sequence to integer token ids and maps speakers/languages to ids
- turns phoneme durations from seconds into frame counts and builds the frame-to-phoneme alignment (`mel2ph`)
- extracts the sung f0 with the pitch extractor (RMVPE) and converts it to MIDI semitones
- builds the note sequence from `note_seq`/`note_dur`, interpolates rest notes and computes the smoothed base-pitch curve
- extracts the variance target features from the waveform via harmonic decomposition (`hnsep`): energy, breathiness, voicing, tension (whichever are enabled in the config)
- (acoustic model) computes the mel spectrogram as the acoustic target
- splits the items into train/valid sets using each dataset's `test_prefixes`

The result is written as binary indexed datasets into `binary_data_dir` (default `DiffSinger\checkpoints\binary`): `train.data` / `train.meta`, `valid.data` / `valid.meta`, plus `spk_map.json`, `lang_map.json`, the dictionary files and distribution plots. Training loads ONLY these binary files — not the raw wavs.

Notes:
- Re-run **Binarize** whenever you add/change recordings or transcriptions, or change config options that affect features (e.g. `predict_energy`, `f0_min`, `hop_size`, ...). Otherwise training silently reads stale binaries.
- Binarization is per-config-type: variance and acoustic produce different features, so their binary sets must not be mixed (training's backup logic guards against resuming an acoustic run with a variance config and vice versa).

### AMD .bat launchers
All AMD .bat files call the project's `venv` directly — no Conda is needed or used.

1. `setup_amd.bat`:
    - creates/repairs the `venv` and installs ROCm + PyTorch for AMD (see Installation above)
2. `run_gui_amd.bat`:
    - launches the DiffTrainer GUI from the `venv`
    - NOTE: unlike the CUDA launchers, it does not check for updates — run **Update Tools** yourself
3. `launch_tensorboard_amd.bat`:
    - launches TensorBoard pointed at the main checkpoints folder (`DiffSinger\checkpoints`)
    - shows everything merged into one run; use the two dedicated launchers below for a clean view
4. `launch_tensorboard_variance_amd.bat`:
    - builds a variance-only TensorBoard view and opens it on port 6006
    - first runs `make_tb_views.py variance`, then serves `DiffSinger\tb_views\variance`
    - shows just the variance run (`var_loss`, `energy_r2`, `breathiness_r2`, ...) without acoustic data mixed in
    - re-run after each training to pick up new runs
5. `launch_tensorboard_acoustic_amd.bat`:
    - builds an acoustic-only TensorBoard view and opens it on port 6007
    - first runs `make_tb_views.py acoustic`, then serves `DiffSinger\tb_views\acoustic`
    - note: the acoustic `.ckpt` backup folder (`DiffSinger\checkpoints_incompatible_ckpt_backup`) contains no event files; this view is built from the old acoustic event files still in `DiffSinger\checkpoints\lightning_logs\latest`
6. `run_quickinference_amd.bat`:
    - runs quickinference.py from the `venv`

`make_tb_views.py` (shared helper, no need to run manually): scans `DiffSinger\checkpoints\lightning_logs\latest`, classifies each TensorBoard event file by its tags (`var_loss` = variance, `mel_loss` = acoustic), and hard-links them into per-run subdirectories under `DiffSinger\tb_views\variance` / `DiffSinger\tb_views\acoustic`. Hard links mean the current training run updates live while old runs stay separated as their own TensorBoard experiments.

### Helper .bat files
- `set_max_steps.bat`: change `max_updates` (max training steps) in the training config without opening a text editor
    - `set_max_steps.bat 300000` → acoustic config
    - `set_max_steps.bat variance 80000` (or `set_max_steps.bat 80000 variance`) → variance config
    - `set_max_steps.bat` with no args → prompts for the value
- `view_phonemes.bat`: list and open the language phoneme dictionaries (`DiffSinger\dictionaries\*-phonemes.txt`) in Notepad for viewing/editing
    - pick a number to open one language, `A` to open all, `Q` to quit
- `DiffSinger\train_variance.bat`: variance training from a batch file (activates the `venv`, runs `scripts/train.py` with `configs\variance.yaml` into `checkpoints\variance`)
    - NOTE: train into a SEPARATE work dir from the acoustic model. The variance model has a different architecture and CANNOT resume an acoustic checkpoint (`model_ckpt_steps_*.ckpt`). `--reset` only resets hparams, NOT checkpoints, so a fresh exp_name is required.
- `DiffSinger\gen_notes.bat`: auto-generates `note_seq`/`note_dur` from the audio f0 contour (one note per phone)
    - this is a pitch-following approximation, NOT real musical score annotation. Variance training will run, but you will NOT get true note-level pitch control at inference — for that you still need real MIDI/score notes in `transcriptions.csv`.
import csv, os, pathlib, json
from decimal import Decimal
from math import isclose
from typing import Tuple, List
import librosa
import numpy as np
from tqdm import tqdm

from dt_modules.get_pitch import get_pitch

def csv2ds(transcription_file, wavs_folder, tolerance, hop_size, sample_rate, pe, ds_path):
    """Convert a transcription file to DS file"""
    wavs_folder = pathlib.Path(wavs_folder)
    assert wavs_folder.is_dir(), "wavs folder not found."
    out_ds = {}
    out_exists = []
    with open(transcription_file, "r", encoding="utf-8") as f:
        for trans_line in tqdm(csv.DictReader(f)):
            item_name = trans_line["name"]
            wav_fn = wavs_folder / f"{item_name}.wav"
            ds_fn = wavs_folder / f"{item_name}.ds"
            ph_dur = list(map(float, trans_line["ph_dur"].strip().split()))
            ph_num = list(map(int, trans_line["ph_num"].strip().split()))
            note_seq = trans_line["note_seq"].strip().split()
            note_dur = list(map(float, trans_line["note_dur"].strip().split()))
            note_glide = trans_line["note_glide"].strip().split() if "note_glide" in trans_line else None

            assert wav_fn.is_file(), f"{item_name}.wav not found."
            assert len(ph_dur) == sum(ph_num), "ph_dur and ph_num mismatch."
            assert len(note_seq) == len(note_dur), "note_seq and note_dur should have the same length."
            if note_glide:
                assert len(note_glide) == len(note_seq), "note_glide and note_seq should have the same length."
            assert isclose(
                sum(ph_dur), sum(note_dur), abs_tol=tolerance
            ), f"[{item_name}] ERROR: mismatch total duration: {sum(ph_dur) - sum(note_dur)}"

            # Resolve note_slur
            if "note_slur" in trans_line and trans_line["note_slur"]:
                note_slur = list(map(int, trans_line["note_slur"].strip().split()))
            else:
                note_seq, note_dur, note_slur = align_notes_to_words(
                    ph_dur, ph_num, note_seq, note_dur, tol=tolerance
                )
            # Extract f0_seq
            wav, _ = librosa.load(wav_fn, sr=sample_rate, mono=True)
            # length = len(wav) + (win_size - hop_size) // 2 + (win_size - hop_size + 1) // 2
            # length = ceil((length - win_size) / hop_size)
            f0_timestep, f0, _ = get_pitch(pe, wav, hop_size, sample_rate, ds_path)
            ds_content = [
                {
                    "offset": 0.0,
                    "text": trans_line["ph_seq"],
                    "ph_seq": trans_line["ph_seq"],
                    "ph_dur": " ".join(str(round(d, 6)) for d in ph_dur),
                    "ph_num": trans_line["ph_num"],
                    "note_seq": " ".join(note_seq),
                    "note_dur": " ".join(str(round(d, 6)) for d in note_dur),
                    "note_slur": " ".join(map(str, note_slur)),
                    "f0_seq": " ".join(map("{:.1f}".format, f0)),
                    "f0_timestep": str(f0_timestep),
                }
            ]
            if note_glide:
                ds_content[0]["note_glide"] = " ".join(note_glide)
            out_ds[ds_fn] = ds_content
            if ds_fn.exists():
                out_exists.append(ds_fn)
    for ds_fn, ds_content in out_ds.items():
            with open(ds_fn, "w", encoding="utf-8") as f:
                json.dump(ds_content, f, ensure_ascii=False, indent=4)

def align_notes_to_words(
        ph_dur: List[float], ph_num: List[int], note_seq: List[str], note_dur: List[float], tol: float = 0.01
) -> Tuple[List[str], List[float], List[int]]:
    idx = 0
    word_dur = []
    for num in ph_num:
        word_dur.append(sum(ph_dur[idx:idx + num]))
        idx += num
    word_start = np.cumsum([0.0] + word_dur[:-1])
    word_end = np.cumsum(word_dur)
    note_start = np.cumsum([0.0] + note_dur[:-1])
    note_end = np.cumsum(note_dur)
    new_note_seq = []
    new_note_dur = []
    note_slur = []
    for word_idx in range(len(word_dur)):
        # find the closest note start
        note_start_idx = np.argmin(np.abs(note_start - word_start[word_idx]))
        if word_start[word_idx] < note_start[note_start_idx] - tol:
            note_start_idx = max(0, note_start_idx - 1)
        # find the closest note end
        note_end_idx = np.argmin(np.abs(note_end[note_start_idx:] - word_end[word_idx])) + note_start_idx
        if word_end[word_idx] > note_end[note_end_idx] + tol:
            note_end_idx = min(len(note_end) - 1, note_end_idx + 1)
        # adjust note sequence and durations to fit the word duration
        word_note_seq = []
        word_note_dur = []
        for note_idx in range(note_start_idx, note_end_idx + 1):
            # adjust note start
            if note_idx == note_start_idx:
                start = word_start[word_idx]
            else:
                start = note_start[note_idx]
            # adjust note end
            if note_idx == note_end_idx:
                end = word_end[word_idx]
            else:
                end = note_end[note_idx]
            if word_note_seq and word_note_seq[-1] == note_seq[note_idx]:
                # same note as previous, merge durations
                word_note_dur[-1] += (end - start)
            else:
                word_note_seq.append(note_seq[note_idx])
                word_note_dur.append(end - start)
        new_note_seq.extend(word_note_seq)
        new_note_dur.extend(word_note_dur)
        note_slur.extend([0] + [1] * (len(word_note_seq) - 1))
    return new_note_seq, new_note_dur, note_slur

if __name__ == "__main__":
    csv2ds("C:/Users/megdo/Documents/GitHub/DiffTrainer/raw_data/fixes_segmented/05OPEN.ja/transcriptions.csv", "C:/Users/megdo/Documents/GitHub/DiffTrainer/raw_data/fixes_segmented/05OPEN.ja/wavs", 0.01, 512, 44100, "rmvpe", "C:/Users/megdo/Documents/GitHub/DiffTrainer/DiffSinger")
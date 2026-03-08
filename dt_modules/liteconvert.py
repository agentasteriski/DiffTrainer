import os, csv, json, shutil
import numpy as np
from pathlib import Path

def auto_config(base_path):
    base_dir = Path(base_path)

    phonemes = set()
    def is_excluded(phoneme):
        return phoneme in ["pau", "AP", "SP", "sil"]
    
    for lab_file in base_dir.rglob("*.lab"):
        if any(part.startswith('.') for part in lab_file.parts):
            continue
            
        with open(lab_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    phoneme = parts[2]
                    if not is_excluded(phoneme):
                        phonemes.add(phoneme)
    
    vowel_types = {"a", "i", "u", "e", "o", "N", "M", "NG", "A", "E", "I", "O", "U"}
    liquid_types = {"y", "w", "l", "r"} # liquids and semivowels
    vowel_data = []
    liquid_data = []

    for phoneme_raw in phonemes:
        if "/" in phoneme_raw:
            # Split on '/', take the second half
            phoneme = phoneme_raw.split("/")[1] 
        else:
            # Use the phoneme as is
            phoneme = phoneme_raw
            
        # Sort by short name but add full name to list
        if phoneme[0] in vowel_types:
            vowel_data.append(phoneme_raw)
        elif phoneme[0] in liquid_types:
            liquid_data.append(phoneme_raw)
        else:
            continue
    vowel_data.sort()
    liquid_data.sort()

    liquid_list = {liquid: True for liquid in liquid_data}
    phones4json = {"vowels": vowel_data, "liquids": liquid_list}
    jsonpath = base_dir / "auto_lang_config.json"
    #print(f"Attempting to write to: {jsonpath.absolute()}")
    with open(jsonpath, "w", encoding = "utf-8") as langconfig:
        json.dump(phones4json, langconfig, indent=4)

def read_lab_file(lab_path):
    """Read a .lab file and return phoneme sequences and durations"""
    ph_seq = []
    ph_durs = []

    nnsvsbegone = {
        "br": "AP",
        "pau": "SP",
        "sil": "SP"
    }
    
    with open(lab_path, 'r', encoding = "utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) >= 3:
                # correctly formatted labs go: start_time end_time phoneme
                start_time = int(parts[0])
                end_time = int(parts[1])
                phoneme = parts[2]

                phoneme = nnsvsbegone.get(phoneme, phoneme)

                s = float(start_time) / 10000000
                e = float(end_time) / 10000000

                duration = round((e - s), 12)
                
                ph_seq.append(phoneme)
                ph_durs.append(str(duration))
    
    return ' '.join(ph_seq), ' '.join(ph_durs)

def phoneme_separation(ph_seq, langconfig):
    #this is pretty much from nnsvs_db_converter just adapted to take the phonemes in a slightly different format
    pauses = ['sil', 'pau', 'SP']
    vowel_pos = []
    ph_list = ph_seq.split()
    with open(langconfig) as f:
        lang = json.load(f)
    
    # 1. Identify if the first group starts at index 0 (if the first phoneme is a consonant)
    if ph_list[0] not in pauses + lang['vowels'] + ['br', 'AP']:
        vowel_pos.append(0)

    # 2. Iterate through phonemes to find group boundaries
    for i in range(len(ph_list)):
        p = ph_list[i]
        
        # If it's a vowel, it might be the start of a group
        if p in lang['vowels']:
            # Check for liquids(and semivowels) immediately before the vowel
            if i > 0 and ph_list[i-1] in lang['liquids'].keys():
                liquid_rule = lang['liquids'][ph_list[i-1]]
                
                # If the rule is True or the preceding consonant matches the rule, move the split point back to include the liquid
                if i > 1 and (liquid_rule is True or ph_list[i-2] in liquid_rule):
                    if ph_list[i-2] not in pauses + lang['vowels']:
                        vowel_pos.append(i-1)
                    else:
                        vowel_pos.append(i)
                else:
                    vowel_pos.append(i)
            else:
                vowel_pos.append(i)
        
        # Pauses and breaths always start their own group
        elif p in pauses + ['br', 'AP']:
            vowel_pos.append(i)

    # 3. Add the end boundary to close the last group
    vowel_pos.append(len(ph_list))

    # 4. Use np.diff to find the count of phonemes in each group
    vowel_pos = sorted(list(set(vowel_pos)))
    ph_num = np.diff(vowel_pos)
    
    return ' '.join(map(str, ph_num))

def lab2csv(base_path, langconfig):
    """Iterates through subfolders and creates one CSV for each containing .lab files"""

    base_dir = Path(base_path)
    speaker_labs = {}

    for lab_file in base_dir.rglob('*.lab'):
        # If the file is inside a "lab" subfolder, the speaker dir is one level up
        if lab_file.parent.name == 'lab':
            speaker_dir = lab_file.parent.parent
        else:
            speaker_dir = lab_file.parent

        # Skip if we are accidentally looking inside an already processed 'wavs' output folder
        if speaker_dir.name == 'wavs' or lab_file.parent.name == 'wavs':
            continue

        if speaker_dir not in speaker_labs:
            speaker_labs[speaker_dir] = []
        speaker_labs[speaker_dir].append(lab_file)

    for speaker_dir, lab_files in speaker_labs.items():
        wavs_dir = speaker_dir / "wavs"
        wavs_dir.mkdir(parents=True, exist_ok=True)
        
        lab_files.sort(key=lambda x: x.name)

        output_csv = speaker_dir / "transcriptions.csv"

        print(f"Processing speaker {speaker_dir.name}")

        with open(output_csv, 'w', newline='', encoding="utf-8") as csvfile:
            fieldnames = ['name', 'ph_seq', 'ph_dur', 'ph_num']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for lab_file in lab_files:
                try:
                    if lab_file.parent.name == 'lab': #vlabeler format
                        wav_file = speaker_dir / 'wav' / f"{lab_file.stem}.wav"
                    else:
                        wav_file = lab_file.with_suffix('.wav') #nnsvs_db_converter format

                    if not wav_file.exists():
                        print(f"Warning: No matching .wav file found for {lab_file}")
                        continue
                    
                    ph_seq, ph_durs = read_lab_file(lab_file)
                    ph_num = phoneme_separation(ph_seq, langconfig)
                    
                    writer.writerow({
                        'name': lab_file.stem,
                        'ph_seq': ph_seq,
                        'ph_dur': ph_durs,
                        'ph_num': ph_num
                    })
                    
                    shutil.move(str(lab_file), str(wavs_dir / lab_file.name))
                    shutil.move(str(wav_file), str(wavs_dir / wav_file.name))

                except Exception as e:
                    print(f"Error in {lab_file.name}: {e}")
            
            for subfolder_name in ['lab', 'wav']:
                subfolder_path = speaker_dir / subfolder_name
                if subfolder_path.exists() and subfolder_path.is_dir():
                    if not any(subfolder_path.iterdir()):
                        subfolder_path.rmdir()
    print("Converted all speakers to DiffSinger format!")


if __name__ == "__main__":
    # to use auto-config: comment out first langconfig line, un-comment second one and auto_config line
    base_path = "C:/Users/AAAAA/Documents/GitHub/DiffTrainer/raw_data/big_test"
    langconfig = "insert_path_here"
    #langconfig = os.path.join(base_path, "auto_lang_config.json") 
    
    #auto_config(base_path)
    lab2csv(base_path, langconfig)
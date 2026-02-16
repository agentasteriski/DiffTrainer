#doesn't work yet, difftrainer.py still uses uta's contraption
import csv, json
import soundfile as sf
import numpy as np
from pathlib import Path

def read_lab_file(lab_path, fs):
    """Read a .lab file and return phoneme sequences and durations"""
    ph_seq = []
    ph_durs = []
    
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

def process_wav_lab_pairs(base_path, output_csv, langconfig):
    """Process all .wav and .lab pairs in the base path"""
    
    # Find all .lab files
    lab_files = list(Path(base_path).glob('**/*.lab'))
    lab_files.sort(key=lambda x: x.name)
    
    # Prepare CSV file
    with open(output_csv, 'w', newline='', encoding = "utf-8") as csvfile:
        fieldnames = ['name', 'ph_seq', 'ph_dur', 'ph_num']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for lab_file in lab_files:
            try:
                # Find corresponding .wav file
                wav_file = lab_file.with_suffix('.wav')
                
                if not wav_file.exists():
                    print(f"Warning: No matching .wav file found for {lab_file}")
                    continue
                
                # Read audio to get sample rate
                x, fs = sf.read(wav_file)
                
                # Read phoneme information from .lab file
                ph_seq, ph_durs = read_lab_file(lab_file, fs)
                ph_num = phoneme_separation(ph_seq, langconfig)

                basename = lab_file.stem
                
                # Write to CSV
                writer.writerow({
                    'name': f'{basename}',
                    'ph_seq': ph_seq,
                    'ph_dur': ph_durs,
                    'ph_num': ph_num
                })
                
                print(f"Processed: {basename}")
                
            except Exception as e:
                print(f"Error processing {lab_file}: {e}")

# Edit this for standalone usage
if __name__ == "__main__":
    base_path = "C:/Users/AAAAA/Documents/GitHub/DiffTrainer/raw_data/test"
    output_csv = "output_transcription.csv" #only does the csv, folder reorganizing is up to you
    langconfig = "exampleconfig.json"
    
    process_wav_lab_pairs(base_path, output_csv, langconfig)
    print(f"CSV file created: {output_csv}")

#doesn't work yet, difftrainer.py still uses uta's contraption
import os
import csv
import soundfile as sf
import numpy as np
from pathlib import Path

def read_lab_file(lab_path, fs):
    """Read a .lab file and return phoneme sequences and durations"""
    ph_seq = []
    ph_durs = []
    
    with open(lab_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) >= 3:
                # Format: start_time end_time phoneme
                start_time = int(parts[0])
                end_time = int(parts[1])
                phoneme = parts[2]
                s = float(start_time) / 10000000
                e = float(end_time) / 10000000

                # Convert time from samples to seconds and calculate duration
                duration = (e - s) / fs
                
                ph_seq.append(phoneme)
                ph_durs.append(str(duration))
    
    return ' '.join(ph_seq), ph_durs

def process_wav_lab_pairs(base_path, output_csv):
    """Process all .wav and .lab pairs in the base path"""
    
    # Find all .lab files
    lab_files = list(Path(base_path).glob('**/*.lab'))
    lab_files.sort(key=lambda x: x.name)
    
    # Prepare CSV file
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['name', 'ph_seq', 'ph_dur']
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
                
                # Write to CSV
                writer.writerow({
                    'name': lab_file.stem,
                    'ph_seq': ph_seq,
                    'ph_dur': ' '.join(ph_durs)
                })
                
                print(f"Processed: {lab_file.stem}")
                
            except Exception as e:
                print(f"Error processing {lab_file}: {e}")

# Usage
if __name__ == "__main__":
    # Set your base path here
    base_path = "C:/Users/AAAAA/Documents/DiffTrainer-main/raw_data/seven"
    output_csv = "output_transcription.csv"
    
    process_wav_lab_pairs(base_path, output_csv)
    print(f"CSV file created: {output_csv}")

# straight up by ghin from https://github.com/MLo7Ghinsan/ghin_shenanigans/blob/main/scripts/corpus_segmenter.py
import soundfile as sf
import os
import numpy as np

pause_phonemes = ["pau", "sil", "SP"]
breath_phonemes = ["AP", "bre"]
all_pause_phonemes = pause_phonemes + breath_phonemes
report_path = "report.txt"

# i just found out about these and holy shit im using them they're so slay
yellow = "\033[93m"
cyan = "\033[96m"
green = "\033[92m"
reset = "\033[0m"



# slay information to write as txt later so ppl dont have to check it themselves <3
total_segments = 0
total_removed_segments = 0
total_skipped_files = 0
total_audio_duration = 0
valid_segments_count = 0
max_silence_length = 0.25
subfolder_reports = []

def load_lab(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    lab_data = []
    for line in lines:
        start, end, phoneme = line.strip().split()
        lab_data.append((int(start), int(end), phoneme))
    return lab_data

def fade(audio_segment, sample_rate, pause_start, pause_end, fade_type="in"):
    pause_length = pause_end - pause_start
    fade_half_length = pause_length // 2

    if pause_length <= 0 or fade_half_length <= 0:
        return
        
    if pause_start < 0 or pause_end > len(audio_segment):
        return
        
    if fade_type == "in":
        audio_segment[pause_start:pause_start + fade_half_length] = 0
        fade_in_samples = np.linspace(0, 1, pause_end - (pause_start + fade_half_length))
        target_length = min(len(audio_segment[pause_start + fade_half_length:pause_end]), len(fade_in_samples))
        audio_segment[pause_start + fade_half_length:pause_start + fade_half_length + target_length] *= fade_in_samples[:target_length]
    elif fade_type == "out":
        fade_out_samples = np.linspace(1, 0, fade_half_length)
        target_length = min(len(audio_segment[pause_start:pause_start + fade_half_length]), len(fade_out_samples))
        audio_segment[pause_start:pause_start + target_length] *= fade_out_samples[:target_length]
        audio_segment[pause_start + fade_half_length:pause_end] = 0

# to check for longest audio cus sometimes it'd be too long
def find_longest_seg(folder_path):
    longest_file = None
    longest_duration = 0

    for file in os.listdir(folder_path):
        if file.endswith(".wav"):
            file_path = os.path.join(folder_path, file)
            audio, sample_rate = sf.read(file_path)
            duration = len(audio) / sample_rate
            if duration > longest_duration:
                longest_duration = duration
                longest_file = file_path

    return longest_file, longest_duration

# fun part
def segment_audio_and_labels(wav_path, lab_path, output_folder, max_length_sec):
    global total_segments, total_removed_segments, total_audio_duration, valid_segments_count

    audio, sample_rate = sf.read(wav_path)
    max_samples = int(max_length_sec * sample_rate)
    lab_data = load_lab(lab_path)

    segments = []
    current_segment = []
    current_length = 0
    segment_start_time = 0

    for start, end, phoneme in lab_data:
        duration = int((end - start) * sample_rate / 1e7)

        if phoneme in all_pause_phonemes and current_length + duration >= max_samples:
            if current_segment:
                if current_segment[-1][2] not in all_pause_phonemes:
                    current_segment.append((start, end, phoneme))
            segments.append((segment_start_time, current_segment))

            current_segment = [(start, end, phoneme)]
            current_length = duration
            segment_start_time = start
        else:
            current_segment.append((start, end, phoneme))
            current_length += duration

    if current_segment:
        if current_segment[-1][2] != all_pause_phonemes:
            current_segment.append(current_segment[-1])
        segments.append((segment_start_time, current_segment))

    base_filename = os.path.splitext(os.path.basename(wav_path))[0]
    print(f"File '{base_filename}.wav|.lab' has been separated into {len(segments)} segments.")

    for i, (segment_start_time, segment) in enumerate(segments):

        if not segment:
            continue

        # for trimming silence
        first_p_start, first_p_end, first_p_phn = segment[0]
        first_p_dur_s = (first_p_end - first_p_start) / 1e7
        if first_p_phn in pause_phonemes and first_p_dur_s > max_silence_length:
            new_start = first_p_end - int(max_silence_length * 1e7)
            segment[0] = (new_start, first_p_end, first_p_phn)

        last_p_start, last_p_end, last_p_phn = segment[-1]
        last_p_dur_s = (last_p_end - last_p_start) / 1e7
        if last_p_phn in pause_phonemes and last_p_dur_s > max_silence_length:
            new_end = last_p_start + int(max_silence_length * 1e7)
            segment[-1] = (last_p_start, new_end, last_p_phn)

        new_seg_start_time = segment[0][0]
        new_seg_end_time = segment[-1][1]

        seg_start_sample = int(new_seg_start_time * sample_rate / 1e7)
        seg_end_sample = int(new_seg_end_time * sample_rate / 1e7)
        seg_end_sample = min(seg_end_sample, len(audio))
        
        segment_audio = np.copy(audio[seg_start_sample:seg_end_sample])

        # doing fade in-out to prevent the choking sound in silence phonemes- you are WELCOME
        # doing 0.1 (10%) on fade amount for breath to not reduce too much details....
        segment_start_time = new_seg_start_time
        
        if segment[0][2] in pause_phonemes:
            first_pause_start = int((segment[0][0] - segment_start_time) * sample_rate / 1e7)
            first_pause_end = int((segment[0][1] - segment_start_time) * sample_rate / 1e7)
            fade(segment_audio, sample_rate, first_pause_start, first_pause_end, fade_type = "in")
        elif segment[0][2] in breath_phonemes:
            first_breath_start = int((segment[0][0] - segment_start_time) * sample_rate / 1e7)
            first_breath_end = int((segment[0][1] - segment_start_time) * sample_rate / 1e7)
            breath_length = first_breath_end - first_breath_start
            fade_length = int(0.1 * breath_length)
            fade(segment_audio, sample_rate, first_breath_start, first_breath_start + fade_length, fade_type="in")

        if segment[-1][2] in pause_phonemes:
            last_pause_start = int((segment[-1][0] - segment_start_time) * sample_rate / 1e7)
            last_pause_end = int((segment[-1][1] - segment_start_time) * sample_rate / 1e7)
            fade(segment_audio, sample_rate, last_pause_start, last_pause_end, fade_type = "out")
        elif segment[-1][2] in breath_phonemes:
            last_breath_start = int((segment[-1][0] - segment_start_time) * sample_rate / 1e7)
            last_breath_end = int((segment[-1][1] - segment_start_time) * sample_rate / 1e7)
            breath_length = last_breath_end - last_breath_start
            fade_length = int(0.1 * breath_length)
            fade(segment_audio, sample_rate, last_breath_end - fade_length, last_breath_end, fade_type="out")

        #adding SP to the start and end if its breath phoneme
        silence_samples = int(max_silence_length * sample_rate)
        silence_audio = np.zeros(silence_samples, dtype=audio.dtype)

        if segment[0][2] in breath_phonemes:
            segment_audio = np.concatenate((silence_audio, segment_audio))
            for j in range(len(segment)):
                start, end, phoneme = segment[j]
                segment[j] = (start + int(max_silence_length * 1e7), end + int(max_silence_length * 1e7), phoneme)
            new_first = (segment_start_time, segment_start_time + int(max_silence_length * 1e7), "SP")
            segment.insert(0, new_first)

        if segment[-1][2] in breath_phonemes:
            segment_audio = np.concatenate((segment_audio, silence_audio))
            new_last = (segment[-1][1], segment[-1][1] + int(max_silence_length * 1e7), "SP")
            segment.append(new_last)
            
        cleaned_segment = []
        for i, ph in enumerate(segment):
            if i > 0 and ph[2] == "SP" and segment[i - 1][2] == "SP" and ph[0] == segment[i - 1][0] and ph[1] == segment[i - 1][1]:
                continue  # skip duplicate
            cleaned_segment.append(ph)
        segment = cleaned_segment
        
        seg_wav_path = os.path.join(output_folder, f"{base_filename}_seg{i+1}.wav")
        sf.write(seg_wav_path, segment_audio, sample_rate)
        
        seg_lab_path = os.path.abspath(os.path.join(output_folder, f"{base_filename}_seg{i+1}.lab"))
        with open(seg_lab_path, "w") as seg_lab_file:
            for start, end, phoneme in segment:
                new_start = start - segment_start_time
                new_end = end - segment_start_time
                seg_lab_file.write(f"{new_start} {new_end} {phoneme}\n")

        total_segments += 1
        segment_duration = len(segment_audio) / sample_rate
        total_audio_duration += segment_duration
        valid_segments_count += 1

    removed_segments = 0
    for i in range(1, len(segments) + 1):
        seg_lab_path = os.path.join(output_folder, f"{base_filename}_seg{i}.lab")
        seg_wav_path = os.path.join(output_folder, f"{base_filename}_seg{i}.wav")
        if not os.path.exists(seg_lab_path):
            continue
        segment_data = load_lab(seg_lab_path)
        
        if all(phoneme in all_pause_phonemes for _, _, phoneme in segment_data):
            os.remove(seg_lab_path)
            os.remove(seg_wav_path)
            total_removed_segments += 1
            removed_segments += 1
            valid_segments_count -= 1
            print(f"Removed segment {i} with only pause phoneme for '{base_filename}.wav|.lab'.")

# for both folders and wav|lab that are in the folder
def process_folder(input_folder, output_folder, max_length_sec, report_path):
    os.makedirs(output_folder, exist_ok=True)
    global total_skipped_files, subfolder_reports
    
    processed_files = set()

    for root, dirs, files in os.walk(input_folder):
        folder_name = os.path.basename(root)
        is_split_folder = folder_name.lower() in ["wav", "lab"]
        
        relative_path = os.path.relpath(root, input_folder)
        output_subfolder = os.path.join(output_folder, relative_path)
        
        if is_split_folder:
            target_output = os.path.dirname(output_subfolder) #redirect to speaker level
        else:
            target_output = output_subfolder

        folder_segments = 0
        skipped_count = 0

        removed_at_start = total_removed_segments #segments counted in previous speakers

        for filename in files:
            if filename.endswith(".wav"):
                base_name = os.path.splitext(filename)[0]
                wav_path = os.path.join(root, filename)
                
                lab_path_same = os.path.join(root, f"{base_name}.lab")
                
                parent_dir = os.path.dirname(root)
                final_lab_path = None
                
                if os.path.exists(lab_path_same):
                    final_lab_path = lab_path_same #nnsvs_db_converter style
                else: #VLabeler style
                    for sibling in os.listdir(parent_dir):
                        if sibling.lower() == "lab":
                            potential_lab = os.path.join(parent_dir, sibling, f"{base_name}.lab")
                            if os.path.exists(potential_lab):
                                final_lab_path = potential_lab
                                break

                if final_lab_path:
                    file_key = os.path.abspath(wav_path)
                    if file_key in processed_files:
                        continue
                    
                    os.makedirs(target_output, exist_ok=True)
                    segments_before = total_segments
                    segment_audio_and_labels(wav_path, final_lab_path, target_output, max_length_sec)
                    folder_segments += (total_segments - segments_before)
                    processed_files.add(file_key)
                else:
                    skipped_count += 1
                    total_skipped_files += 1
                    print(f"No equivalent .lab to {filename}.wav, skipping it....")

        if folder_segments > 0:
            longest_file, longest_dur = find_longest_seg(target_output)
            subfolder_reports.append({
                "folder": os.path.relpath(target_output, output_folder),
                "segments_created": folder_segments,
                "segments_removed": total_removed_segments - removed_at_start,
                "files_skipped": skipped_count,
                "longest_audio_file": longest_file,
                "longest_audio_duration": longest_dur
            })

    with open(report_path, "w") as report_file:
        for report in subfolder_reports:
            report_file.write(f"Folder: {report['folder']}\n")
            report_file.write(f"  Segments created: {report['segments_created']}\n")
            report_file.write(f"  Segments removed: {report['segments_removed']}\n")
            report_file.write(f"  Files skipped: {report['files_skipped']}\n")
            report_file.write(f"  Longest audio file: {report['longest_audio_file']}\n")
            report_file.write(f"  Duration of longest audio file: {int(report['longest_audio_duration'])} seconds\n\n")
            
        report_file.write(f"Total segments created: {total_segments}\n")
        report_file.write(f"Total removed segments: {total_removed_segments}\n")
        report_file.write(f"Total valid segments: {valid_segments_count}\n")
        report_file.write(f"Total skipped files: {total_skipped_files}\n")
        report_file.write(f"Total audio duration of valid segments: {int(total_audio_duration)} seconds\n")

    print(f"Segmentation complete! Saved report as {report_path}")



def main():
    print(f"{yellow}!!!~Welcome to Corpus Segmenter~!!!\n")
    print(f"{cyan}This is a little tool for segmenting your labeled corpus as the name suggest.\n")
    print(f"Supporting label format: HTK label (.lab)\n")
    print(f"The phonemes that will be accountable for {green}silence {cyan}phonemes accounted for segmentation are {green}{pause_phonemes}\n")
    print(f"{cyan}The phonemes that will be accountable for {green}breath {cyan}phonemes accounted for segmentation are {green}{breath_phonemes}\n")
    print(f"{cyan}This tool will not segment exactly on the inputted maximum segment length,\n")
    print(f"the logic of segmenting is based on the closest {green}silence and breath {cyan}phoneme to that value.{reset}\n")
    print("|\n")
    print("|\n")
    print("|\n")
    input_folder = input("Enter the path to the input folder: ")
    output_folder = input("Enter the path to the output folder: ")
    max_length_sec = float(input("Enter the maximum segment length in seconds: "))
    
    process_folder(input_folder, output_folder, max_length_sec, report_path)

if __name__ == "__main__":
    main()
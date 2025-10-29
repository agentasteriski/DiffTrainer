import os, glob, yaml

def dictgenerator(aco_folder_dir, main_stuff):
    aco_folder_onnx = os.path.join(aco_folder_dir, "onnx")
    phoneme_types_list = {
        "a": "vowel", "i": "vowel", "u": "vowel", "e": "vowel", "o": "vowel",
        "b": "stop", "d": "stop", "g": "stop", "k": "stop", "p": "stop", "q": "stop", "t": "stop",
        "c": "affricate", "j": "affricate",
        "f": "fricative", "h": "fricative", "s": "fricative", "v": "fricative", "z": "fricative",
        "l": "liquid", "r": "liquid",
        "m": "nasal", "n": "nasal",
        "w": "semivowel", "y": "semivowel",
    }
    ou_canon_languages = {"zh", "en", "de", "it", "ja", "yue", "ko", "pt", "ru", "es"}

    lang_dictionary_files = glob.glob(os.path.join(aco_folder_onnx, "*.txt"))
    print("Dictionary files found:", [os.path.basename(dict_name) for dict_name in lang_dictionary_files])
    
    training_config = os.path.join(aco_folder_dir, "config.yaml")
    with open(training_config, "r", encoding="utf-8") as extrasource:
        config = yaml.safe_load(extrasource)
        extra_phonemes = config.get("extra_phonemes", [])
    print(f"Found {len(extra_phonemes)} extra phonemes")

    language_specific_phonemes = {}
    general_phonemes = []
    
    for phoneme in extra_phonemes:
        if "/" in phoneme: # Check for language prefix
            lang_code, basephoneme = phoneme.split("/")
            if lang_code not in language_specific_phonemes:
                language_specific_phonemes[lang_code] = []
            language_specific_phonemes[lang_code].append(basephoneme)
        else:
            if phoneme != 'AP' and phoneme != 'SP' and 'trash' not in str(phoneme): #AP/SP readded manually later, trash gets trashed
                general_phonemes.append(phoneme)

    # Check if there's only one dictionary file
    if len(lang_dictionary_files) == 1:
        dictionary_file = lang_dictionary_files[0]
        dictionary_ext = os.path.basename(dictionary_file).split("-")[1].split(".")[0]

        symbols = []
        entries = []
        
        for phoneme in general_phonemes:
            phoneme_type = phoneme_types_list.get(phoneme[0], "stop")
            symbol_entry = {"symbol": phoneme, "type": phoneme_type}
            entry_entry = {"grapheme": phoneme, "phonemes": [phoneme]} 

            symbols.append(symbol_entry)
            entries.append(entry_entry)
        
        with open(dictionary_file, "r", encoding="utf-8") as f:
            for line in f:
                phoneme = line.strip().split()[0]
                phoneme_type = phoneme_types_list.get(phoneme[0], "stop")
                symbol_entry = {"symbol": phoneme, "type": phoneme_type}
                entry_entry = {"grapheme": phoneme, "phonemes": [phoneme]} 

                symbols.append(symbol_entry)
                entries.append(entry_entry)
        
        out_path = os.path.join(main_stuff, f"dsdict.yaml")
        print(f"Writing file: dsdict.yaml with {len(symbols)} entries")
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write("symbols:\n")
            out_f.write('- {symbol: SP, type: vowel}\n')
            out_f.write('- {symbol: AP, type: vowel}\n')
            for item in symbols:
                out_f.write(f"- {{symbol: {item['symbol']}, type: {item['type']}}}\n")
            out_f.write("\nentries:\n")
            for item in entries:
                out_f.write(f"- {{grapheme: \"{item['grapheme']}\", phonemes: [\"{item['phonemes'][0]}\"]}}\n")
            out_f.write('- {grapheme: "SP", phonemes: [SP]}\n')
            out_f.write('- {grapheme: "AP", phonemes: [AP]}\n')

    else:  # Original logic for multiple files
        all_symbols = []
        all_entries = []

        for phoneme in general_phonemes:
            phoneme_type = phoneme_types_list.get(phoneme[0], "stop")
            symbol_entry = {"symbol": phoneme, "type": phoneme_type}
            entry_entry = {"grapheme": phoneme, "phonemes": [phoneme]} 

            all_symbols.append(symbol_entry)
            all_entries.append(entry_entry)

        # First, accumulate all symbols from all dictionaries
        for dictionary_file in lang_dictionary_files:
            dictionary_ext = os.path.basename(dictionary_file).split("-")[1].split(".")[0]

            with open(dictionary_file, "r", encoding="utf-8") as f:
                for line in f:
                    phoneme = line.strip().split()[0]
                    phoneme_type = phoneme_types_list.get(phoneme[0], "stop")
                    symbol_entry = {"symbol": f"{dictionary_ext}/{phoneme}", "type": phoneme_type}
                    entry_entry = {"grapheme": phoneme, "phonemes": [f"{dictionary_ext}/{phoneme}"]}

                    all_symbols.append(symbol_entry) 
                    all_entries.append(entry_entry)
            
            if dictionary_ext in language_specific_phonemes:
                for phoneme in language_specific_phonemes[dictionary_ext]:
                    phoneme_type = phoneme_types_list.get(phoneme[0], "stop")
                    symbol_entry = {"symbol": f"{dictionary_ext}/{phoneme}", "type": phoneme_type}
                    entry_entry = {"grapheme": phoneme, "phonemes": [f"{dictionary_ext}/{phoneme}"]}
                    
                    all_symbols.append(symbol_entry) 
                    all_entries.append(entry_entry)
        
        # Now, write each dsdict-[dictionary_ext].yaml file
        for dictionary_file in lang_dictionary_files:
            dictionary_ext = os.path.basename(dictionary_file).split("-")[1].split(".")[0]

            symbols = []
            replacements = []
            entries = []

            with open(dictionary_file, "r", encoding="utf-8") as f:
                for line in f:
                    phoneme = line.strip().split()[0]
                    phoneme_type = phoneme_types_list.get(phoneme[0], "stop")
                    symbol_entry = {"symbol": f"{dictionary_ext}/{phoneme}", "type": phoneme_type}
                    replacement_entry = {"from": phoneme, "to": f"{dictionary_ext}/{phoneme}"}
                    entry_entry = {"grapheme": phoneme, "phonemes": [f"{dictionary_ext}/{phoneme}"]}

                    symbols.append(symbol_entry)
                    replacements.append(replacement_entry)
                    entries.append(entry_entry)


            out_path = os.path.join(main_stuff, f"dsdict-{dictionary_ext}.yaml")
            print(f"Writing file: dsdict-{dictionary_ext}.yaml with {len(symbols)} entries")
            with open(out_path, "w", encoding="utf-8") as out_f:
                out_f.write("symbols:\n")
                out_f.write('- {symbol: SP, type: vowel}\n')
                out_f.write('- {symbol: AP, type: vowel}\n')
                for item in all_symbols:  # should be able to pull phonemes from all langs if directly input
                    out_f.write(f"- {{symbol: {item['symbol']}, type: {item['type']}}}\n")
                if dictionary_ext not in ou_canon_languages: #all default OU phonemizers have been patched to take langcodes, replacements not needed
                    out_f.write("\nreplacements:\n")
                    for item in replacements:
                        out_f.write(f"- {{from: \"{item['from']}\", to: \"{item['to']}\"}}\n")
                out_f.write("\nentries:\n")
                for item in entries:
                    out_f.write(f"- {{grapheme: \"{item['grapheme']}\", phonemes: [\"{item['phonemes'][0]}\"]}}\n")
                out_f.write('- {grapheme: "SP", phonemes: [SP]}\n')
                out_f.write('- {grapheme: "AP", phonemes: [AP]}\n')

        # Finally, write the base dsdict.yaml
        dsdict_path = os.path.join(main_stuff, "dsdict.yaml")
        print(f"Writing file: dsdict.yaml with {len(all_symbols)} entries")
        with open(dsdict_path, "w", encoding="utf-8") as out_f:
            out_f.write("symbols:\n")
            out_f.write('- {symbol: SP, type: vowel}\n')
            out_f.write('- {symbol: AP, type: vowel}\n')
            for item in all_symbols:
                out_f.write(f"- {{symbol: {item['symbol']}, type: {item['type']}}}\n")
            out_f.write("\nentries:\n")
            for item in all_entries:
                out_f.write(f"- {{grapheme: \"{item['grapheme']}\", phonemes: [\"{item['phonemes'][0]}\"]}}\n")
            out_f.write('- {grapheme: "SP", phonemes: [SP]}\n')
            out_f.write('- {grapheme: "AP", phonemes: [AP]}\n')
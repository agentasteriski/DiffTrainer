import os, shutil, yaml, glob
from modules import autodsdict # type: ignore (stops vscode from whining)

def run_OU_config(ou_name_var, ou_export_location, aco_folder_dir, var_folder_dir, vocoder_onnx=None, autodsdictvar=None):
        print("making directories...")
        aco_folder_onnx = os.path.join(aco_folder_dir, "onnx")
        aco_config = os.path.join(aco_folder_dir, "config.yaml")
        var_folder_onnx = os.path.join(var_folder_dir, "onnx")
        var_config = os.path.join(var_folder_dir, "config.yaml")
        try:
            ou_name = ou_name_var.get()
            ou_name_stripped = "".join(ou_name.split()) #takes the spaces out so cmd doesn't get confused
            main_stuff = os.path.join(ou_export_location, ou_name_stripped)
            dsmain = os.path.join(main_stuff, "dsmain")
            mainembeds = os.path.join(main_stuff, "embeds")
            dsdur = os.path.join(main_stuff, "dsdur")
            durembeds = os.path.join(dsdur, "embeds")
            dsvariance = os.path.join(main_stuff, "dsvariance")
            varembeds = os.path.join(dsvariance, "embeds")
            dspitch = os.path.join(main_stuff, "dspitch")
            pitchembeds = os.path.join(dspitch, "embeds")
            if not os.path.exists(main_stuff):
                os.makedirs(main_stuff)
            if not os.path.exists(dsmain):
                os.makedirs(dsmain)
                os.makedirs(mainembeds) #these embed folders wind up empty if it's single speaker
                os.makedirs(dsdur)
                os.makedirs(durembeds) #but it doesn't hurt anything and I don't feel like making it conditional
                try:
                    if os.path.exists(os.path.join(var_folder_onnx, "variance.onnx")):
                        os.makedirs(dsvariance)
                        os.makedirs(varembeds)
                    else: pass
                except Exception as e:
                    print(f"Error creating directories: {e}")
                try:
                    if os.path.exists(os.path.join(var_folder_onnx, "pitch.onnx")):
                        os.makedirs(dspitch)
                        os.makedirs(pitchembeds)
                    else: pass
                except Exception as e:
                    print(f"Error creating directories: {e}")
            with open(os.path.join(main_stuff, "character.txt"), "w", encoding = "utf-8") as file:
                file.write(f"name={ou_name}\n") #this file could be fancier but feels like overkill for this program
            with open(os.path.join(main_stuff, "character.yaml"), "w", encoding = "utf-8") as file: #create initial yaml
                file.write("default_phonemizer: OpenUtau.Core.DiffSinger.DiffSingerPhonemizer\n") #defaults to DIFFS on first use
                file.write("singer_type: diffsinger\n")
                file.write("text_file_encoding: utf-8\n")
                file.write("image:\n")
                file.write("portrait:\n")
                file.write("portrait_opacity: 0.45\n")
        except Exception as e:
            print(f"Error creating directories: {e}")
        print("\nmoving core files...")

        try:
            shutil.copy(os.path.join(aco_folder_onnx, "acoustic.onnx"), dsmain)
            shutil.copy(os.path.join(aco_folder_onnx, "phonemes.json"), dsmain)
            shutil.copy(os.path.join(aco_folder_onnx, "languages.json"), dsmain)
            shutil.copy(os.path.join(aco_folder_onnx, "dsconfig.yaml"), main_stuff) #just straight up uses the original acoustic dsconfig as the one for the main folder
            shutil.copy(os.path.join(var_folder_onnx, "linguistic.onnx"), dsmain)

        except Exception as e:
            print(f"Error moving core files: {e}")

        print("\nmoving acoustic embeds...")
        try:
            acoustic_emb_files = [file for file in os.listdir(aco_folder_onnx) if file.endswith(".emb")]
            for emb_file in acoustic_emb_files:
                shutil.copy(os.path.join(aco_folder_onnx, emb_file), mainembeds)
            acoustic_emb_files = os.listdir(aco_folder_onnx)
            acoustic_embeds = []
            acoustic_color_suffix = []
            for file in acoustic_emb_files:
                if file.endswith(".emb"):
                    acoustic_emb = os.path.splitext(file)[0]
                    acoustic_embeds.append("embeds/" + acoustic_emb)
                    acoustic_color_suffix.append(acoustic_emb)
        except Exception as e:
                    print(f"Error moving acoustic embeds: {e}")


        print("\nmoving variance files...")
        try:
            var_emb_files = [file for file in os.listdir(var_folder_onnx) if file.endswith(".emb")]
            if os.path.exists(os.path.join(var_folder_onnx, "dur.onnx")):
                shutil.copy(os.path.join(var_folder_onnx, "dur.onnx"), dsdur)
                for emb_file in var_emb_files:
                    shutil.copy(os.path.join(var_folder_onnx, emb_file), durembeds)
            if os.path.exists(os.path.join(var_folder_onnx, "variance.onnx")):
                shutil.copy(os.path.join(var_folder_onnx, "variance.onnx"), dsvariance)
                for emb_file in var_emb_files:
                    shutil.copy(os.path.join(var_folder_onnx, emb_file), varembeds)
            if os.path.exists(os.path.join(var_folder_onnx, "pitch.onnx")):
                shutil.copy(os.path.join(var_folder_onnx, "pitch.onnx"), dspitch)
                for emb_file in var_emb_files:
                    shutil.copy(os.path.join(var_folder_onnx, emb_file), pitchembeds)
            variance_emb_files = os.listdir(var_folder_onnx)
            variance_embeds = []
            variance_color_suffix = []
            for file in variance_emb_files:
                if file.endswith(".emb"):
                    variance_emb = os.path.splitext(file)[0]
                    variance_embeds.append("embeds/" + variance_emb)
                    variance_color_suffix.append(variance_emb)
        except Exception as e:
            print(f"Error moving variance files: {e}")

        print("writing main configs...")
        try:
            subbanks = [] #list of vocal modes
            for i, (acoustic_embed_color, acoustic_embed_suffix) in enumerate(zip(acoustic_color_suffix, acoustic_embeds), start=1):
                color = f"{i:02}: {acoustic_embed_color}" #name of vocal mode
                suffix = f"{acoustic_embed_suffix}" #where to find the acoustic embed
                subbanks.append({"color": color, "suffix": suffix})
            if subbanks: #add all the modes and where to find them to character config
                with open(os.path.join(main_stuff, "character.yaml"), "r", encoding = "utf-8") as config:
                    character_config = yaml.safe_load(config)
                character_config["subbanks"] = subbanks 
                with open(os.path.join(main_stuff, "character.yaml"), "w", encoding = "utf-8") as config:
                    yaml.dump(character_config, config)
            with open(os.path.join(main_stuff, "dsconfig.yaml"), "r", encoding = "utf-8") as config:
                dsconfig_data = yaml.safe_load(config) #just edit the original config seriously
            dsconfig_data["acoustic"] = "dsmain/acoustic.onnx" #fix those file paths
            dsconfig_data["phonemes"] = "dsmain/phonemes.json" #btw we can't os.path.join here bc windows had to be special and use \ when everyone else uses /
            dsconfig_data["languages"] = "dsmain/languages.json"
            dsconfig_data["vocoder"] = "nsf_hifigan" #gets overwritten later if there's a custom vocoder
            dsconfig_data["singer_type"] = "diffsinger"
            if subbanks:
                dsconfig_data["speakers"] = acoustic_embeds #cleans up the file names
            with open(os.path.join(main_stuff, "dsconfig.yaml"), "w", encoding = "utf-8") as config:
                yaml.dump(dsconfig_data, config, sort_keys=False)
        except Exception as e:
                    print(f"Error writing OU main configs: {e}")

        print("writing sub-configs...")
        try:
            with open(aco_config, "r", encoding = "utf-8") as config:
                acoustic_config_data = yaml.safe_load(config) #copies most of the main dsconfig
            sample_rate = acoustic_config_data.get("audio_sample_rate")
            hop_size = acoustic_config_data.get("hop_size")
            with open(var_config, "r", encoding = "utf-8") as config:
                variance_config_data = yaml.safe_load(config)
            sample_rate2 = variance_config_data.get("sample_rate")
            hop_size2 = variance_config_data.get("hop_size")
            use_note_rest = variance_config_data.get("use_note_rest")
            use_continuous_acceleration = variance_config_data.get("use_continuous_acceleration")
            use_lang_id = acoustic_config_data.get("use_lang_id")

            with open(os.path.join(dsdur, "dsconfig.yaml"), "w", encoding = "utf-8") as file:
                file.write("phonemes: ../dsmain/phonemes.json\n")
                file.write("languages: ../dsmain/languages.json\n")
                file.write("linguistic: ../dsmain/linguistic.onnx\n")
                file.write("dur: dur.onnx\n") #file paths aren't totally the same so gotta rewrite
            with open(os.path.join(dsdur, "dsconfig.yaml"), "r", encoding = "utf-8") as config:
                dsdur_config = yaml.safe_load(config)
            dsdur_config["use_continuous_acceleration"] = use_continuous_acceleration
            dsdur_config["sample_rate"] = sample_rate2
            dsdur_config["hop_size"] = hop_size2
            dsdur_config["predict_dur"] = True #this is the dur config, if it doesn't predict_dur wtf does it do
            dsdur_config["use_lang_id"] = use_lang_id
            if subbanks:
                dsdur_config["speakers"] = variance_embeds #points it to the correct embeds for dur
            with open(os.path.join(dsdur, "dsconfig.yaml"), "w", encoding = "utf-8") as config:
                yaml.dump(dsdur_config, config, sort_keys=False)

            try:
                if os.path.exists(os.path.join(var_folder_onnx, "variance.onnx")): #if no bre/ene/ten/voc, skips this section
                    with open(var_config, "r", encoding = "utf-8") as config: #it's basically the same as dsdur in basic export tho
                        var_config_data = yaml.safe_load(config)
                    predict_voicing = var_config_data.get("predict_voicing")
                    predict_tension = var_config_data.get("predict_tension")
                    predict_energy = var_config_data.get("predict_energy")
                    predict_breathiness = var_config_data.get("predict_breathiness")
                    predict_dur = var_config_data.get("predict_dur")
                    with open(os.path.join(dsvariance, "dsconfig.yaml"), "w", encoding = "utf-8") as file:
                        file.write("phonemes: ../dsmain/phonemes.json\n")
                        file.write("languages: ../dsmain/languages.json\n")
                        file.write("linguistic: ../dsmain/linguistic.onnx\n")
                        file.write("variance: variance.onnx\n")
                    with open(os.path.join(dsvariance, "dsconfig.yaml"), "r", encoding = "utf-8") as config:
                        dsvariance_config = yaml.safe_load(config)
                    dsvariance_config["use_continuous_acceleration"] = use_continuous_acceleration
                    dsvariance_config["sample_rate"] = sample_rate
                    dsvariance_config["hop_size"] = hop_size
                    dsvariance_config["predict_dur"] = predict_dur
                    dsvariance_config["predict_voicing"] = predict_voicing
                    dsvariance_config["predict_tension"] = predict_tension
                    dsvariance_config["predict_energy"] = predict_energy
                    dsvariance_config["predict_breathiness"] = predict_breathiness
                    dsvariance_config["use_lang_id"] = use_lang_id
                    if subbanks:
                        dsvariance_config["speakers"] = variance_embeds
                    with open(os.path.join(dsvariance, "dsconfig.yaml"), "w", encoding = "utf-8") as config:
                        yaml.dump(dsvariance_config, config, sort_keys=False)
                else:
                    print("No variance selected")
            except Exception as e:
                print(f"Error editing variance config: {e}")

            try:
                if os.path.exists(os.path.join(var_folder_onnx, "pitch.onnx")): #if no pitch, skips this section
                    with open(os.path.join(dspitch, "dsconfig.yaml"), "w", encoding = "utf-8") as file:
                        file.write("phonemes: ../dsmain/phonemes.json\n")
                        file.write("languages: ../dsmain/languages.json\n")
                        file.write("linguistic: ../dsmain/linguistic.onnx\n")
                        file.write("predict_dur: true\n")
                        file.write("pitch: pitch.onnx\n")
                        file.write("use_expr: true\n")
                    with open(os.path.join(dspitch, "dsconfig.yaml"), "r", encoding = "utf-8") as config:
                        dspitch_config = yaml.safe_load(config)
                    dspitch_config["use_continuous_acceleration"] = use_continuous_acceleration
                    dspitch_config["sample_rate"] = sample_rate
                    dspitch_config["hop_size"] = hop_size
                    dspitch_config["predict_dur"] = predict_dur
                    dspitch_config["use_lang_id"] = use_lang_id
                    if subbanks:
                        dspitch_config["speakers"] = variance_embeds
                    dspitch_config["use_note_rest"] = use_note_rest
                    with open(os.path.join(dspitch, "dsconfig.yaml"), "w", encoding = "utf-8") as config:
                        yaml.dump(dspitch_config, config, sort_keys=False)
                else:
                    print("No pitch selected")
            except Exception as e:
                print(f"Error editing pitch config: {e}")
        except Exception as e:
            print(f"Error editing sub-configs: {e}")

        if vocoder_onnx:
            print("making dsvocoder directory and necessary files...")
            try:
                os.makedirs(os.path.join(main_stuff, "dsvocoder"))
                vocoder_folder = os.path.dirname(vocoder_onnx)
                vocoder_file = os.path.basename(vocoder_onnx)
                vocoder_name = os.path.splitext(vocoder_file)[0]
                shutil.copy(vocoder_onnx, os.path.join(main_stuff, "dsvocoder"))
                shutil.copy(os.path.join(vocoder_folder, "vocoder.yaml"), os.path.join(main_stuff, "dsvocoder"))
                with open(os.path.join(main_stuff, "dsconfig.yaml"), "r", encoding = "utf-8") as config:
                    dsconfig_data2 = yaml.safe_load(config)
                dsconfig_data2["vocoder"] = vocoder_name #overwrites nsf_hifigan
                with open(os.path.join(main_stuff, "dsconfig.yaml"), "w", encoding = "utf-8") as config:
                    yaml.dump(dsconfig_data2, config, sort_keys=False)
            except Exception as e:
                    print(f"Error adding custom vocoder: {e}")
        autodict = autodsdictvar.get()
        if autodict == True:
            autodsdict.dictgenerator(aco_folder_dir, main_stuff)

            lang_dictionary_files_yaml = glob.glob(os.path.join(main_stuff, "*.yaml"))
            for yaml_dictionary_file in lang_dictionary_files_yaml:
                filename = os.path.basename(yaml_dictionary_file)
                if filename != "dsconfig.yaml" and filename != "character.yaml" and os.path.exists(yaml_dictionary_file):
                    shutil.copy(yaml_dictionary_file, dsdur)
                    if os.path.exists(os.path.join(var_folder_onnx, "variance.onnx")):
                        shutil.copy(yaml_dictionary_file, dsvariance)
                    if os.path.exists(os.path.join(var_folder_onnx, "pitch.onnx")):
                        shutil.copy(yaml_dictionary_file, dspitch)
                    os.remove(yaml_dictionary_file)
        print("OU setup complete!")
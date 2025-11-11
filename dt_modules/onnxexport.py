import os, json, shutil, sys
from collections import defaultdict

realpython = sys.executable

def prep_onnx_export(ckpt_save_dir):
    onnx_folder_dir = os.path.join(ckpt_save_dir, "onnx")
    if os.path.exists(onnx_folder_dir):
        onnx_bak = os.path.join(ckpt_save_dir, "onnx_old")
        os.rename(onnx_folder_dir, onnx_bak)
        print("backing up existing onnx folder...")
    spkmap = os.path.join(ckpt_save_dir, "spk_map.json")
    with open(spkmap, "r") as file:
        data = json.load(file)
    result = {}
    seen_values = defaultdict(list)
    for key, value in data.items():
        seen_values[value].append(key)
    for value, keys in seen_values.items():
        if len(keys) > 1:
            # Merging duplicate spk_ids by trying to reduce the names to a common prefix
            min_length = min(len(key) for key in keys)
            common_prefix = ""
            for i in range(min_length):
                char_set = set(key[i] for key in keys)
                if len(char_set) != 1:
                    break
                common_prefix += char_set.pop()
            # If you used '-lang' or something, get rid of the separator
            unwanted_chars = ('-', '_', '.')
            while common_prefix.endswith(unwanted_chars):
                common_prefix = common_prefix.rstrip("-_.")
            # If you did something insane like naming folders '-1' and '-2', and it just deleted the 1 and 2, no blank entries
            if common_prefix:
                result[common_prefix] = value
            else:
                result[min(keys, key=len)] = value
        else:
            result[keys[0]] = value
    with open(spkmap, "w") as file:
        json.dump(result, file)

def writecmd(ckpt_save_dir, expselect):
    cmdstage = [realpython, 'scripts/export.py']
    export_check = expselect.get()
    ckpt_save_abs = os.path.abspath(ckpt_save_dir)
    onnx_folder_dir = os.path.join(ckpt_save_dir, "onnx")
    onnx_folder_abs = os.path.abspath(onnx_folder_dir)
    if export_check == 1:
        print("exporting acoustic...")
        cmdstage.append('acoustic')
        cmdstage.append('--exp')
        cmdstage.append(ckpt_save_abs)
        cmdstage.append('--out')
        cmdstage.append(onnx_folder_abs)
    elif export_check == 2:
        print("exporting variance...")
        cmdstage.append('variance')
        cmdstage.append('--exp')
        cmdstage.append(ckpt_save_abs)
        cmdstage.append('--out')
        cmdstage.append(onnx_folder_abs)

    command = " ".join(cmdstage)
    return command
    #run_cmdB(command)


def onnx_cleanup(ckpt_save_dir):
    print("Getting the files in order...")
    #move file cus it export stuff outside the save folder for some reason
    onnx_folder_dir = os.path.join(r"" + ckpt_save_dir, "onnx")
    ckpt_save_abs = os.path.abspath(ckpt_save_dir)
    onnx_folder_abs = os.path.abspath(onnx_folder_dir)
    mv_basename = os.path.dirname(ckpt_save_abs)
    #for .onnx
    [shutil.move(os.path.join(mv_basename, filename), onnx_folder_abs)
    for filename in os.listdir(mv_basename) if filename.endswith(".onnx")]
    #for .emb
    [shutil.move(os.path.join(mv_basename, filename), onnx_folder_abs)
    for filename in os.listdir(mv_basename) if filename.endswith(".emb")]
    #for dict and phonemes txt
    [shutil.move(os.path.join(mv_basename, filename), onnx_folder_abs)
    for filename in os.listdir(mv_basename) if filename.endswith(("dictionary.txt", "phonemes.txt", "languages.json", "phonemes.json"))]

    prefix = os.path.basename(ckpt_save_dir)
    if prefix != "acoustic":
        wronnx = prefix + ".onnx"
        wronnx_path = os.path.join(onnx_folder_dir, wronnx)
        rightnnx_path = os.path.join(onnx_folder_dir, "acoustic.onnx")
        if os.path.exists(wronnx_path):
            os.rename(wronnx_path, rightnnx_path)
    nameList = os.listdir(onnx_folder_dir)
    for fileName in nameList:
        if fileName == prefix:
            continue
        fullname = os.path.join(onnx_folder_dir, fileName)
        rename=fileName.removeprefix(prefix + ".")
        fullrename = os.path.join(onnx_folder_dir, rename)
        os.rename(fullname, fullrename)
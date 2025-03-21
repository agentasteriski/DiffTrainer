import subprocess, os, yaml, sys, json
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from ezlocalizr import ezlocalizr

if os.path.exists('assets/ds_gui.json'):
      ctk.set_default_color_theme("assets/ds_gui.json")
else:
      pass
main_path = os.getcwd()
diffolder = f"{main_path}/DiffSinger"
ckpts = f"{main_path}/DiffSinger/checkpoints"

username = os.environ.get('USERNAME')
def is_linux():
    return sys.platform.startswith("linux")
def is_windows():
    return sys.platform.startswith("win")
def is_macos():
    return sys.platform.startswith("darwin")

if is_windows():
    username = os.environ.get('USERNAME')
    if os.path.exists(os.path.join(main_path, "miniconda")):
        conda_path = os.path.join(main_path, "miniconda", "condabin", "conda.bat")
    elif os.path.exists(os.path.join("C:", "ProgramData", "anaconda3")):
        conda_path = os.path.join("C:", "ProgramData", "anaconda3", "condabin", "conda.bat")
    elif os.path.exists(os.path.join("C:", "ProgramData", "miniconda3")):
        conda_path = os.path.join("C:", "ProgramData", "miniconda3", "condabin", "conda.bat")
    elif os.path.exists(os.path.join("C:", "Users", username, "anaconda3")):
        conda_path = os.path.join("C:", "Users", username, "anaconda3", "condabin", "conda.bat")
    elif os.path.exists(os.path.join("C:", "Users", username, "miniconda3")):
        conda_path = os.path.join("C:", "Users", username, "miniconda3", "condabin", "conda.bat")
    else: conda_path = "conda"
elif is_macos():
    if os.path.exists(os.path.join("opt", "miniconda3")):
        conda_path = os.path.join("opt", "miniconda3", "etc", "profile.d", "conda.sh")
    elif os.path.exists(os.path.join("opt", "anaconda3")):
        conda_path = os.path.join("opt", "anaconda3", "etc", "profile.d", "conda.sh")
    else: conda_path = "conda"
elif is_linux():
    username = os.environ.get('USER')
    if os.path.exists(os.path.join("Users", username, "anaconda3")):
        conda_path = os.path.join("Users", username, "anaconda3", "etc", "profile.d", "conda.sh")
    elif os.path.exists(os.path.join("Users", username, "miniconda3")):
        conda_path = os.path.join("Users", username, "miniconda3", "etc", "profile.d", "conda.sh")
    else: conda_path = "conda"

guisettings = {
    'lang': 'en_US',
}


if os.path.exists(('assets/guisettings.yaml')):
    with open('assets/guisettings.yaml', 'r', encoding='utf-8') as c:
        try:
                guisettings.update(yaml.safe_load(c))
                c.close()
        except yaml.YAMLError as exc:
            print("No settings detected, defaulting to EN_US")

ctk.FontManager.load_font(os.path.join(main_path, "assets","RedHatDisplay-Regular.ttf"))
ctk.FontManager.load_font(os.path.join(main_path, "assets","MPLUS2-Regular.ttf"))
ctk.FontManager.load_font(os.path.join(main_path, "assets","NotoSansSC-Regular.ttf"))
ctk.FontManager.load_font(os.path.join(main_path, "assets","NotoSansTC-Regular.ttf"))

font_en = 'Red Hat Display'
font_jp = 'M PLUS 2'
font_cn = 'Noto Sans SC'
font_tw = 'Noto Sans TC'

varckptQ = ''

def var():
        varget = filedialog.askdirectory(title=L('getvar'), initialdir = "DiffSinger/checkpoints")
        os.chdir(main_path)
        varckpt = os.path.relpath(varget, ckpts)
        print(varckpt)
        global varckptQ
        varckptQ = '"{}"'.format(varckpt)
def aco():
        acoget = filedialog.askdirectory(title=L('getaco'), initialdir = "DiffSinger/checkpoints")
        os.chdir(main_path)
        acockpt = os.path.relpath(acoget, ckpts)
        print(acockpt)
        aco_config = acoget + "/config.yaml"
        with open(aco_config, "r", encoding = "utf-8") as config:
                conf = yaml.safe_load(config)
        global bre_status
        bre_status = conf["use_breathiness_embed"]
        global ene_status
        ene_status = conf["use_energy_embed"]
        global ten_status
        ten_status = conf["use_tension_embed"]
        global voc_status
        voc_status = conf["use_voicing_embed"]
        global acockptQ
        acockptQ = '"{}"'.format(acockpt)
def ds():
        dsinput = filedialog.askopenfilename(title=L('getds'), filetypes=[("DS files", "*.ds")])
        print(dsinput)
        print(L('eval'))
        with open(dsinput, 'r', encoding='utf-8') as file:
             data = json.load(file)
        
        global hasdur
        def find_dur(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'ph_dur':
                        return True
                    else:
                        if find_dur(value):
                            return True
            if isinstance(data, list):
                for item in data:
                    if find_dur(item):
                        return True
            return False
        if find_dur(data):
             hasdur = True
             print(L('hasdur'))
        else:
             hasdur = False

        global haspitch
        def find_pitch(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'f0_seq':
                        return True
                    else:
                        if find_pitch(value):
                            return True
            if isinstance(data, list):
                for item in data:
                    if find_pitch(item):
                        return True
            return False
        if find_pitch(data):
             haspitch = True
             print(L('haspitch'))
        else:
             haspitch = False

        global hastension
        def find_tension(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'tension':
                        return True
                    else:
                        if find_tension(value):
                            return True
            if isinstance(data, list):
                for item in data:
                    if find_tension(item):
                        return True
            return False
        if find_tension(data):
             hastension = True
             print(L('hasten'))
        else:
             hastension = False
        
        global hasvoicing
        def find_voicing(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'voicing':
                        return True
                    else:
                        if find_voicing(value):
                            return True
            if isinstance(data, list):
                for item in data:
                    if find_voicing(item):
                        return True
            return False
        if find_voicing(data):
             hasvoicing = True
             print(L('hasvoc'))
        else:
             hasvoicing = False

        global hasenergy
        def find_energy(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'energy':
                        return True
                    else:
                        if find_energy(value):
                            return True
            if isinstance(data, list):
                for item in data:
                    if find_energy(item):
                        return True
            return False
        if find_energy(data):
             hasenergy = True
             print(L('hasene'))
        else:
             hasenergy = False

        global hasbreathiness
        def find_breathiness(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'breathiness':
                        return True
                    else:
                        if find_breathiness(value):
                            return True
            if isinstance(data, list):
                for item in data:
                    if find_breathiness(item):
                        return True
            return False
        if find_breathiness(data):
             hasbreathiness = True
             print(L('hasbre'))
        else:
             hasbreathiness = False

        print(L('eval2'))
        global dsinputQ
        dsinputQ = '"{}"'.format(dsinput)
        dsloc = os.path.dirname(dsinput)
        global dslocQ
        dslocQ = '"{}"'.format(dsloc)
        dsname = os.path.basename(dsinput)
        dsname2 = os.path.splitext(dsname)[0]
        global dsname2Q
        dsname2Q = '"{}"'.format(dsname2)
        postvar = dsname2 + "_var"
        global postvarQ
        postvarQ = '"{}"'.format(postvar)
        postvards = dsloc + "/" + postvar + ".ds"
        global postvardsQ 
        postvardsQ = '"{}"'.format(postvards)
        global renderedQ
        rendered = os.path.join(dsloc, dsname2) + ".wav"
        renderedQ = '"{}"'.format(rendered)

def run_cmdA(cmd):
        if is_windows():
            cmd = f'{conda_path} activate difftrainerA >nul && {cmd}'
        elif is_linux() or is_macos():
            cmd = f'eval "$(conda shell.bash hook)" && {conda_path} activate difftrainerA && {cmd}'
        try:
            subprocess.run(cmd, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")
def render():
      os.chdir(diffolder)
      spkname = spk.get()
      langname = lcode.get()
      pdur = overdur.get()
      ppit = overpit.get()
      pbre = overbre.get()
      prene = overene.get()
      pten = overten.get()
      pvoc = overvoc.get()
      if varckptQ != '':
            cmd1 = ['python', 'scripts/infer.py', 'variance', dsinputQ, '--exp', varckptQ, '--spk', spkname, '--lang', langname, '--out', dslocQ, '--title', postvarQ]
            if pdur == True:
                 cmd1.append('--predict')
                 cmd1.append('dur')
            if ppit == True:
                 cmd1.append('--predict')
                 cmd1.append('pitch')
            if pbre == True:
                 cmd1.append('--predict')
                 cmd1.append('breathiness')
            if prene == True:
                 cmd1.append('--predict')
                 cmd1.append('energy')
            if pten == True:
                 cmd1.append('--predict')
                 cmd1.append('tension')
            if pvoc == True:
                 cmd1.append('--predict')
                 cmd1.append('voicing')
            if (pdur == True or ppit == True or prene == True or pten == True or pvoc == True) and pbre == False and bre_status == True and hasbreathiness == False:
                 cmd1.append('--predict')
                 cmd1.append('breathiness')
            if (pdur == True or ppit == True or pbre == True or pten == True or pvoc == True) and prene == False and ene_status == True and hasenergy == False:
                 cmd1.append('--predict')
                 cmd1.append('energy')
            if (pdur == True or ppit == True or pbre == True or prene == True or pvoc == True) and pten == False and ten_status == True and hastension == False:
                 cmd1.append('--predict')
                 cmd1.append('tension')
            if (pdur == True or ppit == True or pbre == True or pten == True or prene == True) and pvoc == False and voc_status == True and hasvoicing == False:
                 cmd1.append('--predict')
                 cmd1.append('voicing')
            print(L('inf1'))
            command1 = ' '.join(cmd1)
            run_cmdA(command1)
            cmd2 = ['python', 'scripts/infer.py', 'acoustic', postvardsQ, '--exp', acockptQ, '--spk', spkname, '--lang', langname, '--out', dslocQ, '--title', dsname2Q]
            command2 = ' '.join(cmd2)
            run_cmdA(command2)
            print(L('inf2'))
        
            subprocess.check_call(["powershell", "-c", f'(New-Object Media.SoundPlayer {renderedQ}).PlaySync();'])
      else:
            cmd3 = ['python', 'scripts/infer.py', 'acoustic', dsinputQ, '--exp', acockptQ, '--spk', spkname, '--lang', langname, '--out', dslocQ, '--title', dsname2Q]
            command3 = ' '.join(cmd3)
            print(L('inf2'))
            run_cmdA(command3)
            subprocess.check_call(["powershell", "-c", f'(New-Object Media.SoundPlayer {renderedQ}).PlaySync();'])

def replay():
    try:
        subprocess.check_call(["powershell", "-c", f'(New-Object Media.SoundPlayer {renderedQ}).PlaySync();'])
    except subprocess.CalledProcessError:
         print(L('replayerror'))




app = ctk.CTk()
app.title("Quick Inference")

lang = ctk.StringVar(value=guisettings['lang'])
L = ezlocalizr(language=lang.get(),
                            string_path='strings',
                            default_lang='en_US')
if lang.get() in ['jp-JP']:
      font = ctk.CTkFont(family=font_jp, size = 14)
elif lang.get() in ['zh-CN']:
      font = ctk.CTkFont(family=font_cn, size = 16)
elif lang.get() in ['zh-TW']:
      font = ctk.CTkFont(family=font_tw, size = 16)
else:
      font = ctk.CTkFont(family=font_en)

button = ctk.CTkButton(app, text=L('varckpt'), command=var, font=font)
button.grid(row=0, column=0, padx=10, pady=10)
button2 = ctk.CTkButton(app, text=L('acockpt'), command=aco, font=font)
button2.grid(row=0, column=1, padx=10, pady=10)

overwriteframe = ctk.CTkFrame(app)
overwriteframe.grid(row=1, padx=10, pady=10, column=0, columnspan=2)
over = ctk.CTkLabel(overwriteframe, text=L('overwrite'), font=font)
over.grid(row=0, column=0, columnspan=2, padx=5, pady=(5,0))
overdur = tk.BooleanVar()
overpit = tk.BooleanVar()
overbre = tk.BooleanVar()
overene = tk.BooleanVar()
overten = tk.BooleanVar()
overvoc = tk.BooleanVar()

durbox = ctk.CTkCheckBox(overwriteframe, text="dur", variable=overdur, font=font)
durbox.grid(row=1, column=0, padx=(5,0), pady=5)
pitbox = ctk.CTkCheckBox(overwriteframe, text="pit", variable=overpit, font=font)
pitbox.grid(row=1, column=1, padx=(5,0), pady=5)
brebox = ctk.CTkCheckBox(overwriteframe, text="bre", variable=overbre, font=font)
brebox.grid(row=2, column=0, padx=(5,0), pady=(0,5))
enebox = ctk.CTkCheckBox(overwriteframe, text="ene", variable=overene, font=font)
enebox.grid(row=2, column=1, padx=(5,0), pady=(0,5))
tenbox = ctk.CTkCheckBox(overwriteframe, text="ten", variable=overten, font=font)
tenbox.grid(row=3, column=0, padx=(5,0), pady=(0,5))
vocbox = ctk.CTkCheckBox(overwriteframe, text="voc", variable=overvoc, font=font)
vocbox.grid(row=3, column=1, padx=(5,0), pady=(0,5))



spk = tk.StringVar(value=L('spk'))
box = ctk.CTkEntry(app, textvariable=spk, font=font)
box.grid(row=2, column=0, padx=10, pady=10)
lcode = tk.StringVar(value=L('langcode'))
box2 = ctk.CTkEntry(app, textvariable=lcode, font=font)
box2.grid(row=2, column=1, padx=10, pady=10)
button3 = ctk.CTkButton(app, text=L('getds'), command=ds, font=font)
button3.grid(row=3, column=0, padx=10, pady=10)
button4 = ctk.CTkButton(app, text=L('render'), command=render, font=font)
button4.grid(row=3, column=1, padx=10, pady=10)
button5 = ctk.CTkButton(app, text=L('replay'), command=replay, font=font)
button5.grid(row=4, column=0, padx=10, pady=10, columnspan=2)

app.mainloop()
import subprocess, os, yaml, sys
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
        global acockptQ
        acockptQ = '"{}"'.format(acockpt)
def ds():
        dsinput = filedialog.askopenfilename(title=L('getds'), filetypes=[("DS files", "*.ds")])
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
        print(dsinput)
        
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
      if varckptQ != '':
            cmd1 = ['python', 'scripts/infer.py', 'variance', dsinputQ, '--exp', varckptQ, '--spk', spkname, '--out', dslocQ, '--title', postvarQ]
            print('inferencing variance data...')
            command1 = ' '.join(cmd1)
            run_cmdA(command1)
            cmd2 = ['python', 'scripts/infer.py', 'acoustic', postvardsQ, '--exp', acockptQ, '--spk', spkname, '--out', dslocQ, '--title', dsname2Q]
            command2 = ' '.join(cmd2)
            run_cmdA(command2)
            print('inferencing acoustic data...')
        
            subprocess.check_call(["powershell", "-c", f'(New-Object Media.SoundPlayer {renderedQ}).PlaySync();'])
      else:
            cmd3 = ['python', 'scripts/infer.py', 'acoustic', dsinputQ, '--exp', acockptQ, '--spk', spkname, '--out', dslocQ, '--title', dsname2Q]
            command3 = ' '.join(cmd3)
            print('inferencing acoustic data...')
            run_cmdA(command3)
            subprocess.check_call(["powershell", "-c", f'(New-Object Media.SoundPlayer {renderedQ}).PlaySync();'])

def replay():
      subprocess.check_call(["powershell", "-c", f'(New-Object Media.SoundPlayer {renderedQ}).PlaySync();'])




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
spk = tk.StringVar(value=L('spk'))
box = ctk.CTkEntry(app, textvariable=spk, font=font)
box.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
button3 = ctk.CTkButton(app, text=L('getds'), command=ds, font=font)
button3.grid(row=2, column=0, padx=10, pady=10)
button4 = ctk.CTkButton(app, text=L('render'), command=render, font=font)
button4.grid(row=2, column=1, padx=10, pady=10)
button5 = ctk.CTkButton(app, text=L('replay'), command=replay, font=font)
button5.grid(row=3, column=0, padx=10, pady=10, columnspan=2)

app.mainloop()
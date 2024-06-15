import subprocess, os, yaml
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from ezlocalizr import ezlocalizr
import pyglet

if os.path.exists('assets/ds_gui.json'):
      ctk.set_default_color_theme("assets/ds_gui.json")
else:
      pass
main_path = os.getcwd()
diffolder = f"{main_path}/DiffSinger"
ckpts = f"{main_path}/DiffSinger/checkpoints"

if os.path.exists(f"{main_path}/python"):
    pip_exe = f"{main_path}/python/Scripts/pip"
    python_exe = f"{main_path}/python/python.exe"
else:
    pip_exe = "pip"
    python_exe = "python"

guisettings = {
    'lang': 'en_US'
}

pyglet.options['win32_gdi_font'] = True

if os.path.exists(('assets/guisettings.yaml')):
    with open('assets/guisettings.yaml', 'r', encoding='utf-8') as c:
        try:
            guisettings.update(yaml.safe_load(c))
            c.close()
        except yaml.YAMLError as exc:
            print("No language choice detected, defaulting to EN_US")

pyglet.font.add_file(os.path.join("assets","RedHatDisplay-Regular.ttf"))
font_en = 'Red Hat Display'
pyglet.font.add_file(os.path.join("assets","MPLUS2-Regular.ttf"))
font_jp = 'M PLUS 2'
pyglet.font.add_file(os.path.join("assets","NotoSansSC-Regular.ttf"))
font_cn = 'Noto Sans SC'
pyglet.font.add_file(os.path.join("assets","NotoSansSC-Regular.ttf"))
font_tw = 'Noto Sans TC'


def var():
        varget = filedialog.askdirectory(title=L('getvar'), initialdir = "DiffSinger/checkpoints")
        os.chdir(main_path)
        global varckpt
        varckpt = os.path.relpath(varget, ckpts)
        print(varckpt)
def aco():
        acoget = filedialog.askdirectory(title=L('getaco'), initialdir = "DiffSinger/checkpoints")
        os.chdir(main_path)
        global acockpt
        acockpt = os.path.relpath(acoget, ckpts)
        print(acockpt)
def ds():
        global dsinput
        dsinput = filedialog.askopenfilename(title=L('getds'), filetypes=[("DS files", "*.ds")])
        global dsloc
        dsloc = os.path.dirname(dsinput)
        dsname = os.path.basename(dsinput)
        global dsname2
        dsname2 = os.path.splitext(dsname)[0]
        global dsname3
        dsname3 = os.path.splitext(dsinput)[0]
        global postvar
        postvar = dsname2 + "_var"
        global postvards
        postvards = dsloc + "/" + postvar + ".ds"
        print(dsinput)
def render():
      os.chdir(diffolder)
      spkname = spk.get()
      if varckpt != '':
            cmd1 = [python_exe, 'scripts/infer.py', 'variance', dsinput, '--exp', varckpt, '--spk', spkname, '--out', dsloc, '--title', postvar]
            print('inferencing variance data...')
            print(' '.join(cmd1))
            output = subprocess.check_output(cmd1, universal_newlines=True)
            print(output)
            cmd2 = [python_exe, 'scripts/infer.py', 'acoustic', postvards, '--exp', acockpt, '--spk', spkname, '--out', dsloc, '--title', dsname2]
            print(cmd2)
            print('inferencing acoustic data...')
            subprocess.check_output(cmd2, universal_newlines=True)
            global rendered
            rendered = os.path.join(dsloc, dsname2) + ".wav"
            subprocess.check_call(["powershell", "-c", f'(New-Object Media.SoundPlayer {rendered}).PlaySync();'])
      else:
            cmd3 = [python_exe, 'scripts/infer.py', 'acoustic', dsinput, '--exp', acockpt, '--spk', spkname, '--out', dsloc, '--title', dsname2]
            print(cmd3)
            print('inferencing acoustic data...')
            subprocess.check_output(cmd3, universal_newlines=True)
            subprocess.check_call(["powershell", "-c", f'(New-Object Media.SoundPlayer {rendered}).PlaySync();'])

def replay():
      subprocess.check_call(["powershell", "-c", f'(New-Object Media.SoundPlayer {rendered}).PlaySync();'])




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
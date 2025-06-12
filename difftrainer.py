import zipfile, shutil, csv, json, yaml, random, subprocess, os, requests, re, webbrowser, sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
from tqdm import tqdm
from CTkToolTip import CTkToolTip
from ezlocalizr import ezlocalizr
from collections import defaultdict


ctk.set_default_color_theme("assets/ds_gui.json")
main_path = os.path.dirname(__file__)
version = "0.3.33"
releasedate = "6/12/25"

#checks OS, looks for conda in default install locations(+custom install in Difftrainer folder for Windows)
#if it's not there then it better be in path
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
    elif os.path.exists(os.path.join("C:", os.sep, "ProgramData", "anaconda3")):
        conda_path = os.path.join("C:", os.sep, "ProgramData", "anaconda3", "condabin", "conda.bat")
    elif os.path.exists(os.path.join("C:", os.sep, "ProgramData", "miniconda3")):
        conda_path = os.path.join("C:", os.sep, "ProgramData", "miniconda3", "condabin", "conda.bat")
    elif os.path.exists(os.path.join("C:", os.sep, "Users", username, "anaconda3")):
        conda_path = os.path.join("C:", os.sep, "Users", username, "anaconda3", "condabin", "conda.bat")
    elif os.path.exists(os.path.join("C:", os.sep, "Users", username, "miniconda3")):
        conda_path = os.path.join("C:", os.sep, "Users", username, "miniconda3", "condabin", "conda.bat")
    else: 
        conda_path = "conda"
elif is_macos():
    if os.path.exists(os.path.join("opt", "miniconda3")):
        conda_path = os.path.join("opt", "miniconda3", "etc", "profile.d", "conda.sh")
    elif os.path.exists(os.path.join("opt", "anaconda3")):
        conda_path = os.path.join("opt", "anaconda3", "etc", "profile.d", "conda.sh")
    else: conda_path = "conda"
elif is_linux():
    username = os.environ.get('USER')
    if os.path.exists(os.path.join("home", username, "anaconda3")):
        conda_path = os.path.join("home", username, "anaconda3", "etc", "profile.d", "conda.sh")
    elif os.path.exists(os.path.join("home", username, "miniconda3")):
        conda_path = os.path.join("home", username, "miniconda3", "etc", "profile.d", "conda.sh")
    else: conda_path = "conda"

#starts with English before overriding the language with whatever's in the settings
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

#this function is basically undocumented in CTk docs but I found it in a random issues thread on the GitHub
#it doesn't work on Mac but it doesn't break things like the Pyglet method did
ctk.FontManager.load_font(os.path.join(main_path, "assets","RedHatDisplay-Regular.ttf"))
ctk.FontManager.load_font(os.path.join(main_path, "assets","MPLUS2-Regular.ttf"))
ctk.FontManager.load_font(os.path.join(main_path, "assets","NotoSansSC-Regular.ttf"))
ctk.FontManager.load_font(os.path.join(main_path, "assets","NotoSansTC-Regular.ttf"))

font_en = 'Red Hat Display'
font_jp = 'M PLUS 2'
font_cn = 'Noto Sans SC'
font_tw = 'Noto Sans TC'

class tabview(ctk.CTkTabview):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        os.chdir(main_path)

        self.all_shits = r"" #forcing users to select the folder <3
        self.data_folder = r"" #more forces
        self.ckpt_save_dir = r"" #even more forces
        self.trainselect_option = r"" #rawr
        self.vocoder_onnx = r"" #actually this one isn't forcing anything none is fine
        self.spk_info = {}

        self.lang = ctk.StringVar(value=guisettings['lang'])
        self.L = ezlocalizr(language=self.lang.get(),
                            string_path='strings',
                            default_lang='en_US')
        if self.lang.get() in ['jp-JP']:
            self.font = ctk.CTkFont(family=font_jp, size = 14)
            self.font_ul = ctk.CTkFont(family=font_jp, size = 14, underline=True)
        elif self.lang.get() in ['zh-CN']:
            self.font = ctk.CTkFont(family=font_cn, size = 16)
            self.font_ul = ctk.CTkFont(family=font_cn, size = 16, underline=True)
        elif self.lang.get() in ['zh-TW']:
            self.font = ctk.CTkFont(family=font_tw, size = 16)
            self.font_ul = ctk.CTkFont(family=font_tw, size = 16, underline=True)
        else:
            self.font = ctk.CTkFont(family=font_en)
            self.font_ul = ctk.CTkFont(family=font_en, underline=True)

        # create tabs
        self.add(self.L('tab_ttl_1'))
        self.add(self.L('tab_ttl_2'))
        self.add(self.L('tab_ttl_3'))
        self.add(self.L('tab_ttl_4'))
        self.add(self.L('tab_ttl_5'))
        self.add(self.L('tab_ttl_6'))
        for button in self._segmented_button._buttons_dict.values():
            button.configure(font = self.font)

        # load images
        self.logo = ctk.CTkImage(light_image=Image.open("assets/difftrainerlogo.png"),
                                  dark_image=Image.open("assets/difftrainerlogo.png"),
                                  size=(400, 150))

        ##ABOUT
        #to do: rewrite for accuracy(at this point all that's left of Ghin's code is the segmenter tab and the questionable variable names)
        #add info on tools used, add line to credit active localization
        self.label = ctk.CTkLabel(master=self.tab(self.L('tab_ttl_1')), text = "", image = self.logo)
        self.label.grid(row=0, column=0, ipady=10, columnspan = 3)
        self.label = ctk.CTkLabel(master=self.tab(self.L('tab_ttl_1')), text = f"{self.L('vers')} {version}({releasedate})", font = self.font)
        self.label.grid(row=1, column=1)
        self.button = ctk.CTkButton(master=self.tab(self.L('tab_ttl_1')), text = self.L('changelog'), font = self.font)
        self.button.grid(row=2, column=0, padx=50)
        self.button.bind("<Button-1>", lambda e: self.credit("https://github.com/agentasteriski/DiffTrainer/blob/multidict/changelog.md"))
        self.button = ctk.CTkButton(master=self.tab(self.L('tab_ttl_1')), text = self.L('update'), command = self.dl_update, font = self.font)
        self.button.grid(row=2, column=2, padx=50)
        self.tooltip = CTkToolTip(self.button, message=(self.L('update2')), font = self.font)
        self.label = ctk.CTkLabel(master=self.tab(self.L('tab_ttl_1')), text = (self.L('cred_front') + " Aster"), font = self.font_ul)
        self.label.bind("<Button-1>", lambda e: self.credit("https://github.com/agentasteriski"))
        self.label.grid(row=3, column=0, columnspan=2, pady=30)
        self.tooltip = CTkToolTip(self.label, message="owo")
        self.label = ctk.CTkLabel(master=self.tab(self.L('tab_ttl_1')), text = (self.L('cred_back') + " Ghin"), font = self.font_ul)
        self.label.bind("<Button-1>", lambda e: self.credit("https://github.com/MLo7Ghinsan"))
        self.label.grid(row=3, column=1, columnspan=2, pady=30)
        self.tooltip = CTkToolTip(self.label, message="uwu")
        self.label = ctk.CTkLabel(master=self.tab(self.L('tab_ttl_1')), text = self.L('restart'), font = self.font)
        self.label.grid(row=4, column=2, sticky=tk.W)
        self.langselect = ctk.CTkComboBox(master=self.tab(self.L('tab_ttl_1')), values=self.L.lang_list, command=lambda x: self.refresh(self.lang.get(), master=self), variable=self.lang, font = self.font)
        self.langselect.grid(row=4, column=2, sticky=tk.SE)

        ##SEGMENT

        self.frame1 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_2')))
        self.frame1.grid(padx=(35, 10), pady=(10,0))
        self.label = ctk.CTkLabel(master=self.frame1, text = (self.L('silperseg')), font = self.font)
        self.label.grid(row=0, column=0)
        self.tooltip = CTkToolTip(self.label, message=(self.L('silperseg2')), font = self.font)
        global max_sil
        max_sil = tk.IntVar()
        self.maxsil_box = ctk.CTkEntry(master=self.frame1, textvariable = max_sil, width = 40, font = self.font)
        self.maxsil_box.insert(0, "2")
        self.maxsil_box.grid(row=2)
        self.maxsil_slider = ctk.CTkSlider(master=self.frame1, from_=1, to=10, number_of_steps=10, variable=max_sil)
        self.maxsil_slider.set(2)
        self.maxsil_slider.grid(row=1)

        self.frame3 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_2')))
        self.frame3.grid(row=1, column=0, padx=(35, 10), pady=(40, 20))
        self.label = ctk.CTkLabel(master=self.frame3, text = (self.L('length_seg')), font = self.font)
        self.tooltip = CTkToolTip(self.label, message=(self.L('length_seg2')), font = self.font)
        self.label.grid(row=0, column=0)
        global max_seg_ln
        max_seg_ln = tk.DoubleVar()
        self.maxseg_box = ctk.CTkEntry(master=self.frame3, textvariable = max_seg_ln, width = 40, font = self.font)
        self.maxseg_box.insert(0, "2")
        self.maxseg_box.grid(row=2)
        self.maxseg_slider = ctk.CTkSlider(master=self.frame3, from_=2, to=20, number_of_steps=18, variable=max_seg_ln)
        self.maxseg_slider.set(2)
        self.maxseg_slider.grid(row=1)

        self.frame4 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_2')))
        self.frame4.grid(row=0, column=2, padx=(10, 35), pady=(20, 10), rowspan=2)
        self.estimatemidi = ctk.CTkLabel(master=self.frame4, text = (self.L('estmidi')), font = self.font)
        self.estimatemidi.grid(row=0, column=0, padx=5)
        self.midiframe = ctk.CTkFrame(master=self.frame4)
        self.midiframe.grid(row=0, column=1)
        self.estimatemidivar = tk.StringVar()
        self.estimatemidiA = ctk.CTkRadioButton(master=self.midiframe, text = (self.L('estmidiA')), value = 'default', variable = self.estimatemidivar, font = self.font)
        self.estimatemidiA.grid(row=0, sticky="w", padx=10)
        self.tooltip = CTkToolTip(self.estimatemidiA, message=(self.L('estmidiA2')), font=self.font)
        self.estimatemidiB = ctk.CTkRadioButton(master=self.midiframe, text = (self.L('estmidiB')), value = 'some', variable = self.estimatemidivar, font = self.font)
        self.estimatemidiB.grid(row=1, sticky="w", padx=10)
        self.tooltip = CTkToolTip(self.estimatemidiB, message=(self.L('estmidiB2')), font=self.font)
        self.estimatemidiC = ctk.CTkRadioButton(master=self.midiframe, text = (self.L('estmidiC')), value = 'off', variable = self.estimatemidivar, font = self.font)
        self.estimatemidiC.grid(row=2, sticky="w", padx=10)
        self.tooltip = CTkToolTip(self.estimatemidi, message=(self.L('estmidi2')), font = self.font)
        global estimate_midi
        estimate_midi = self.estimatemidivar
        self.detectbreathvar = tk.BooleanVar()
        self.detectbreath = ctk.CTkCheckBox(master=self.frame4, text = (self.L('detbre')), variable = self.detectbreathvar, font = self.font)
        self.detectbreath.deselect()
        self.detectbreath.grid(row=3, column=0, columnspan=2, pady=10)
        self.tooltip = CTkToolTip(self.detectbreath, message=(self.L('detbre2')), font = self.font)
        global detectbreath
        detectbreath = self.detectbreathvar
        self.button = ctk.CTkButton(master=self.frame4, text = (self.L('rawdata')), command = self.grab_raw_data, font = self.font)
        self.button.grid(row=4, column=0, columnspan=2)
        self.tooltip = CTkToolTip(self.button, message=(self.L('rawdata2')), font = self.font)
        self.button = ctk.CTkButton(master=self.tab(self.L('tab_ttl_2')), text = (self.L('prepdata')), command = self.run_segment, font = self.font)
        self.button.grid(row=4, column=1, pady=(5, 15))
        self.tooltip = CTkToolTip(self.button, message=(self.L('prepdata2')), font = self.font)

        ##CONFIG
        self.frame5 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_3')))
        self.frame5.grid(columnspan=3)
        self.label = ctk.CTkLabel(master=self.frame5, text=(self.L('type')), font = self.font)
        self.label.grid(row=0, column=0, rowspan=2, padx=15)
        self.trtype = tk.IntVar(value=0)
        self.acobutton = ctk.CTkRadioButton(master=self.frame5, text=(self.L('aco')), variable=self.trtype, value=1, font = self.font)
        self.acobutton.grid(row=0, column=1)
        self.varbutton = ctk.CTkRadioButton(master=self.frame5, text=(self.L('var')), variable=self.trtype, value=2, font = self.font)
        self.varbutton.grid(row=1, column=1)
        global trainselect
        trainselect = self.trtype

        global adv_on
        adv_on = tk.StringVar()
        self.advswitch = ctk.CTkSwitch(master=self.frame5, text=(self.L('adv')), variable=adv_on, onvalue="on", offvalue="off", command=self.changeState, font = self.font)
        self.advswitch.grid(row=0, column=2)
        self.tooltip = CTkToolTip(self.advswitch, message=(self.L('adv2')), font = self.font)
        global config_name
        config_name = tk.StringVar(value="enter_custom_name")
        self.confnamebox = ctk.CTkEntry(master=self.frame5, textvariable=config_name, state=tk.DISABLED, font = self.font)
        self.confnamebox.grid(row=1, column=2, padx=10)
        self.databutton = ctk.CTkButton(master=self.frame5, text=(self.L('datafolder')), command=self.grab_data_folder, font = self.font)
        self.databutton.grid(row=0, column=3, rowspan=2, padx=10)
        self.tooltip = CTkToolTip(self.databutton, message=(self.L('datafolder2')), font = self.font)
        self.ckptbutton = ctk.CTkButton(master=self.frame5, text=(self.L('savefolder')), command=self.ckpt_folder_save, font = self.font)
        self.ckptbutton.grid(row=0, column=4, rowspan=2, padx=(0,15))
        self.tooltip = CTkToolTip(self.ckptbutton, message=(self.L('savefolder2')), font = self.font)

        self.frame6 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_3')))
        self.frame6.grid(columnspan=1, row=1, pady=10)
        self.label = ctk.CTkLabel(master=self.frame6, text=(self.L('confsel')), font = self.font)
        self.label.grid(row=0, column=0, padx=15)
        self.tooltip = CTkToolTip(self.label, message=(self.L('confsel2')), font = self.font)
        global preset
        preset = ctk.StringVar()
        self.configbox = ctk.CTkComboBox(master=self.frame6, values=["1. Basic functions", "2. Pitch", "3. Breathiness/Energy", "4. BRE/ENE + Pitch", "5. Tension", "6. Tension + Pitch", "7. Kitchen Sink"], variable=preset, command=self.combobox_callback, state="readonly", font = self.font, dropdown_font = self.font)
        self.configbox.grid(row=0, column=1)
        self.label = ctk.CTkLabel(master=self.frame6, text=(self.L('advconfig')), font = self.font)
        self.label.grid(row=1, column=0, padx=15)
        self.tooltip = CTkToolTip(self.label, message=(self.L('advconfig2')), font = self.font)
        self.subframe = ctk.CTkFrame(master=self.frame6)
        self.subframe.grid(row=2, column=0, columnspan=2)
        global randaug
        randaug = tk.BooleanVar()
        self.confbox1 =  ctk.CTkCheckBox(master=self.subframe, text="gen", variable=randaug, onvalue = True, offvalue = False, state=tk.DISABLED, font = self.font)
        self.confbox1.grid(row=2, column=2, pady=5)
        self.tooltip = CTkToolTip(self.confbox1, message="random_pitch_shifting/use_key_shift_embed(gender)", font=self.font)
        global trainpitch
        trainpitch = tk.BooleanVar()
        self.confbox2 =  ctk.CTkCheckBox(master=self.subframe, text="pit", variable=trainpitch, onvalue = True, offvalue = False, state=tk.DISABLED, font = self.font)
        self.confbox2.grid(row=3, column=3, pady=5, padx=(0,3))
        self.tooltip = CTkToolTip(self.confbox2, message="predict_pitch", font=self.font)
        global trainbre
        trainbre = tk.BooleanVar()
        self.confbox3 =  ctk.CTkCheckBox(master=self.subframe, text="bre", variable=trainbre, onvalue = True, offvalue = False, state=tk.DISABLED, font = self.font)
        self.confbox3.grid(row=4, column=1, pady=5, padx=(3,0))
        self.tooltip = CTkToolTip(self.confbox3, message="use_breathiness_embed/predict_breathiness", font=self.font)
        global trainten
        trainten = tk.BooleanVar()
        self.confbox4 =  ctk.CTkCheckBox(master=self.subframe, text="ten", variable=trainten, onvalue = True, offvalue = False, state=tk.DISABLED, font = self.font)
        self.confbox4.grid(row=3, column=1, pady=5, padx=(3,0))
        self.tooltip = CTkToolTip(self.confbox4, message="use_tension_embed/predict_tension", font=self.font)
        global trainvoc
        trainvoc = tk.BooleanVar()
        self.confbox5 =  ctk.CTkCheckBox(master=self.subframe, text="voc", variable=trainvoc, onvalue = True, offvalue = False, state=tk.DISABLED, font = self.font)
        self.confbox5.grid(row=3, column=2, pady=5)
        self.tooltip = CTkToolTip(self.confbox5, message="use_voicing_embed/predict_voicing", font=self.font)
        global traindur
        traindur = tk.BooleanVar()
        self.confbox6 =  ctk.CTkCheckBox(master=self.subframe, text="dur", variable=traindur, onvalue = True, offvalue = False, state=tk.DISABLED, font = self.font)
        self.confbox6.grid(row=2, column=1, pady=5, padx=(3,0))
        self.tooltip = CTkToolTip(self.confbox6, message="predict_dur", font=self.font)
        global stretchaug
        stretchaug = tk.BooleanVar()
        self.confbox7 =  ctk.CTkCheckBox(master=self.subframe, text="vel", variable=stretchaug, onvalue = True, offvalue = False, state=tk.DISABLED, font = self.font)
        self.confbox7.grid(row=2, column=3, pady=5, padx=(0,3))
        self.tooltip = CTkToolTip(self.confbox7, message="random_time_stretching/use_speed_embed(velocity)", font=self.font)
        global trainene
        trainene = tk.BooleanVar()
        self.confbox8 =  ctk.CTkCheckBox(master=self.subframe, text="ene", variable=trainene, onvalue = True, offvalue = False, state=tk.DISABLED, font = self.font)
        self.confbox8.grid(row=4, column=2, pady=5)
        self.tooltip = CTkToolTip(self.confbox8, message="use_energy_embed/predict_energy", font=self.font)
        global preferds
        preferds = tk.BooleanVar()
        self.confbox9 = ctk.CTkCheckBox(master=self.subframe, text="prefer_ds", variable=preferds, onvalue = True, offvalue = False, state=tk.DISABLED, font = self.font)
        self.confbox9.grid(row=5, column=1, padx=(3,0), pady=5)
        global vr
        vr = tk.BooleanVar()
        self.confbox10 =  ctk.CTkCheckBox(master=self.frame6, text=(self.L('vr')), variable=vr, onvalue = True, offvalue = False, font = self.font)
        self.confbox10.grid(row=3, column=0, columnspan=2, pady=15)
        self.tooltip = CTkToolTip(self.confbox10, message=(self.L('vr2')), font = self.font)
        global backbone
        backbone = tk.StringVar()
        self.confbox11 = ctk.CTkComboBox(master=self.subframe, values=["lynxnet2", "wavenet", "lynxnet"], variable=backbone, font = self.font, dropdown_font = self.font)
        self.confbox11.set("lynxnet2")
        self.confbox11.configure(state="disabled")
        self.confbox11.grid(row=5, column=2, columnspan=2, pady=5)
        self.tooltip = CTkToolTip(self.confbox11, message=(self.L('wavenet2')), font = self.font)
        self.confbox12 = ctk.CTkCheckBox(master=self.subframe, text="dummy", state=tk.DISABLED, font=self.font)
        self.confbox12.grid(row=4, column=3, pady=5, padx=(0,3))
        self.tooltip = CTkToolTip(self.confbox12, message=(self.L('dummy')), font = self.font)

        self.frame14 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_3')))
        self.frame14.grid(columnspan=2, row=1, column=1, pady=10)
        self.label = ctk.CTkLabel(master=self.frame14, text=self.L('speaker'), font=self.font)
        self.label.grid(row=0, column=0, padx=20)
        self.label = ctk.CTkLabel(master=self.frame14, text=self.L('spk_lang'), font=self.font)
        self.label.grid(row=0, column=1, padx=20)
        self.tooltip = CTkToolTip(self.label, message=(self.L('spk_lang2')), font=self.font)
        self.label = ctk.CTkLabel(master=self.frame14, text=self.L('spk_id'), font=self.font)
        self.label.grid(row=0, column=2, padx=20)
        self.tooltip = CTkToolTip(self.label, message=(self.L('spk_id2')), font=self.font)
        self.subframe2 = ctk.CTkScrollableFrame(master=self.frame14, width=360)
        self.subframe2.grid(row=1, columnspan=3)
        self.langedit = ctk.CTkButton(master=self.frame14, text=(self.L('lang_edit')), command=self.langeditor, font=self.font)
        self.langedit.grid(row=2, column=1, pady=3)
        self.tooltip = CTkToolTip(self.langedit, message=(self.L('lang_edit2')), font=self.font)



        self.frame7 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_3')))
        self.frame7.grid(row=2, column=0)
        self.label = ctk.CTkLabel(master=self.frame7, text = (self.L('saveint')), font = self.font)
        self.label.grid(row=0, column=0)
        self.tooltip = CTkToolTip(self.label, message=(self.L('saveint2')), font = self.font)
        global save_int
        save_int = tk.IntVar()
        self.saveintbox = ctk.CTkEntry(master=self.frame7, textvariable = save_int, width = 60, font = self.font)
        self.saveintbox.insert(0, "2000")
        self.saveintbox.grid(row=2)
        self.saveintslider = ctk.CTkSlider(master=self.frame7, from_=1000, to=10000, number_of_steps=9, variable=save_int)
        self.saveintslider.set(2000)
        self.saveintslider.grid(row=1)

        self.frame8 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_3')))
        self.frame8.grid(row=2, column=1)
        self.label = ctk.CTkLabel(master=self.frame8, text = (self.L('maxbatch')), font = self.font)
        self.label.grid(row=0, column=0)
        self.tooltip = CTkToolTip(self.label, message=(self.L('maxbatch2')), font = self.font)
        global batch_size
        batch_size = tk.IntVar()
        self.batchbox = ctk.CTkEntry(master=self.frame8, textvariable = batch_size, width = 60, font = self.font)
        self.batchbox.insert(0, "9")
        self.batchbox.grid(row=2)
        self.batchslider = ctk.CTkSlider(master=self.frame8, from_=1, to=100, number_of_steps=99, variable=batch_size)
        self.batchslider.set(9)
        self.batchslider.grid(row=1)

        ctk.CTkButton(master=self.tab(self.L('tab_ttl_3')), text=(self.L('saveconf')), command=self.write_config, font = self.font).grid(row=2, column=2)

        ##PREPROCESS/TRAIN
        self.frame9 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_4')))
        self.frame9.grid(row=0, column=0, rowspan=2, columnspan=2, padx=120)
        self.loadbutton = ctk.CTkButton(master=self.frame9, text=("1. " + (self.L('step1'))), command=self.load_config_function, font = self.font)
        self.loadbutton.grid(row=0, column=0, padx=25, pady=25)
        self.tooltip = CTkToolTip(self.loadbutton, message=(self.L('step1-2')), font = self.font)
        self.savebutton = ctk.CTkButton(master=self.frame9, text=("2. " + (self.L('step2'))), command=self.ckpt_folder_save, font = self.font)
        self.savebutton.grid(row=0, column=1, padx=25, pady=25)
        self.tooltip = CTkToolTip(self.savebutton, message=(self.L('step2-2')), font = self.font)
        self.binarizebutton = ctk.CTkButton(master=self.frame9, text=("3a. " + (self.L('step3a'))), command=self.binarize, font = self.font)
        self.binarizebutton.grid(row=1, column=0, padx=25, pady=25)
        self.tooltip = CTkToolTip(self.binarizebutton, message=(self.L('step3a2')), font = self.font)
        self.trainbutton = ctk.CTkButton(master=self.frame9, text=("3b. " + (self.L('step3b'))), command=self.train_function, font = self.font)
        self.trainbutton.grid(row=1, column=1, padx=25, pady=25)
        self.frame10 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_4')))
        self.frame10.grid(row=2, column=0, pady=10)
        self.label = ctk.CTkLabel(master=self.frame10, text=(self.L('warning1')), font = self.font).grid(row=0, column=0)
        self.label = ctk.CTkLabel(master=self.frame10, text=(self.L('warning2')), font = self.font).grid(row=1, column=0)
        self.frame11 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_4')))
        self.frame11.grid(row=2, column=1)
        self.label = ctk.CTkLabel(master=self.frame11, text=(self.L('patchlabel')), font = self.font)
        self.label.grid()
        self.tooltip = CTkToolTip(self.label, message=(self.L('patchtip')), font = self.font)
        self.tensorpatch = ctk.CTkButton(master=self.frame11, text=(self.L('patchbutton')), command=self.tensor_patch, font = self.font)
        self.tensorpatch.grid()
        self.tooltip = CTkToolTip(self.tensorpatch, message=(self.L('patchtip')), font = self.font)

        ##EXPORT
        self.frame12 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_5')))
        self.frame12.grid(column=0, row=0, padx=90, pady=10)
        self.expselect_option = tk.IntVar(value=0)
        self.acobutton = ctk.CTkRadioButton(master=self.frame12, text=(self.L('aco')), variable=self.expselect_option, value=1, font = self.font)
        self.acobutton.grid(row=0, column=0, padx=10)
        self.tooltip = CTkToolTip(self.acobutton, message=(self.L('acotip')), font = self.font)
        self.varbutton = ctk.CTkRadioButton(master=self.frame12, text=(self.L('var')), variable=self.expselect_option, value=2, font = self.font)
        self.varbutton.grid(row=1, column=0, padx=10)
        self.tooltip = CTkToolTip(self.varbutton, message=(self.L('vartip')), font = self.font)
        global expselect
        expselect = self.expselect_option
        self.button = ctk.CTkButton(master=self.frame12, text=(self.L('step2')), command=self.ckpt_folder_save, font = self.font)
        self.button.grid(row=0, column=1, rowspan=2, padx=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('step2-2alt')), font = self.font)
        global onnx_folder
        onnx_folder = self.onnx_folder_save
        self.button = ctk.CTkButton(master=self.frame12, text=(self.L('onnx')), command=self.run_onnx_export, font = self.font)
        self.button.grid(row=0, column=2, rowspan=2, padx=10)
        self.frame13 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_5')))
        self.frame13.grid(row=3, column=0, pady=10)
        self.button = ctk.CTkButton(master=self.frame13, text=(self.L('getaco')), command=self.get_aco_folder, font = self.font)
        self.button.grid(row=0, column=0, padx=10, pady=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('getaco2')), font = self.font)
        global ou_name_var
        ou_name_var = tk.StringVar(value="enter_singer_name")
        self.namebox = ctk.CTkEntry(master=self.frame13, textvariable=ou_name_var, font = self.font)
        self.namebox.grid(row=1, column=0, padx=10, pady=10)
        self.tooltip = CTkToolTip(self.namebox, message=(self.L('namebox')), font = self.font)
        self.button = ctk.CTkButton(master=self.frame13, text=(self.L('vocoder')), command=self.get_vocoder, font = self.font)
        self.button.grid(row=2, column=0, padx=10, pady=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('vocoder2')), font = self.font)
        self.button = ctk.CTkButton(master=self.frame13, text=(self.L('getvar')), command=self.get_var_folder, font = self.font)
        self.button.grid(row=0, column=1, padx=10, pady=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('getaco2')), font = self.font)
        self.button = ctk.CTkButton(master=self.frame13, text=(self.L('ousave')), command=self.get_OU_folder, font = self.font)
        self.button.grid(row=1, column=1, padx=10, pady=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('ousave2')), font = self.font)
        self.button = ctk.CTkButton(master=self.frame13, text=(self.L('ouexport')), command=self.run_OU_config, font = self.font)
        self.button.grid(row=2, column=1, padx=10, pady=10)

        ##EXPORT 2 ELECTRIC BOOGALOO
        self.frame15 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_6')))
        self.frame15.grid(column=0, row=0, padx=90, pady=10)
        self.expselect_option2 = tk.IntVar(value=0)
        self.acobutton = ctk.CTkRadioButton(master=self.frame15, text=(self.L('aco')), variable=self.expselect_option2, value=1, font = self.font)
        self.acobutton.grid(row=0, column=0, padx=10)
        self.tooltip = CTkToolTip(self.acobutton, message=(self.L('acotip')), font = self.font)
        self.varbutton = ctk.CTkRadioButton(master=self.frame15, text=(self.L('var')), variable=self.expselect_option2, value=2, font = self.font)
        self.varbutton.grid(row=1, column=0, padx=10)
        self.tooltip = CTkToolTip(self.varbutton, message=(self.L('vartip')), font = self.font)
        global expselect2
        expselect2 = self.expselect_option2
        self.button = ctk.CTkButton(master=self.frame15, text=(self.L('step2')), command=self.ckpt_folder_save, font = self.font)
        self.button.grid(row=0, column=1, rowspan=2, padx=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('step2-2alt')), font = self.font)
        onnx_folder = self.onnx_folder_save
        self.button = ctk.CTkButton(master=self.frame15, text=(self.L('onnx')), command=self.run_onnx_export2, font = self.font)
        self.button.grid(row=0, column=2, rowspan=2, padx=10)
        self.frame16 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_6')))
        self.frame16.grid(row=3, column=0, pady=10)
        self.button = ctk.CTkButton(master=self.frame16, text=(self.L('aco')), command=self.get_aco_folder, font = self.font)
        self.button.grid(row=0, column=0, padx=10, pady=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('getaco2')), font = self.font)
        self.button = ctk.CTkButton(master=self.frame16, text=(self.L('var')), command=self.get_var_folder, font = self.font)
        self.button.grid(row=0, column=2, padx=10, pady=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('getaco2')), font = self.font)
        self.button = ctk.CTkButton(master=self.frame16, text=(self.L('dur')), command=self.get_dur_folder, font = self.font)
        self.button.grid(row=0, column=1, padx=10, pady=10)
        self.button = ctk.CTkButton(master=self.frame16, text=(self.L('pit')), command=self.get_pitch_folder, font = self.font)
        self.button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('getaco2')), font = self.font)
        global ou_name_var2
        ou_name_var2 = tk.StringVar(value="enter_singer_name")
        self.namebox = ctk.CTkEntry(master=self.frame16, textvariable=ou_name_var2, font = self.font)
        self.namebox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        self.tooltip = CTkToolTip(self.namebox, message=(self.L('namebox')), font = self.font)
        self.button = ctk.CTkButton(master=self.frame16, text=(self.L('vocoder_adv')), command=self.get_vocoder, font = self.font)
        self.button.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('vocoder2')), font = self.font)
        self.button = ctk.CTkButton(master=self.frame16, text=(self.L('ousave')), command=self.get_OU_folder, font = self.font)
        self.button.grid(row=2, column=1, columnspan=2, padx=10, pady=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('ousave2')), font = self.font)
        self.button = ctk.CTkButton(master=self.frame16, text=(self.L('ouexport')), command=self.run_adv_config, font = self.font)
        self.button.grid(row=3, column=1, padx=10, pady=10)

    #keeps the checkboxes in config tab locked until advanced config is enabled
    def changeState(self):
        print("Toggling advanced configuration", adv_on.get())
        if adv_on.get() == "on":
            self.confbox1.configure(state=tk.NORMAL)
            self.confbox2.configure(state=tk.NORMAL)
            self.confbox3.configure(state=tk.NORMAL)
            self.confbox4.configure(state=tk.NORMAL)
            self.confbox5.configure(state=tk.NORMAL)
            self.confbox6.configure(state=tk.NORMAL)
            self.confbox7.configure(state=tk.NORMAL)
            self.confbox8.configure(state=tk.NORMAL)
            self.confbox9.configure(state=tk.NORMAL)
            self.confbox11.configure(state=tk.NORMAL)
            self.confnamebox.configure(state=tk.NORMAL)
        elif adv_on.get() == "off":
            self.confbox1.configure(state=tk.DISABLED)
            self.confbox2.configure(state=tk.DISABLED)
            self.confbox3.configure(state=tk.DISABLED)
            self.confbox4.configure(state=tk.DISABLED)
            self.confbox5.configure(state=tk.DISABLED)
            self.confbox6.configure(state=tk.DISABLED)
            self.confbox7.configure(state=tk.DISABLED)
            self.confbox8.configure(state=tk.DISABLED)
            self.confbox9.configure(state=tk.DISABLED)
            self.confbox11.configure(state=tk.DISABLED)
            self.confnamebox.configure(state=tk.DISABLED)
        else:
            self.confbox1.configure(state=tk.DISABLED)
            self.confbox2.configure(state=tk.DISABLED)
            self.confbox3.configure(state=tk.DISABLED)
            self.confbox4.configure(state=tk.DISABLED)
            self.confbox5.configure(state=tk.DISABLED)
            self.confbox6.configure(state=tk.DISABLED)
            self.confbox7.configure(state=tk.DISABLED)
            self.confbox8.configure(state=tk.DISABLED)
            self.confbox9.configure(state=tk.DISABLED)
            self.confbox11.configure(state=tk.DISABLED)
            self.confnamebox.configure(state=tk.DISABLED)

    #checks and unchecks boxes based on selected config
    def combobox_callback(self, choice):
        print("Configuration selected:", choice)
        if choice == "1. Basic functions":
            self.confbox1.select()
            self.confbox2.deselect()
            self.confbox3.deselect()
            self.confbox4.deselect()
            self.confbox5.deselect()
            self.confbox6.select()
            self.confbox7.select()
            self.confbox8.deselect()
        elif choice == "2. Pitch":
            self.confbox1.select()
            self.confbox2.select()
            self.confbox3.deselect()
            self.confbox4.deselect()
            self.confbox5.deselect()
            self.confbox6.select()
            self.confbox7.select()
            self.confbox8.deselect()
        elif choice == "3. Breathiness/Energy":
            self.confbox1.select()
            self.confbox2.deselect()
            self.confbox3.select()
            self.confbox4.deselect()
            self.confbox5.deselect()
            self.confbox6.select()
            self.confbox7.select()
            self.confbox8.select()
        elif choice == "4. BRE/ENE + Pitch":
            self.confbox1.select()
            self.confbox2.select()
            self.confbox3.select()
            self.confbox4.deselect()
            self.confbox5.deselect()
            self.confbox6.select()
            self.confbox7.select()
            self.confbox8.select()
        elif choice == "5. Tension":
            self.confbox1.select()
            self.confbox2.deselect()
            self.confbox3.deselect()
            self.confbox4.select()
            self.confbox5.deselect()
            self.confbox6.select()
            self.confbox7.select()
            self.confbox8.deselect()
        elif choice == "6. Tension + Pitch":
            self.confbox1.select()
            self.confbox2.select()
            self.confbox3.deselect()
            self.confbox4.select()
            self.confbox5.deselect()
            self.confbox6.select()
            self.confbox7.select()
            self.confbox8.deselect()
        elif choice == "7. Kitchen Sink":
            self.confbox1.select()
            self.confbox2.select()
            self.confbox3.select()
            self.confbox4.select()
            self.confbox5.select()
            self.confbox6.select()
            self.confbox7.select()
            self.confbox8.deselect()
        else:
            print("Please select a preset or enable custom configuration!")

    #runs a command through env A
    global run_cmdA
    def run_cmdA(cmd):
        if is_windows():
            cmd = f'{conda_path} activate difftrainerA >nul && {cmd}'
        elif is_linux() or is_macos():
            cmd = f'eval "$(conda shell.bash hook)" && {conda_path} activate difftrainerA && {cmd}'
        try:
            subprocess.run(cmd, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")

    #runs a command through env B
    global run_cmdB
    def run_cmdB(cmd):
        if is_windows():
            cmd = f'{conda_path} activate difftrainerB >nul && {cmd}'
        elif is_linux() or is_macos():
            cmd = f'eval "$(conda shell.bash hook)" && {conda_path} activate difftrainerB && {cmd}'
        try:
            subprocess.run(cmd, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")

###COMMANDS###
    global all_shits_not_wav_n_lab
    all_shits_not_wav_n_lab = "raw_data/diffsinger_db"

    def refresh(self, choice, master):
        # Better option for updating the display language tbh.
        guisettings['lang'] = choice
        with open('assets/guisettings.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(guisettings, f, default_flow_style=False)
            f.close()
        self.L.load_lang(choice)

        print(f'Set display language to {choice}')

        self.destroy()
        create_widgets

    def credit(self, url):
        webbrowser.open_new(url)

    #stops everything from dying when anything touched a Mac
    def is_hidden_folder(folder):
        return folder.startswith('.')

    def dl_update(self):
        if not os.path.exists(all_shits_not_wav_n_lab):
          os.makedirs(all_shits_not_wav_n_lab)
        uta_url = "https://github.com/UtaUtaUtau/nnsvs-db-converter/archive/refs/heads/main.zip"
        uta_zip = os.path.join(os.getcwd(), uta_url.split("/")[-1])
        uta_script_folder_name = "nnsvs-db-converter-main"

        diffsinger_url = "https://github.com/agentasteriski/DiffSinger/archive/refs/heads/muon_lynxnet2.zip"
        diffsinger_zip = os.path.join(os.getcwd(), diffsinger_url.split("/")[-1])
        diffsinger_script_folder_name = "DiffSinger-muon_lynxnet2"

        vocoder_url = "https://github.com/openvpi/vocoders/releases/download/pc-nsf-hifigan-44.1k-hop512-128bin-2025.02/pc_nsf_hifigan_44.1k_hop512_128bin_2025.02.zip"
        vocoder_zip = os.path.join(os.getcwd(), vocoder_url.split("/")[-1])
        vocoder_folder = "DiffSinger/checkpoints"

        oldvocoder_url = "https://github.com/openvpi/vocoders/releases/download/nsf-hifigan-44.1k-hop512-128bin-2024.02/nsf_hifigan_44.1k_hop512_128bin_2024.02.zip"
        oldvocoder_zip = os.path.join(os.getcwd(), oldvocoder_url.split("/")[-1])

        rmvpe_url = "https://github.com/yxlllc/RMVPE/releases/download/230917/rmvpe.zip"
        rmvpe_zip = os.path.join(os.getcwd(), rmvpe_url.split("/")[-1])
        rmvpe_subfolder_name = "DiffSinger/checkpoints/rmvpe"
        os.makedirs(rmvpe_subfolder_name, exist_ok = True)

        vr_url = "https://github.com/yxlllc/vocal-remover/releases/download/hnsep_240512/hnsep_240512.zip"
        vr_zip = os.path.join(os.getcwd(), vr_url.split("/")[-1])
        vr_subfolder_name = "DiffSinger/checkpoints"
        os.makedirs(vr_subfolder_name, exist_ok = True)

        SOME_url = "https://github.com/openvpi/SOME/releases/download/v1.0.0-baseline/0119_continuous128_5spk.zip"
        SOME_zip = os.path.join(os.getcwd(), SOME_url.split("/")[-1])
        SOME_subfolder_name = "DiffSinger/checkpoints/SOME"
        os.makedirs(SOME_subfolder_name, exist_ok = True)

        SOME_url2 = "https://github.com/agentasteriski/SOME-lite/archive/refs/heads/main.zip"
        SOME_zip2 = os.path.join(os.getcwd(), SOME_url2.split("/")[-1])

        dicts_url = "https://github.com/agentasteriski/difftrainer-dictfiles/archive/refs/heads/main.zip"
        dicts_zip = os.path.join(os.getcwd(), dicts_url.split("/")[-1])
        dicts_subfolder_name = "DiffSinger/dictionaries"
        dicts_subsubfolder = os.path.join(dicts_subfolder_name, "difftrainer-dictfiles-main")

        if os.path.exists("nnsvs-db-converter") or os.path.exists("DiffSinger"):
            user_response = messagebox.askyesno("File Exists", "Necessary files already exist. Do you want to re-download and replace them? Make sure any user files are backed up OUTSIDE of the DiffSinger folder.")
            if not user_response:
                return

            if os.path.exists("nnsvs-db-converter"):
                try:
                    shutil.rmtree("nnsvs-db-converter")
                except Exception as e:
                    print(f"Error deleting the existing 'nnsvs-db-converter' folder: {e}")

            if os.path.exists("DiffSinger"):
                try:
                    shutil.rmtree("DiffSinger")
                except Exception as e:
                    print(f"Error deleting the existing 'DiffSinger' folder: {e}")
            if os.path.exists("SOME"):
                try:
                    shutil.rmtree("SOME")
                except Exception as e:
                    print(f"Error deleting the existing 'SOME' folder: {e}")
            if os.path.exists("dictionaries2"):
                try:
                    shutil.rmtree("dictionaries2")
                except Exception as e:
                    print(f"Error deleting the existing 'dictionaries2' folder: {e}")

        response = requests.get(uta_url, stream = True)
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(total = total_size, unit = "B", unit_scale = True, desc = "downloading nnsvs-db-converter") as progress_bar:
            with open("main.zip", "wb") as f:
                for chunk in response.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
        with zipfile.ZipFile(uta_zip, "r") as zip_ref:
            zip_ref.extractall()
        os.remove(uta_zip)
        if os.path.exists(uta_script_folder_name):
            os.rename(uta_script_folder_name, "nnsvs-db-converter") #renaming stuff cus i dont wanna change my path from the nb much

        response = requests.get(diffsinger_url, stream = True)
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(total = total_size, unit = "B", unit_scale = True, desc = "downloading DiffSinger") as progress_bar:
            with open("muon_lynxnet2.zip", "wb") as f:
                for chunk in response.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))

        with zipfile.ZipFile(diffsinger_zip, "r") as zip_ref:
            zip_ref.extractall()
        os.remove(diffsinger_zip)
        if os.path.exists(diffsinger_script_folder_name):
            os.rename(diffsinger_script_folder_name, "DiffSinger") #this beech too


        response = requests.get(vocoder_url, stream = True)
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(total = total_size, unit = "B", unit_scale = True, desc = "downloading PC-NSF-HifiGAN") as progress_bar:
            with open("pc_nsf_hifigan_44.1k_hop512_128bin_2025.02.zip", "wb") as f:
                for chunk in response.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
        with zipfile.ZipFile(vocoder_zip, "r") as zip_ref:
            zip_ref.extractall(vocoder_folder)
        os.remove(vocoder_zip)

        response = requests.get(oldvocoder_url, stream = True)
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(total = total_size, unit = "B", unit_scale = True, desc = "downloading previous NSF-HifiGAN for compatibility") as progress_bar:
            with open("nsf_hifigan_44.1k_hop512_128bin_2024.02.zip", "wb") as f:
                for chunk in response.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
        with zipfile.ZipFile(oldvocoder_zip, "r") as zip_ref:
            zip_ref.extractall(vocoder_folder)
        os.remove(oldvocoder_zip)

        response = requests.get(rmvpe_url, stream = True)
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(total = total_size, unit = "B", unit_scale = True, desc = "downloading RMVPE") as progress_bar:
            with open("rmvpe.zip", "wb") as f:
                for chunk in response.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
        with zipfile.ZipFile(rmvpe_zip, "r") as zip_ref:
            zip_ref.extractall(rmvpe_subfolder_name)
        os.remove(rmvpe_zip)

        response = requests.get(vr_url, stream = True)
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(total = total_size, unit = "B", unit_scale = True, desc = "downloading VR") as progress_bar:
            with open("hnsep_240512.zip", "wb") as f:
                for chunk in response.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
        with zipfile.ZipFile(vr_zip, "r") as zip_ref:
            zip_ref.extractall(vr_subfolder_name)
        os.remove(vr_zip)

        response = requests.get(SOME_url, stream = True)
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(total = total_size, unit = "B", unit_scale = True, desc = "downloading SOME model") as progress_bar:
            with open("0119_continuous128_5spk.zip", "wb") as f:
                for chunk in response.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
        with zipfile.ZipFile(SOME_zip, "r") as zip_ref:
            zip_ref.extractall(SOME_subfolder_name)
        os.remove(SOME_zip)

        response = requests.get(SOME_url2, stream = True)
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(total = total_size, unit = "B", unit_scale = True, desc = "downloading SOME scripts") as progress_bar:
            with open("main.zip", "wb") as f:
                for chunk in response.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
        with zipfile.ZipFile(SOME_zip2, "r") as zip_ref:
            zip_ref.extractall()
        os.remove(SOME_zip2)
        if os.path.exists("SOME-lite-main"):
            os.rename("SOME-lite-main", "SOME") #this beech too
        
        response = requests.get(dicts_url, stream = True)
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(total = total_size, unit = "B", unit_scale = True, desc = "downloading dictionary files") as progress_bar:
            with open("main.zip", "wb") as f:
                for chunk in response.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
        with zipfile.ZipFile(dicts_zip, "r") as zip_ref:
            zip_ref.extractall(dicts_subfolder_name)
        os.remove(dicts_zip)
        for filename in os.listdir(dicts_subsubfolder):
            source = os.path.join(dicts_subsubfolder, filename)
            dest = os.path.join(dicts_subfolder_name, filename)
            if os.path.isfile(source):
                shutil.copy(source, dest)
        shutil.rmtree(dicts_subsubfolder, ignore_errors=False)

        if os.path.exists("db_converter_config.yaml"):
            os.remove("db_converter_config.yaml")

        converter_config = {
            "use_cents": True,
            "time_step": 0.005,
            "f0_min": 40,
            "f0_max": 1200,
            "audio_sample_rate": 44100,
            "voicing_treshold_midi": 0.45,
            "voicing_treshold_breath": 0.6,
            "breath_window_size": 0.05,
            "breath_min_length": 0.1,
            "breath_db_threshold": -60,
            "breath_centroid_treshold": 2000,
            "max-length-relaxation-factor": 0.1,
            "pitch-extractor": "parselmouth",
            "write_label": "htk"
        }
        with open("db_converter_config.yaml", "w", encoding = "utf-8") as config:
            yaml.dump(converter_config, config)

        print("Adding the secret sauce...")
        with open("DiffSinger/configs/base.yaml", "r", encoding = "utf-8") as config1:
            base_config = yaml.safe_load(config1)
        base_config["pe"] = "rmvpe"
        base_config["f0_max"] = 1600
        with open("DiffSinger/configs/base.yaml", "w", encoding = "utf-8") as config1:
            yaml.dump(base_config, config1, default_flow_style=False, sort_keys=False)
        with open("DiffSinger/configs/acoustic.yaml", "r", encoding = "utf-8") as config2:
            aco_config = yaml.safe_load(config2)
        aco_config["main_loss_type"] = "l1"
        aco_config["tension_smooth_width"] = 0.06 #original default 0.12, lowering it reduces vocal modes coming out the same
        aco_config["voicing_smooth_width"] = 0.06
        aco_config["breathiness_smooth_width"] = 0.06
        aco_config["energy_smooth_width"] = 0.06
        aco_config["diff_accelerator"] = "unipc"
        aco_config["augmentation_args"]["random_pitch_shifting"]["range"] = [-3.0, 3.0]
        aco_config["augmentation_args"]["random_pitch_shifting"]["scale"] = 0.25
        with open("DiffSinger/configs/acoustic.yaml", "w", encoding = "utf-8") as config2:
            yaml.dump(aco_config, config2, default_flow_style=False, sort_keys=False)
        with open("DiffSinger/configs/variance.yaml", "r", encoding = "utf-8") as config3:
            var_config = yaml.safe_load(config3)
        var_config["main_loss_type"] = "l1"
        var_config["tension_logit_max"] = 8 #nobody is hitting the original default, lowering this reduces the nastiness at high tension(tbh could/should still go lower for a lot of people)
        var_config["tension_logit_min"] = -8 #haven't heard as many issues with low tension but just for good measure
        var_config["tension_smooth_width"] = 0.06 
        var_config["voicing_smooth_width"] = 0.06
        var_config["breathiness_smooth_width"] = 0.06
        var_config["energy_smooth_width"] = 0.06
        var_config["diff_accelerator"] = "unipc"
        with open("DiffSinger/configs/variance.yaml", "w", encoding = "utf-8") as config3:
            yaml.dump(var_config, config3, default_flow_style=False, sort_keys=False)
        new_f0_max=1600
        with open("DiffSinger/utils/binarizer_utils.py", "r", encoding = "utf-8") as f:
            f0_read = f.read()
        up_f0_val = re.sub(r"f0_max\s*=\s*.*", f"f0_max={new_f0_max},", f0_read)
        with open("DiffSinger/utils/binarizer_utils.py", "w", encoding = "utf-8") as f:
            f.write(up_f0_val)

        #no idea how to do this on other OS and honestly idc, it's here for the bit
        if is_windows():
            subprocess.check_call(["powershell", "-c", f'(New-Object Media.SoundPlayer "{main_path}/assets/setup_complete.wav").PlaySync();'])

        print("Setup Complete!")



    def grab_raw_data(self):
        self.all_shits = filedialog.askdirectory(title="Select raw data folder", initialdir = "raw_data")
        if not os.path.exists(all_shits_not_wav_n_lab):
            os.makedirs(all_shits_not_wav_n_lab)
        print("raw data path: " + self.all_shits)

    #oldest code in the whole thing, questionable phoneme behavior, idk what the purpose of liquids/vowels.txt even is
    def run_segment(self):
            if not self.all_shits:
                messagebox.showinfo("Required", "Please select a a folder containing raw data folder(s) first")
                return
            messagebox.showinfo("Warning", 'This process will remove the original .wav and .lab files, please be sure to make a backup for your data before pressing "OK" or closing this window')
            print("\n")
            print("process running...")
            print("editing necessary phonemes for db converter...")
            # incase if user labeled SP as pau but i think utas script already account SP so meh
            try:
                for root, dirs, files in os.walk(self.all_shits):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for filename in files:
                        if filename.endswith(".lab"):
                            file_path = os.path.join(root, filename)
                            with open(file_path, "r", encoding = "utf-8") as file:
                                file_data = file.read()
                            file_data = file_data.replace("SP", "pau")
                            file_data = file_data.replace("br", "AP") #it needs AP instead of br, but if users didnt label breath then whoop their lost
                            with open(file_path, "w", encoding = "utf-8") as file:
                                file.write(file_data)
                # for funny auto dict generator lmao
                print("generating dictionary from phonemes...")
                out = "DiffSinger/dictionaries/custom_dict.txt"
            except Exception as e:
                    print(f"Error during dictionary generation: {e}")

            phonemes = set()

            def is_excluded(phoneme):
                return phoneme in ["pau", "AP", "SP", "sil"]

            try:
                phoneme_folder_path = self.all_shits
                for root, dirs, files in os.walk(phoneme_folder_path):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for file in files:
                        if file.endswith(".lab"):
                            fpath = os.path.join(root, file)
                            with open(fpath, "r", encoding = "utf-8") as lab_file:
                                for line in lab_file:
                                    line = line.strip()
                                    if line:
                                        phoneme = line.split()[2]
                                        if not is_excluded(phoneme):
                                            phonemes.add(phoneme)
                phoneme_folder_path = all_shits_not_wav_n_lab
                for root, dirs, files in os.walk(phoneme_folder_path):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for file in files:
                        if file.endswith(".csv"):
                            fpath = os.path.join(root, file)
                            with open(fpath, "r", newline="", encoding = "utf-8") as csv_file:
                                csv_reader = csv.DictReader(csv_file)
                                for row in csv_reader:
                                    if "ph_seq" in row:
                                        ph_seq = row["ph_seq"].strip()
                                        for phoneme in ph_seq.split():
                                            if not is_excluded(phoneme):
                                                phonemes.add(phoneme)
                phoneme_folder_path = self.all_shits
                for root, dirs, files in os.walk(phoneme_folder_path):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for file in files:
                        if file.endswith(".json"):
                            fpath = os.path.join(root, file)
                            with open(fpath, "r", encoding = "utf-8") as json_file:
                                row = json.load(json_file)
                                ph_seq = row["ph_seq"]
                                for phoneme in ph_seq.split():
                                    if not is_excluded(phoneme):
                                        phonemes.add(phoneme)

                with open(out, "w", encoding = "utf-8") as f:
                    for phoneme in sorted(phonemes):
                        f.write(phoneme + "\t" + phoneme + "\n")

                # for vowels and consonants.txt.... well adding luquid type for uta's script
                dict_path = out
                vowel_types = {"a", "i", "u", "e", "o", "N", "M", "NG"}
                liquid_types = {"y", "w", "l", "r"} # r for english labels, it should be fine with jp too
                vowel_data = []
                consonant_data = []
                liquid_data = []

                with open(dict_path, "r", encoding = "utf-8") as f:
                    for line in f:
                        phoneme, _ = line.strip().split("\t")
                        if phoneme[0] in vowel_types:
                            vowel_data.append(phoneme)
                        elif phoneme[0] in liquid_types:
                            liquid_data.append(phoneme)
                        else:
                            consonant_data.append(phoneme)

                vowel_data.sort()
                liquid_data.sort()
                consonant_data.sort()
                directory = os.path.dirname(dict_path)

                # make txt for language json file
                print("writing vowels.txt...")
                vowel_txt_path = os.path.join(directory, "vowels.txt")
                with open(vowel_txt_path, "w", encoding = "utf-8") as f:
                    f.write(" ".join(vowel_data))
                print("writing liquids.txt...")
                liquid_txt_path = os.path.join(directory, "liquids.txt")
                with open(liquid_txt_path, "w", encoding = "utf-8") as f:
                    f.write(" ".join(liquid_data))
                print("writing consonants.txt...")
                consonant_txt_path = os.path.join(directory, "consonants.txt")
                with open(consonant_txt_path, "w", encoding = "utf-8") as f:
                    f.write(" ".join(consonant_data))

                # here's a funny json append
                with open(vowel_txt_path, "r", encoding="utf-8") as f:
                    vowel_data = f.read().split()
                with open(liquid_txt_path, "r", encoding = "utf-8") as f:
                    liquid_data = f.read().split()
                with open(consonant_txt_path, "r", encoding = "utf-8") as f:
                    consonant_data = f.read().split()
                liquid_list = {liquid: True for liquid in liquid_data} #temp fix, might need more research about the push in timing'''
                phones4json = {"vowels": vowel_data, "liquids": liquid_list}
                with open("nnsvs-db-converter/lang.sample.json", "w", encoding = "utf-8") as rawr:
                    json.dump(phones4json, rawr, indent=4)
            except Exception as e:
                    print(f"Error during preparation: {e}")
            try:
                with open("db_converter_config.yaml", "r", encoding = "utf-8") as config:
                    converter = yaml.safe_load(config)
            except Exception as e:
                    print(f"Error opening db_converter_config: {e}")

            max_silence = max_sil.get()
            max_wav_length = max_seg_ln.get()

            try:
                for raw_folder_name in os.listdir(self.all_shits):
                    raw_folder_path = os.path.join(self.all_shits, raw_folder_name)
                    raw_folder_path = os.path.normpath(raw_folder_path)
                    # Exclude .DS_Store and any other hidden files or directories
                    if raw_folder_name.startswith('.'):
                        continue
                    if any(filename.endswith(".lab") for filename in os.listdir(raw_folder_path)):
                        print("segmenting data...")
                        #dear god please work
                        converterpy = os.path.join("nnsvs-db-converter", "db_converter.py")
                        cmdstage = ["python", converterpy, '-l', str(max_wav_length), '-s', str(max_silence), '-L', 'nnsvs-db-converter/lang.sample.json', '-F', '1600', "--folder", raw_folder_path]
                        if self.estimatemidivar.get() == "default":
                            estimate_midi_print = "Default"
                            cmdstage.append("-m")
                            cmdstage.append("-D")
                            cmdstage.append("-c")
                        elif self.estimatemidivar.get() == "some":
                            estimate_midi_print = "SOME"
                        else:
                            estimate_midi_print = "Off"
                        if self.detectbreathvar.get() == True:
                            cmdstage.append('-B')
                            cmdstage.append("-v")
                            cmdstage.append(str(converter["voicing_treshold_breath"]))
                            cmdstage.append("-W")
                            cmdstage.append(str(converter["breath_window_size"]))
                            cmdstage.append("-b")
                            cmdstage.append(str(converter["breath_min_length"]))
                            cmdstage.append("-e")
                            cmdstage.append(str(converter["breath_db_threshold"]))
                            cmdstage.append("-C")
                            cmdstage.append(str(converter["breath_centroid_treshold"]))
                            detect_breath_print = "True"
                        else:
                            detect_breath_print = "False"
                        if converter["write_label"] == False:
                            write_label_print = "Not writing labels"
                        elif converter["write_label"] == "htk":
                            cmdstage.append("-w htk")
                            write_label_print = "Write HTK labels"
                        elif converter["write_label"] == "aud":
                            cmdstage.append("-w aud")
                            write_label_print = "Write Audacity labels"
                        else:
                            write_label_print = "unknown value, not writing labels"
                        command = " ".join(cmdstage)
                        print("\n",
                            "##### Converter Settings #####\n",
                            f"max audio segment length: {str(max_wav_length)}\n",
                            f"max silence amount: {str(max_silence)}\n",
                            f"estimate midi: {estimate_midi_print}\n",
                            f"detect breath: {detect_breath_print}\n",
                            f"export label: {write_label_print}\n"
                            )
                        run_cmdA(command)
            except Exception as e:
                print(f"Error during segmentation: {e}")
            try:
                    #this for folder organization / raw data cleanup
                    for raw_folder_name in os.listdir(self.all_shits):
                        # Exclude .DS_Store and any other hidden files or directories
                        if raw_folder_name.startswith('.'):
                            continue
                        raw_folder_path = os.path.join(self.all_shits, raw_folder_name)
                        raw_folder_path = os.path.normpath(raw_folder_path)
                        for filename in os.listdir(raw_folder_path):
                            if filename.endswith(".wav") or filename.endswith(".lab"):
                                os.remove(os.path.join(raw_folder_path, filename))
                        diff_singer_db_path = os.path.join(raw_folder_path, "diffsinger_db")
                        for stuff in os.listdir(diff_singer_db_path):
                            stuff_path = os.path.join(diff_singer_db_path, stuff)
                            singer_folder_dat_main = os.path.join(raw_folder_path, stuff)
                            if os.path.isfile(stuff_path):
                                shutil.move(stuff_path, singer_folder_dat_main)
                            elif os.path.isdir(stuff_path):
                                shutil.move(stuff_path, singer_folder_dat_main)
                        shutil.rmtree(diff_singer_db_path)
            except Exception as e:
                    print(f"Error during file cleanup: {e}")
            try:
                    if self.estimatemidivar.get() == "some":
                        for speaker in os.listdir(self.all_shits):
                            if speaker.startswith('.'):
                                continue
                            speaker_path = os.path.join(self.all_shits, speaker)
                            if os.path.isdir(speaker_path):
                                print("loading SOME...")
                                cmdstage = ["python", "SOME/batch_infer.py", "--model", "DiffSinger/checkpoints/SOME/0119_continuous256_5spk/model_ckpt_steps_100000_simplified.ckpt", "--dataset", speaker_path, "--overwrite"]
                                command2 = " ".join(cmdstage)
                                run_cmdA(command2)
                    else:
                        pass
            except Exception as e:
                    print(f"Error during SOME pitch generation: {e}")
            print("data segmentation complete!")

    def grab_data_folder(self):
        global data_folder
        data_folder = filedialog.askdirectory(title="Select data folder", initialdir = "DiffSinger")
        print("data path: " + data_folder)
        if data_folder:
            self.load_spk(data_folder)

    def load_spk(self, data_folder):
        for widget in self.subframe2.winfo_children():
            widget.destroy()
        self.spk_info = {}
        spk_folders = [f for f in os.listdir(data_folder) if os.path.isdir(os.path.join(data_folder, f)) and not f.startswith('.')]
        spk_rows = []
        for spk in spk_folders:
            folder_to_id = {spk: i for i, spk in enumerate(spk_folders)}
            folder_name = os.path.basename(spk)
            folder_id = folder_to_id.get(folder_name, -1)
            raw_dir = os.path.join(data_folder, folder_name)
            spk_rows.append(ctk.CTkFrame(master=self.subframe2, width=340))
            spk_rows[folder_id].grid(row=folder_id,sticky="EW", pady=3)
            spk_name_box = ctk.CTkEntry(master=spk_rows[folder_id], width=100, font = self.font)
            spk_name_box.insert(0, folder_name)
            spk_name_box.grid(column=0, row=0, padx=15, pady=3)
            #default selectable languages currently match localizations
            #might change it to the default phoneme lists instead
            #does a Swedish DiffSinger even exist yet?
            spk_lang_select = ctk.CTkComboBox(master=spk_rows[folder_id], values = ["other", "en", "ja", "zh", "ko", "es", "pt", "sv", "tl"], font = self.font)
            spk_lang_select.grid(column=1, row=0, padx=10)
            spk_id_select = ctk.CTkEntry(master=spk_rows[folder_id], width = 20, font = self.font)
            spk_id_select.insert(0, folder_id)
            spk_id_select.grid(column=2, row=0, padx=15)
            self.spk_info[spk] =(raw_dir, folder_name, spk_lang_select, spk_id_select)


    def ckpt_folder_save(self):
        global ckpt_save_dir
        ckpt_save_dir = filedialog.askdirectory(title="Select save folder", initialdir = "DiffSinger/checkpoints")
        self.binary_save_dir = os.path.join(ckpt_save_dir, "binary")
        print("save path: " + ckpt_save_dir)

    def write_config(self):
        #adding checks lmao make sure they select them
        config_check = trainselect.get()
        if not config_check:
            messagebox.showinfo("Required", "Please select a config type")
            return
        if not data_folder:
            messagebox.showinfo("Required", "Please select a folder containing data folder(s)")
            return
        if not ckpt_save_dir:
            messagebox.showinfo("Required", "Please select a save directory")
            return
        print("writing config...")

        enable_random_aug = randaug.get()
        enable_stretch_aug = stretchaug.get()
        duration = traindur.get()
        breathiness = trainbre.get()
        energy = trainene.get()
        pitch = trainpitch.get()
        tension = trainten.get()
        voicing = trainvoc.get()
        pre_type = vr.get()
        ds = preferds.get()
        backbone_type = backbone.get()
        save_interval = save_int.get()
        batch = batch_size.get()
        selected_config_type = trainselect.get()
        allspeakers = []

        for spk, (raw_dir, folder_name, spk_lang_select, spk_id_select) in self.spk_info.items():
            spk_lang = spk_lang_select.get()
            merged_id = int(spk_id_select.get())
            num_spk = merged_id +1
            prefixes = []
            trns = os.path.join(raw_dir, 'transcriptions.csv')
            with open(trns, "r", newline="", encoding = "utf-8") as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader, None)
                for row in csv_reader:
                    if len(row) > 0:
                        prefixes.append(row[0])
                try: test_prefixes = random.sample(prefixes, 3)
                except ValueError: 
                    raise ValueError(f"{self.L('sampleerror')} {spk}!")
                #tried using less than 3 way back and it just errored, not sure what I'm missing there
            spk_block = {
                "raw_data_dir": raw_dir,
                "speaker": folder_name,
                "spk_id": merged_id,
                "language": spk_lang,
                "test_prefixes": test_prefixes
                }
            allspeakers.append(spk_block)


        if selected_config_type == 1:
            with open("DiffSinger/dictionaries/langloader.yaml", "r", encoding = "utf=8") as langloader:
                lang = yaml.safe_load(langloader)
            merged_loc = os.path.join("DiffSinger/dictionaries", lang["merge_list"])
            with open(merged_loc, "r", encoding = "utf-8") as merge_list:
                merges = yaml.safe_load(merge_list)
            with open("DiffSinger/configs/acoustic.yaml", "r", encoding = "utf-8") as config:
                bitch_ass_config = yaml.safe_load(config)
            bitch_ass_config["datasets"] = allspeakers
            bitch_ass_config["num_spk"] = num_spk
            if num_spk > 1:
                bitch_ass_config["use_spk_id"] = True
            else:
                bitch_ass_config["use_spk_id"] = False
            bitch_ass_config["binary_data_dir"] = self.binary_save_dir
            bitch_ass_config["dictionaries"] = lang["dictionaries"]
            bitch_ass_config["num_lang"] = len(lang["dictionaries"])
            if len(lang["dictionaries"]) == 1:
                bitch_ass_config["use_lang_id"] = False
            else:
                bitch_ass_config["use_lang_id"] = True
            bitch_ass_config["extra_phonemes"] = lang["extra_phonemes"]
            bitch_ass_config["merged_phoneme_groups"] = merges["merged_phoneme_groups"]
            bitch_ass_config["augmentation_args"]["random_pitch_shifting"]["enabled"] = enable_random_aug
            bitch_ass_config["augmentation_args"]["random_time_stretching"]["enabled"] = enable_stretch_aug
            bitch_ass_config["use_key_shift_embed"] = enable_random_aug
            bitch_ass_config["use_speed_embed"] = enable_stretch_aug
            bitch_ass_config["max_batch_size"] = int(batch)
            #ive never tried reaching the limit so ill trust kei's setting for this(MLo7)
            #sounds like a lot of users can go higher but 9 is a good start(Aster)
            bitch_ass_config["val_check_interval"] = int(save_interval)
            bitch_ass_config["use_energy_embed"] = energy
            bitch_ass_config["use_breathiness_embed"] = breathiness
            bitch_ass_config["use_tension_embed"] = tension
            bitch_ass_config["use_voicing_embed"] = voicing
            if pre_type==True:
                bitch_ass_config["hnsep"] = "vr"
            else:
                bitch_ass_config["hnsep"] = "world"
            if backbone_type == "wavenet":
                #switches to wavenet backbone at default recommended settings
                #it's the *alternate* backbone toggle, it makes it the opposite of what the default config does
                bitch_ass_config["backbone_type"] = "wavenet"
                bitch_ass_config["backbone_args"]["num_channels"] = 512
                bitch_ass_config["backbone_args"]["num_layers"] = 20
                bitch_ass_config["backbone_args"]["dilation_cycle_length"] = 4
            elif backbone_type == "lynxnet":
                #keeps lynxnet backbone at default recommended settings
                #some people complain they're too heavy but I think they were trying to train on weak cards
                bitch_ass_config["backbone_type"] = "lynxnet"
                bitch_ass_config["backbone_args"]["num_channels"] = 1024
                bitch_ass_config["backbone_args"]["num_layers"] = 6
                bitch_ass_config["backbone_args"]["kernel_size"] = 31
                bitch_ass_config["backbone_args"]["dropout_rate"] = 0.0
                bitch_ass_config["backbone_args"]["strong_cond"] = True
            elif backbone_type == "lynxnet2":
                #keeps lynxnet backbone at default recommended settings
                #some people complain they're too heavy but I think they were trying to train on weak cards
                bitch_ass_config["backbone_type"] = "lynxnet2"
                bitch_ass_config["backbone_args"]["num_channels"] = 1024
                bitch_ass_config["backbone_args"]["num_layers"] = 6
                bitch_ass_config["backbone_args"]["kernel_size"] = 31
                bitch_ass_config["backbone_args"]["dropout_rate"] = 0.0
                bitch_ass_config["backbone_args"]["use_conditioner_cache"] = True
                bitch_ass_config["backbone_args"]["glu_type"] = 'atanglu'
            if adv_on.get() == "on":
                toomanyconfignames = config_name.get()
                customname0 = ("DiffSinger/configs/", toomanyconfignames, ".yaml")
                custom_name = ''.join(customname0)
                with open(custom_name, "w", encoding = "utf-8") as config:
                    yaml.dump(bitch_ass_config, config, default_flow_style=False, sort_keys=False)
                print("wrote custom acoustic config!")
            else:
                with open("DiffSinger/configs/acoustic.yaml", "w", encoding = "utf-8") as config:
                    yaml.dump(bitch_ass_config, config, default_flow_style=False, sort_keys=False)
                print("wrote acoustic config!")

        else:
            with open("DiffSinger/dictionaries/langloader.yaml", "r", encoding = "utf=8") as langloader:
                lang = yaml.safe_load(langloader)
            merged_loc = os.path.join("DiffSinger/dictionaries", lang["merge_list"])
            with open(merged_loc, "r", encoding = "utf-8") as merge_list:
                merges = yaml.safe_load(merge_list)
            with open("DiffSinger/configs/variance.yaml", "r", encoding = "utf-8") as config:
                bitch_ass_config = yaml.safe_load(config)
            bitch_ass_config["diff_loss_type"] = "l1"
            bitch_ass_config["main_loss_type"] = "l1"
            bitch_ass_config["num_spk"] = num_spk
            if num_spk > 1:
                bitch_ass_config["use_spk_id"] = True
            else:
                bitch_ass_config["use_spk_id"] = False
            bitch_ass_config["datasets"] = allspeakers
            bitch_ass_config["dictionaries"] = lang["dictionaries"]
            bitch_ass_config["extra_phonemes"] = lang["extra_phonemes"]
            bitch_ass_config["merged_phoneme_groups"] = merges["merged_phoneme_groups"]
            bitch_ass_config["num_lang"] = len(lang["dictionaries"])
            if len(lang["dictionaries"]) == 1:
                bitch_ass_config["use_lang_id"] = False
            else:
                bitch_ass_config["use_lang_id"] = True
            bitch_ass_config["binary_data_dir"] = self.binary_save_dir
            bitch_ass_config["max_batch_size"] = int(batch)
            bitch_ass_config["val_check_interval"] = int(save_interval)
            bitch_ass_config["predict_dur"] = duration
            bitch_ass_config["predict_energy"] = energy
            bitch_ass_config["predict_breathiness"] = breathiness
            bitch_ass_config["predict_pitch"] = pitch
            bitch_ass_config["predict_tension"] = tension
            bitch_ass_config["predict_voicing"] = voicing
            bitch_ass_config["use_melody_encoder"] = pitch
            bitch_ass_config["binarization_args"]["prefer_ds"] = ds
            if pre_type==True:
                bitch_ass_config["hnsep"] = "vr"
            else:
                bitch_ass_config["hnsep"] = "world"
            if backbone_type== "wavenet":
                #switches to lynxnet at default recommended settings
                #it's the *alternate* backbone toggle, it makes it the opposite of what the default config does
                bitch_ass_config["variances_prediction_args"]["backbone_type"] = "wavenet"
                bitch_ass_config["variances_prediction_args"]["backbone_args"]['num_channels'] = 192
                bitch_ass_config["variances_prediction_args"]["backbone_args"]['num_layers'] = 10
                bitch_ass_config["variances_prediction_args"]["backbone_args"]['dilation_cycle_length'] = 4
                bitch_ass_config["pitch_prediction_args"]["backbone_type"] = "wavenet"
                bitch_ass_config["pitch_prediction_args"]["backbone_args"]['num_channels'] = 256
                bitch_ass_config["pitch_prediction_args"]["backbone_args"]['num_layers'] = 20
                bitch_ass_config["pitch_prediction_args"]["backbone_args"]['dilation_cycle_length'] = 5
   
            elif backbone_type == "lynxnet":
                bitch_ass_config["variances_prediction_args"]["backbone_type"] = "lynxnet"
                bitch_ass_config["variances_prediction_args"]["backbone_args"]['num_channels'] = 384
                bitch_ass_config["variances_prediction_args"]["backbone_args"]['num_layers'] = 6
                bitch_ass_config["variances_prediction_args"]["backbone_args"]['dropout_rate'] = 0.0
                bitch_ass_config["variances_prediction_args"]["backbone_args"]['strong_cond'] = True
                bitch_ass_config["pitch_prediction_args"]["backbone_type"] = "lynxnet"
                bitch_ass_config["pitch_prediction_args"]["backbone_args"]['num_channels'] = 512
                bitch_ass_config["pitch_prediction_args"]["backbone_args"]['num_layers'] = 6
                bitch_ass_config["pitch_prediction_args"]["backbone_args"]['dropout_rate'] = 0.0
                bitch_ass_config["pitch_prediction_args"]["backbone_args"]['strong_cond'] = True
            
            elif backbone_type == "lynxnet2":
                bitch_ass_config["variances_prediction_args"]["backbone_type"] = "lynxnet2"
                bitch_ass_config["variances_prediction_args"]["backbone_args"]['num_channels'] = 384
                bitch_ass_config["variances_prediction_args"]["backbone_args"]['num_layers'] = 6
                bitch_ass_config["variances_prediction_args"]["backbone_args"]['dropout_rate'] = 0.0
                bitch_ass_config["variances_prediction_args"]["backbone_args"]["use_conditioner_cache"] = True
                bitch_ass_config["variances_prediction_args"]["backbone_args"]["glu_type"] = 'atanglu'
                bitch_ass_config["pitch_prediction_args"]["backbone_type"] = "lynxnet2"
                bitch_ass_config["pitch_prediction_args"]["backbone_args"]['num_channels'] = 512
                bitch_ass_config["pitch_prediction_args"]["backbone_args"]['num_layers'] = 6
                bitch_ass_config["pitch_prediction_args"]["backbone_args"]['dropout_rate'] = 0.0
                bitch_ass_config["pitch_prediction_args"]["backbone_args"]["use_conditioner_cache"] = True
                bitch_ass_config["pitch_prediction_args"]["backbone_args"]["glu_type"] = 'atanglu'

            if adv_on.get() == "on":
                toomanyconfignames = config_name.get()
                customname0 = ("DiffSinger/configs/", toomanyconfignames, ".yaml")
                custom_name = ''.join(customname0)
                with open(custom_name, "w", encoding = "utf-8") as config:
                    yaml.dump(bitch_ass_config, config, default_flow_style=False, sort_keys=False)
                print("wrote custom variance config!")

            else:
                with open("DiffSinger/configs/variance.yaml", "w", encoding = "utf-8") as config:
                    yaml.dump(bitch_ass_config, config, default_flow_style=False, sort_keys=False)
                print("wrote variance config!")

        
        
    def langeditor(self):
        #you thought you were done reading GUI code. wrong.
        global editor
        editor = ctk.CTkToplevel(self)
        if is_windows():
            editor.geometry("360x360")
        elif is_macos():
            editor.geometry("400x400")
        elif is_linux():
            editor.geometry("445x420")
        editor.title("DiffTrainer Langloader")
        editor.resizable(False, False)
        with open("DiffSinger/dictionaries/langloader.yaml", "r", encoding = "utf-8") as load_lang:
                global langloader
                langloader = yaml.safe_load(load_lang)
        dictframe = ctk.CTkFrame(master=editor)
        dictframe.grid(row=0, column=0, columnspan=3, pady=(7,0), padx=7)
        tooltip_dict = CTkToolTip(dictframe, message=(self.L('dicts2')), font = self.font)
        dictlabel= ctk.CTkLabel(dictframe, text=(self.L('dicts')), font=self.font)
        dictlabel.grid(row=0, column=0, padx=7, sticky=tk.N)
        tooltip_dict2 = CTkToolTip(dictlabel, message=(self.L('dicts2')), font = self.font)
        global dictbox
        dictbox = tk.Listbox(dictframe, width=30)
        dictbox.grid(row=0, column=1, padx=13, pady=7)
        for key in langloader['dictionaries']:
            dictbox.insert(tk.END, f"{key}: {langloader['dictionaries'][key]}")
        buttonframe1 = ctk.CTkFrame(master=editor)
        buttonframe1.grid(row=1, columnspan=3, padx=13)
        langadd = ctk.CTkButton(buttonframe1, text=(self.L('add_dict')), command=self.add_entry, font=self.font)
        langadd.grid(row=0, column=0, pady=7, padx=13)
        langdel = ctk.CTkButton(buttonframe1, text=(self.L('del_dict')), command=self.remove_entry, font=self.font)
        langdel.grid(row=0, column=2, pady=7, padx=13)
        try: 
            formatted_phonemes = ', '.join(langloader["extra_phonemes"])
        except TypeError:
            formatted_phonemes = ""
        exphframe = ctk.CTkFrame(master=editor)
        exphframe.grid(row=2, column=0, columnspan=3, padx=13, pady=7)
        tooltip_ext = CTkToolTip(exphframe, message=(self.L('ext_ph2')), font = self.font)
        exphlabel = ctk.CTkLabel(exphframe, text=(self.L('ext_ph')), font=self.font)
        exphlabel.grid(row=0, column=0, padx=7)
        tooltip_ext2 = CTkToolTip(exphlabel, message=(self.L('ext_ph2')), font = self.font)
        global exphbox
        exphbox = ctk.CTkEntry(exphframe, font=self.font)
        exphbox.grid(row=0, column=1, padx=13, pady=7)
        exphbox.insert(tk.END, formatted_phonemes)
        mergeframe = ctk.CTkFrame(master=editor)
        mergeframe.grid(row=3, column=0, columnspan=3, padx=13, pady=7)
        tooltip_merge = CTkToolTip(mergeframe, message=(self.L('merge2')), font = self.font)
        mergelabel = ctk.CTkLabel(mergeframe, text=(self.L('merge')), font=self.font)
        mergelabel.grid(row=0, column=0, padx=7)
        tooltip_merge2 = CTkToolTip(mergelabel, message=(self.L('merge2')), font = self.font)
        global mergebox
        mergebox = ctk.CTkEntry(mergeframe, font=self.font)
        mergebox.grid(row=0, column=1, padx=13, pady=7)
        mergebox.insert(tk.END, (langloader["merge_list"]))
        langsave = ctk.CTkButton(editor, text=(self.L('langsave')), command=self.updatelangloader, font=self.font)
        langsave.grid(row=5, column=1, pady=7)

    def update_dictbox(self):
        dictbox.delete(0, tk.END)
        for key in langloader['dictionaries']:
            dictbox.insert(tk.END, f"{key}: {langloader['dictionaries'][key]}")
    
    def add_entry(self):
        language = tk.simpledialog.askstring("Input", "Enter the language code:")
        if language:
            phoneme_file = tk.simpledialog.askstring("Input", f"Enter the file path for {language}:")
            if phoneme_file:
                langloader['dictionaries'][language] = phoneme_file
                self.update_dictbox()
    
    def remove_entry(self):
        try:
            index = dictbox.curselection()[0]
            language = list(langloader['dictionaries'].keys())[index]
            del langloader['dictionaries'][language]
            self.update_dictbox()
        except IndexError:
            pass

    def updatelangloader(self):
        new_phonemes_str = exphbox.get()
        new_phonemes_list = []
        if new_phonemes_str and new_phonemes_str.strip():
            new_phonemes_list = [item.strip() for item in new_phonemes_str.split(',')]
        langloader["extra_phonemes"] = new_phonemes_list
        langloader["merge_list"] = mergebox.get()
        with open("DiffSinger/dictionaries/langloader.yaml", "w", encoding="utf-8") as langdump:
            yaml.dump(langloader, langdump, sort_keys=False)
        editor.destroy()

    def tensor_patch(self):
        with open("DiffSinger/training/acoustic_task.py", "r") as t_aco1:
            tensor_read1 = t_aco1.readlines()
        with open("DiffSinger/training/acoustic_task.py", "w") as t_aco2:
            for line in tensor_read1:
                if line.startswith("matplotlib.use('Agg')"):
                    line = line + "torch.set_float32_matmul_precision('medium')\n"
                t_aco2.write(line)
        with open("DiffSinger/training/variance_task.py", "r") as t_var1:
            tensor_read2 = t_var1.readlines()
        with open("DiffSinger/training/variance_task.py", "w") as t_var2:
            for line in tensor_read2:
                if line.startswith("matplotlib.use('Agg')"):
                    line = line + "torch.set_float32_matmul_precision('medium')\n"
                t_var2.write(line)
        print("Patched!")

    def binarize(self):
        try:
            output = subprocess.check_output(["nvcc", "--version"], stderr=subprocess.STDOUT).decode()
            lines = output.split("\n")
            for line in lines:
                if "release" in line.lower():
                    version = line.split()[-1]
                    print("CUDA version:", version)
                    cuda = "0"
                    break
            else:
                print("CUDA version not found")
                cuda = "-1"
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("CUDA is not available")
            cuda = "-1"
        os.chdir(main_path)
        os.chdir("DiffSinger")
        os.environ["PYTHONPATH"] = "."
        os.environ["CUDA_VISIBLE_DEVICES"] = cuda
        cmdstage = ["python", 'scripts/binarize.py', '--config', configpath]
        command = " ".join(cmdstage)
        run_cmdA(command)
        os.chdir(main_path)

    def load_config_function(self):
        global configpath
        configpath = filedialog.askopenfilename(title="Select config file", initialdir="DiffSinger/configs/", filetypes=[("Config files", "*.yaml")])
        print(configpath)

    def train_function(self):
            try:
                output = subprocess.check_output(["nvcc", "--version"], stderr=subprocess.STDOUT).decode()
                lines = output.split("\n")
                for line in lines:
                    if "release" in line.lower():
                        version = line.split()[-1]
                        print("CUDA version:", version)
                        cuda = "0"
                        break
                else:
                    print("CUDA version not found")
                    cuda = "-1"
            except (FileNotFoundError, subprocess.CalledProcessError):
                print("CUDA is not available")
                cuda = "-1"
            os.chdir(main_path)
            os.chdir("DiffSinger")
            os.environ["PYTHONPATH"] = "."
            os.environ["CUDA_VISIBLE_DEVICES"] = cuda
            if not configpath or not ckpt_save_dir:
                self.label.config(text="Please select your config and the data you would like to train first!")
                return
            cmdstage = ["python", 'scripts/train.py', '--config', configpath, '--exp_name', ckpt_save_dir, '--reset']
            command = " ".join(cmdstage)
            run_cmdA(command)


    def onnx_folder_save(self):
        global onnx_folder_dir
        onnx_folder_dir = filedialog.askdirectory(title="Select onnx export folder", initialdir = "DiffSinger")
        print("export path: " + onnx_folder_dir)

    def run_onnx_export(self):
            os.chdir(main_path)
            os.chdir("DiffSinger")
            os.environ["PYTHONPATH"] = "."
            if not ckpt_save_dir:
                self.label.config(text="Please select your config and the checkpoint you would like to export first!")
                return
            export_check = expselect.get()
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
            cmdstage = ["python", 'scripts/export.py']
            ckpt_save_abs = os.path.abspath(ckpt_save_dir)
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
            else:
                messagebox.showinfo("Required", "Please select a config type")
                return
            command = " ".join(cmdstage)
            run_cmdB(command)
            print("Getting the files in order...")

            #move file cus it export stuff outside the save folder for some reason
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
            os.chdir(onnx_folder_dir)
            wronnx = prefix + ".onnx"
            if os.path.exists(wronnx):
                os.rename(wronnx, "acoustic.onnx")
            nameList = os.listdir()
            for fileName in nameList:
                rename=fileName.removeprefix(prefix + ".")
                os.rename(fileName,rename)

            print("Done!")
            os.chdir(main_path)

    def run_onnx_export2(self):
            os.chdir(main_path)
            os.chdir("DiffSinger")
            os.environ["PYTHONPATH"] = "."
            if not ckpt_save_dir:
                self.label.config(text="Please select your config and the checkpoint you would like to export first!")
                return
            export_check = expselect2.get()
            onnx_folder_dir = os.path.join(ckpt_save_dir, "onnx")
            if os.path.exists(onnx_folder_dir):
                onnx_bak = os.path.join(ckpt_save_dir, "onnx_old")
                os.rename(onnx_folder_dir, onnx_bak)
                print("backing up existing onnx folder...")
            spkmap = os.path.join(ckpt_save_dir, "spk_map.json")
            # Fixing spk_map so the onnx can export
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
            cmdstage = ["python", 'scripts/export.py']
            ckpt_save_abs = os.path.abspath(ckpt_save_dir)
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
            else:
                messagebox.showinfo("Required", "Please select a config type")
                return
            command = " ".join(cmdstage)
            run_cmdB(command)
            print("Getting the files in order...")

            #move file cus it export stuff outside the save folder for some reason
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
            os.chdir(onnx_folder_dir)
            wronnx = prefix + ".onnx"
            if os.path.exists(wronnx):
                os.rename(wronnx, "acoustic.onnx")
            nameList = os.listdir()
            for fileName in nameList:
                rename=fileName.removeprefix(prefix + ".")
                os.rename(fileName,rename)

            print("Done!")
            os.chdir(main_path)


    def get_aco_folder(self):
        global aco_folder_dir
        aco_folder_dir = filedialog.askdirectory(title="Select folder with acoustic checkpoints", initialdir = "DiffSinger/checkpoints/")
        print("Acoustic folder: " + aco_folder_dir)
        global aco_folder_onnx
        aco_folder_onnx = aco_folder_dir + "/onnx"
        global aco_config
        aco_config = os.path.join(aco_folder_dir, "config.yaml")

    def get_var_folder(self):
        var_folder_dir = filedialog.askdirectory(title="Select folder with variance checkpoints", initialdir = "DiffSinger/checkpoints/")
        print("Variance folder: " + var_folder_dir)
        global var_folder_onnx
        var_folder_onnx = var_folder_dir + "/onnx"
        global var_config
        var_config = os.path.join(var_folder_dir, "config.yaml")

    def get_dur_folder(self):
        dur_folder_dir = filedialog.askdirectory(title="Select folder with duration checkpoints", initialdir = "DiffSinger/checkpoints/")
        print("Duration folder: " + dur_folder_dir)
        global dur_folder_onnx
        dur_folder_onnx = dur_folder_dir + "/onnx"
        global dur_config
        dur_config = os.path.join(dur_folder_dir, "config.yaml")

    def get_pitch_folder(self):
        pitch_folder_dir = filedialog.askdirectory(title="Select folder with pitch checkpoints", initialdir = "DiffSinger/checkpoints/")
        print("Pitch folder: " + pitch_folder_dir)
        global pitch_folder_onnx
        pitch_folder_onnx = pitch_folder_dir + "/onnx"
        global pitch_config
        pitch_config = os.path.join(pitch_folder_dir, "config.yaml")

    def get_vocoder(self):
        self.vocoder_onnx = filedialog.askopenfilename(title="OPTIONAL: Select custom vocoder onnx", initialdir="DiffSinger/checkpoints/", filetypes=[("ONNX files", "*.onnx")])
        print("Custom vocoder:" + self.vocoder_onnx)

    def get_OU_folder(self):
        global ou_export_location
        ou_export_location = filedialog.askdirectory(title="Select save folder")
        print("export path: " + ou_export_location)

    def run_OU_config(self):
        os.chdir(main_path)
        os.chdir("DiffSinger")
        os.environ["PYTHONPATH"] = "."

        print("making directories...")
        try:
            ou_name = ou_name_var.get()
            ou_name_stripped = "".join(ou_name.split()) #takes the spaces out so cmd doesn't get confused
            main_stuff = f"{ou_export_location}/{ou_name_stripped}"
            if not os.path.exists(main_stuff):
                os.makedirs(main_stuff)
            if not os.path.exists(f"{main_stuff}/dsmain"):
                os.makedirs(f"{main_stuff}/dsmain")
                os.makedirs(f"{main_stuff}/embeds") #these embed folders wind up empty if it's single speaker
                os.makedirs(f"{main_stuff}/dsdur")
                os.makedirs(f"{main_stuff}/dsdur/embeds") #but it doesn't hurt anything and I don't feel like making it conditional
                try:
                    if os.path.exists(f"{var_folder_onnx}/variance.onnx"):
                        os.makedirs(f"{main_stuff}/dsvariance")
                        os.makedirs(f"{main_stuff}/dsvariance/embeds")
                    else: pass
                except Exception as e:
                    print(f"Error creating directories: {e}")
                try:
                    if os.path.exists(f"{var_folder_onnx}/pitch.onnx"):
                        os.makedirs(f"{main_stuff}/dspitch")
                        os.makedirs(f"{main_stuff}/dspitch/embeds")
                    else: pass
                except Exception as e:
                    print(f"Error creating directories: {e}")
            with open(f"{main_stuff}/character.txt", "w", encoding = "utf-8") as file:
                file.write(f"name={ou_name}\n") #this file could be fancier but feels like overkill for this program
            with open(f"{main_stuff}/character.yaml", "w", encoding = "utf-8") as file: #create initial yaml
                file.write("default_phonemizer: OpenUtau.Core.DiffSinger.DiffSingerPhonemizer\n") #defaults to DIFFS on first use
                file.write("singer_type: diffsinger\n")
        except Exception as e:
            print(f"Error creating directories: {e}")
        print("\nmoving core files...")

        try:
            shutil.copy(f"{aco_folder_onnx}/acoustic.onnx", f"{main_stuff}/dsmain")
            shutil.copy(f"{aco_folder_onnx}/phonemes.json", f"{main_stuff}/dsmain")
            shutil.copy(f"{aco_folder_onnx}/languages.json", f"{main_stuff}/dsmain")
            shutil.copy(f"{aco_folder_onnx}/dsconfig.yaml", main_stuff) #just straight up uses the original acoustic dsconfig as the one for the main folder
            shutil.copy(f"{var_folder_onnx}/linguistic.onnx", f"{main_stuff}/dsmain")

        except Exception as e:
            print(f"Error moving core files: {e}")

        print("\nmoving acoustic embeds...")
        try:
            acoustic_emb_files = [file for file in os.listdir(aco_folder_onnx) if file.endswith(".emb")]
            for emb_file in acoustic_emb_files:
                shutil.copy(f"{aco_folder_onnx}/{emb_file}", f"{main_stuff}/embeds")
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
            if os.path.exists(f"{var_folder_onnx}/dur.onnx"):
                shutil.copy(f"{var_folder_onnx}/dur.onnx", f"{main_stuff}/dsdur")
                for emb_file in var_emb_files:
                    shutil.copy(f"{var_folder_onnx}/{emb_file}", f"{main_stuff}/dsdur/embeds")
            if os.path.exists(f"{var_folder_onnx}/variance.onnx"):
                shutil.copy(f"{var_folder_onnx}/variance.onnx", f"{main_stuff}/dsvariance")
                for emb_file in var_emb_files:
                    shutil.copy(f"{var_folder_onnx}/{emb_file}", f"{main_stuff}/dsvariance/embeds")
            if os.path.exists(f"{var_folder_onnx}/pitch.onnx"):
                shutil.copy(f"{var_folder_onnx}/pitch.onnx", f"{main_stuff}/dspitch")
                for emb_file in var_emb_files:
                    shutil.copy(f"{var_folder_onnx}/{emb_file}", f"{main_stuff}/dspitch/embeds")
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
                with open(f"{main_stuff}/character.yaml", "r", encoding = "utf-8") as config:
                    character_config = yaml.safe_load(config)
                character_config["subbanks"] = subbanks 
                with open(f"{main_stuff}/character.yaml", "w", encoding = "utf-8") as config:
                    yaml.dump(character_config, config)
            #placeholders to fill in later if you care, can be left this way for private/test models
            with open(f"{main_stuff}/character.yaml", "a", encoding = "utf-8") as file:
                file.write("\n")
                file.write("text_file_encoding: utf-8\n")
                file.write("\n")
                file.write("image:\n")
                file.write("portrait:\n")
                file.write("portrait_opacity: 0.45\n")
            with open(f"{main_stuff}/dsconfig.yaml", "r", encoding = "utf-8") as config:
                dsconfig_data = yaml.safe_load(config) #just edit the original config seriously
            dsconfig_data["acoustic"] = "dsmain/acoustic.onnx" #fix those file paths
            dsconfig_data["phonemes"] = "dsmain/phonemes.json"
            dsconfig_data["languages"] = "dsmain/languages.json"
            dsconfig_data["vocoder"] = "nsf_hifigan" #gets overwritten later if there's a custom vocoder
            dsconfig_data["singer_type"] = "diffsinger"
            if subbanks:
                dsconfig_data["speakers"] = acoustic_embeds #cleans up the file names
            with open(f"{main_stuff}/dsconfig.yaml", "w", encoding = "utf-8") as config:
                yaml.dump(dsconfig_data, config, sort_keys=False)
        except Exception as e:
                    print(f"Error writing OU main configs: {e}")

        print("writing sub-configs...")
        try:
            with open(aco_config, "r", encoding = "utf-8") as config:
                acoustic_config_data = yaml.safe_load(config) #copies most of the main dsconfig
            sample_rate = acoustic_config_data.get("audio_sample_rate")
            hop_size = acoustic_config_data.get("hop_size")
            with open(f"{var_folder_onnx}/dsconfig.yaml", "r", encoding = "utf-8") as config:
                variance_config_data = yaml.safe_load(config)
            sample_rate2 = variance_config_data.get("sample_rate")
            hop_size2 = variance_config_data.get("hop_size")
            use_note_rest = variance_config_data.get("use_note_rest")
            use_continuous_acceleration = variance_config_data.get("use_continuous_acceleration")
            use_lang_id = acoustic_config_data.get("use_lang_id")

            with open(f"{main_stuff}/dsdur/dsconfig.yaml", "w", encoding = "utf-8") as file:
                file.write("phonemes: ../dsmain/phonemes.json\n")
                file.write("languages: ../dsmain/languages.json\n")
                file.write("linguistic: ../dsmain/linguistic.onnx\n")
                file.write("dur: dur.onnx\n") #file paths aren't totally the same so gotta rewrite
            with open(f"{main_stuff}/dsdur/dsconfig.yaml", "r", encoding = "utf-8") as config:
                dsdur_config = yaml.safe_load(config)
            dsdur_config["use_continuous_acceleration"] = use_continuous_acceleration
            dsdur_config["sample_rate"] = sample_rate2
            dsdur_config["hop_size"] = hop_size2
            dsdur_config["predict_dur"] = True #this is the dur config, if it doesn't predict_dur wtf does it do
            dsdur_config["use_lang_id"] = use_lang_id
            if subbanks:
                dsdur_config["speakers"] = variance_embeds #points it to the correct embeds for dur
            with open(f"{main_stuff}/dsdur/dsconfig.yaml", "w", encoding = "utf-8") as config:
                yaml.dump(dsdur_config, config, sort_keys=False)

            try:
                if os.path.exists(f"{var_folder_onnx}/variance.onnx"): #if no bre/ene/ten/voc, skips this section
                    with open(var_config, "r", encoding = "utf-8") as config: #it's basically the same as dsdur in basic export tho
                        var_config_data = yaml.safe_load(config)
                    predict_voicing = var_config_data.get("predict_voicing")
                    predict_tension = var_config_data.get("predict_tension")
                    predict_energy = var_config_data.get("predict_energy")
                    predict_breathiness = var_config_data.get("predict_breathiness")
                    predict_dur = var_config_data.get("predict_dur")
                    with open(f"{main_stuff}/dsvariance/dsconfig.yaml", "w", encoding = "utf-8") as file:
                        file.write("phonemes: ../dsmain/phonemes.json\n")
                        file.write("languages: ../dsmain/languages.json\n")
                        file.write("linguistic: ../dsmain/linguistic.onnx\n")
                        file.write("variance: variance.onnx\n")
                    with open(f"{main_stuff}/dsvariance/dsconfig.yaml", "r", encoding = "utf-8") as config:
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
                    with open(f"{main_stuff}/dsvariance/dsconfig.yaml", "w", encoding = "utf-8") as config:
                        yaml.dump(dsvariance_config, config, sort_keys=False)
                else:
                    print("No variance selected")
            except Exception as e:
                print(f"Error editing variance config: {e}")

            try:
                if os.path.exists(f"{var_folder_onnx}/pitch.onnx"): #if no pitch, skips this section
                    with open(f"{main_stuff}/dspitch/dsconfig.yaml", "w", encoding = "utf-8") as file:
                        file.write("phonemes: ../dsmain/phonemes.json\n")
                        file.write("languages: ../dsmain/languages.json\n")
                        file.write("linguistic: ../dsmain/linguistic.onnx\n")
                        file.write("predict_dur: true\n")
                        file.write("pitch: pitch.onnx\n")
                        file.write("use_expr: true\n")
                    with open(f"{main_stuff}/dspitch/dsconfig.yaml", "r", encoding = "utf-8") as config:
                        dspitch_config = yaml.safe_load(config)
                    dspitch_config["use_continuous_acceleration"] = use_continuous_acceleration
                    dspitch_config["sample_rate"] = sample_rate
                    dspitch_config["hop_size"] = hop_size
                    dspitch_config["predict_dur"] = predict_dur
                    dspitch_config["use_lang_id"] = use_lang_id
                    if subbanks:
                        dspitch_config["speakers"] = variance_embeds
                    dspitch_config["use_note_rest"] = use_note_rest
                    with open(f"{main_stuff}/dspitch/dsconfig.yaml", "w", encoding = "utf-8") as config:
                        yaml.dump(dspitch_config, config, sort_keys=False)
                else:
                    print("No pitch selected")
            except Exception as e:
                print(f"Error editing pitch config: {e}")
        except Exception as e:
            print(f"Error editing sub-configs: {e}")

        if self.vocoder_onnx:
            print("making dsvocoder directory and necessary files...")
            try:
                os.makedirs(f"{main_stuff}/dsvocoder")
                vocoder_folder = os.path.dirname(self.vocoder_onnx)
                vocoder_file = os.path.basename(self.vocoder_onnx)
                vocoder_name = os.path.splitext(vocoder_file)[0]
                shutil.copy(self.vocoder_onnx, os.path.join(main_stuff, "dsvocoder"))
                shutil.copy(f"{vocoder_folder}/vocoder.yaml", f"{main_stuff}/dsvocoder")
                with open(f"{main_stuff}/dsconfig.yaml", "r", encoding = "utf-8") as config:
                    dsconfig_data2 = yaml.safe_load(config)
                dsconfig_data2["vocoder"] = vocoder_name #overwrites nsf_hifigan
                with open(f"{main_stuff}/dsconfig.yaml", "w", encoding = "utf-8") as config:
                    yaml.dump(dsconfig_data2, config, sort_keys=False)
            except Exception as e:
                    print(f"Error adding custom vocoder: {e}")
        print("OU setup complete! Please manually import dsdicts")


    def run_adv_config(self): #see basic export for most of the comments
        os.chdir(main_path)
        os.chdir("DiffSinger")
        os.environ["PYTHONPATH"] = "."

        print("\nmaking directories...")
        try:
            ou_name = ou_name_var2.get()
            ou_name_stripped = "".join(ou_name.split())
            main_stuff = f"{ou_export_location}/{ou_name_stripped}"
            if not os.path.exists(main_stuff):
                os.makedirs(main_stuff)
            if not os.path.exists(f"{main_stuff}/dsmain"):
                os.makedirs(f"{main_stuff}/dsmain")
                os.makedirs(f"{main_stuff}/embeds")
                os.makedirs(f"{main_stuff}/dsdur")
                os.makedirs(f"{main_stuff}/dsdur/embeds/")
                try:
                    if var_folder_onnx: #treats var as fully separate from dur in this version
                        os.makedirs(f"{main_stuff}/dsvariance")
                        os.makedirs(f"{main_stuff}/dsvariance/embeds")
                    else: pass
                except Exception as e:
                    print(f"Error creating directories: {e}")
                try:
                    if pitch_folder_onnx: #same with pitch
                        os.makedirs(f"{main_stuff}/dspitch")
                        os.makedirs(f"{main_stuff}/dspitch/embeds")
                    else: pass
                except Exception as e:
                    print(f"Error creating directories: {e}")
            with open(f"{main_stuff}/character.txt", "w", encoding = "utf-8") as file:
                file.write(f"name={ou_name}\n")
            with open(f"{main_stuff}/character.yaml", "w", encoding = "utf-8") as file: #create initial yaml
                file.write("default_phonemizer: OpenUtau.Core.DiffSinger.DiffSingerPhonemizer\n")
                file.write("singer_type: diffsinger\n")
        except Exception as e:
            print(f"Error creating directories: {e}")
        print("\nmoving core files...")

        try:
            shutil.copy(f"{aco_folder_onnx}/acoustic.onnx", f"{main_stuff}/dsmain")
            shutil.copy(f"{aco_folder_onnx}/phonemes.json", f"{main_stuff}/dsmain")
            shutil.copy(f"{aco_folder_onnx}/languages.json", f"{main_stuff}/dsmain")
            shutil.copy(f"{aco_folder_onnx}/dsconfig.yaml", main_stuff) #default acoustic dsconfig becomes the base
            shutil.copy(f"{dur_folder_onnx}/linguistic.onnx", f"{main_stuff}/dsmain")

        except Exception as e:
            print(f"Error moving core files: {e}")

        print("\nmoving acoustic embeds...")
        try:
            acoustic_emb_files = [file for file in os.listdir(aco_folder_onnx) if file.endswith(".emb")]
            for emb_file in acoustic_emb_files:
                shutil.copy(f"{aco_folder_onnx}/{emb_file}", f"{main_stuff}/embeds")
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

        print("\nmoving duration files...")
        try:
            dur_emb_files = [file for file in os.listdir(dur_folder_onnx) if file.endswith(".emb")]
            for emb_file in dur_emb_files:
                shutil.copy(f"{dur_folder_onnx}/{emb_file}", f"{main_stuff}/dsdur/embeds")
            shutil.copy(f"{dur_folder_onnx}/dur.onnx", f"{main_stuff}/dsdur")
            duration_emb_files = os.listdir(dur_folder_onnx)
            duration_embeds = []
            duration_color_suffix = []
            for file in duration_emb_files:
                if file.endswith(".emb"):
                    duration_emb = os.path.splitext(file)[0]
                    duration_embeds.append("embeds/" + duration_emb)
                    duration_color_suffix.append(duration_emb)
        except Exception as e:
            print(f"Error moving duration files: {e}")


        print("\nmoving variance files...")
        try:
            var_emb_files = [file for file in os.listdir(var_folder_onnx) if file.endswith(".emb")]
            for emb_file in var_emb_files:
                shutil.copy(f"{var_folder_onnx}/{emb_file}", f"{main_stuff}/dsvariance/embeds")
            shutil.copy(f"{var_folder_onnx}/variance.onnx", f"{main_stuff}/dsvariance")
            shutil.copy(f"{var_folder_onnx}/linguistic.onnx", f"{main_stuff}/dsvariance")
            shutil.copy(f"{var_folder_onnx}/phonemes.json", f"{main_stuff}/dsvariance") #multidict merge shenanigans can require multiple different phonemes.json
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

        print("\nmoving pitch files...")
        try:
            pitch_emb_files = [file for file in os.listdir(pitch_folder_onnx) if file.endswith(".emb")]
            for emb_file in pitch_emb_files:
                shutil.copy(f"{pitch_folder_onnx}/{emb_file}", f"{main_stuff}/dspitch/embeds")
            shutil.copy(f"{pitch_folder_onnx}/pitch.onnx", f"{main_stuff}/dspitch")
            shutil.copy(f"{pitch_folder_onnx}/linguistic.onnx", f"{main_stuff}/dspitch")
            shutil.copy(f"{pitch_folder_onnx}/phonemes.json", f"{main_stuff}/dspitch")
            pitch_emb_files = os.listdir(pitch_folder_onnx)
            pitch_embeds = []
            pitch_color_suffix = []
            for file in pitch_emb_files:
                if file.endswith(".emb"):
                    pitch_emb = os.path.splitext(file)[0]
                    pitch_embeds.append("embeds/" + pitch_emb)
                    pitch_color_suffix.append(pitch_emb)
        except Exception as e:
            print(f"Error moving pitch files: {e}")

        print("writing main configs...")
        try:
            subbanks = []
            for i, (acoustic_embed_color, acoustic_embed_suffix) in enumerate(zip(acoustic_color_suffix, acoustic_embeds), start=1):
                color = f"{i:02}: {acoustic_embed_color}"
                suffix = f"{acoustic_embed_suffix}"
                subbanks.append({"color": color, "suffix": suffix})
            if subbanks:
                with open(f"{main_stuff}/character.yaml", "r", encoding = "utf-8") as config:
                    character_config = yaml.safe_load(config)
                character_config["subbanks"] = subbanks
                with open(f"{main_stuff}/character.yaml", "w", encoding = "utf-8") as config:
                    yaml.dump(character_config, config)
            #image, portrait, and portrait opacity can be manually edited
            with open(f"{main_stuff}/character.yaml", "a", encoding = "utf-8") as file:
                file.write("\n")
                file.write("text_file_encoding: utf-8\n")
                file.write("\n")
                file.write("image:\n")
                file.write("portrait:\n")
                file.write("portrait_opacity: 0.45\n")
            with open(f"{main_stuff}/dsconfig.yaml", "r", encoding = "utf-8") as config:
                dsconfig_data = yaml.safe_load(config)
            dsconfig_data["acoustic"] = "dsmain/acoustic.onnx"
            dsconfig_data["phonemes"] = "dsmain/phonemes.json"
            dsconfig_data["languages"] = "dsmain/languages.json"
            dsconfig_data["vocoder"] = "nsf_hifigan"
            dsconfig_data["singer_type"] = "diffsinger"
            if subbanks:
                dsconfig_data["speakers"] = acoustic_embeds
            with open(f"{main_stuff}/dsconfig.yaml", "w", encoding = "utf-8") as config:
                yaml.dump(dsconfig_data, config, sort_keys=False)
        except Exception as e:
                    print(f"Error writing OU main configs: {e}")

        print("writing sub-configs...")
        try:
            with open(aco_config, "r", encoding = "utf-8") as config: #all this stuff should be consistent across configs
                acoustic_config_data = yaml.safe_load(config)
            sample_rate = acoustic_config_data.get("audio_sample_rate")
            hop_size = acoustic_config_data.get("hop_size")
            with open(f"{dur_folder_onnx}/dsconfig.yaml", "r", encoding = "utf-8") as config:
                variance_config_data = yaml.safe_load(config)
            sample_rate2 = variance_config_data.get("sample_rate")
            hop_size2 = variance_config_data.get("hop_size")
            use_continuous_acceleration = variance_config_data.get("use_continuous_acceleration")
            use_lang_id = acoustic_config_data.get("use_lang_id")

            with open(f"{main_stuff}/dsdur/dsconfig.yaml", "w", encoding = "utf-8") as file:
                file.write("phonemes: ../dsmain/phonemes.json\n") #dur gets the main one
                file.write("languages: ../dsmain/languages.json\n")
                file.write("linguistic: ../dsmain/linguistic.onnx\n")
                file.write("dur: dur.onnx\n")
            with open(f"{main_stuff}/dsdur/dsconfig.yaml", "r", encoding = "utf-8") as config:
                dsdur_config = yaml.safe_load(config)
            dsdur_config["use_continuous_acceleration"] = use_continuous_acceleration
            dsdur_config["sample_rate"] = sample_rate2
            dsdur_config["hop_size"] = hop_size2
            dsdur_config["predict_dur"] = True
            dsdur_config["use_lang_id"] = use_lang_id
            if subbanks:
                dsdur_config["speakers"] = duration_embeds
            with open(f"{main_stuff}/dsdur/dsconfig.yaml", "w", encoding = "utf-8") as config:
                yaml.dump(dsdur_config, config, sort_keys=False)

            try:
                if var_folder_onnx:
                    with open(var_config, "r", encoding = "utf-8") as config:
                        var_config_data = yaml.safe_load(config)
                    predict_voicing = var_config_data.get("predict_voicing")
                    predict_tension = var_config_data.get("predict_tension")
                    predict_energy = var_config_data.get("predict_energy")
                    predict_breathiness = var_config_data.get("predict_breathiness")
                    predict_dur = var_config_data.get("predict_dur")
                    with open(f"{main_stuff}/dsvariance/dsconfig.yaml", "w", encoding = "utf-8") as file:
                        file.write("phonemes: phonemes.json\n") #multidict merging shenanigans can require separate phonemes.json
                        file.write("languages: ../dsmain/languages.json\n")
                        file.write("linguistic: linguistic.onnx\n")
                        file.write("variance: variance.onnx\n")
                    with open(f"{main_stuff}/dsvariance/dsconfig.yaml", "r", encoding = "utf-8") as config:
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
                    with open(f"{main_stuff}/dsvariance/dsconfig.yaml", "w", encoding = "utf-8") as config:
                        yaml.dump(dsvariance_config, config, sort_keys=False)
                else:
                    print("No variance selected")
            except Exception as e:
                print(f"Error editing variance config: {e}")

            try:
                if pitch_folder_onnx:
                    with open(f"{main_stuff}/dspitch/dsconfig.yaml", "w", encoding = "utf-8") as file:
                        file.write("phonemes: phonemes.json\n") #multidict merging shenanigans can require separate phonemes.json
                        file.write("languages: ../dsmain/languages.json\n")
                        file.write("linguistic: linguistic.onnx\n")
                        file.write("pitch: pitch.onnx\n")
                        file.write("use_expr: true\n")
                    with open(f"{pitch_folder_onnx}/dsconfig.yaml", "r", encoding = "utf-8") as config:
                        pitch_config_data = yaml.safe_load(config)
                    predict_dur = pitch_config_data.get("predict_dur")
                    use_note_rest = pitch_config_data.get("use_note_rest")
                    with open(f"{main_stuff}/dspitch/dsconfig.yaml", "r", encoding = "utf-8") as config:
                        dspitch_config = yaml.safe_load(config)
                    dspitch_config["use_continuous_acceleration"] = use_continuous_acceleration
                    dspitch_config["sample_rate"] = sample_rate
                    dspitch_config["hop_size"] = hop_size
                    dspitch_config["predict_dur"] = predict_dur
                    dspitch_config["use_lang_id"] = use_lang_id
                    if subbanks:
                        dspitch_config["speakers"] = pitch_embeds
                    dspitch_config["use_note_rest"] = use_note_rest
                    with open(f"{main_stuff}/dspitch/dsconfig.yaml", "w", encoding = "utf-8") as config:
                        yaml.dump(dspitch_config, config, sort_keys=False)
                else:
                    print("No pitch selected")
            except Exception as e:
                print(f"Error editing pitch config: {e}")
        except Exception as e:
            print(f"Error editing sub-configs: {e}")

        if self.vocoder_onnx:
            print("making dsvocoder directory and necessary files...")
            try:
                os.makedirs(f"{main_stuff}/dsvocoder")
                vocoder_folder = os.path.dirname(self.vocoder_onnx)
                vocoder_file = os.path.basename(self.vocoder_onnx)
                vocoder_name = os.path.splitext(vocoder_file)[0]
                shutil.copy(self.vocoder_onnx, os.path.join(main_stuff, "dsvocoder"))
                shutil.copy(f"{vocoder_folder}/vocoder.yaml", f"{main_stuff}/dsvocoder")
                with open(f"{main_stuff}/dsconfig.yaml", "r", encoding = "utf-8") as config:
                    dsconfig_data2 = yaml.safe_load(config)
                dsconfig_data2["vocoder"] = vocoder_name
                with open(f"{main_stuff}/dsconfig.yaml", "w", encoding = "utf-8") as config:
                    yaml.dump(dsconfig_data2, config, sort_keys=False)
            except Exception as e:
                    print(f"Error adding custom vocoder: {e}")
        print("OU setup complete! Please manually import dsdicts")




class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DiffTrainer")
        self.iconpath = ImageTk.PhotoImage(file=os.path.join("assets","hard-drive.png"))
        self.wm_iconbitmap()
        self.iconphoto(False, self.iconpath)
        self.resizable(False, False)
        create_widgets(self)
    

    def on_tab_change(self, event):
        os.chdir(main_path)

    global create_widgets
    def create_widgets(self):
        self.tab_view = tabview(master=self)
        self.tab_view.grid(row=0, column=0, padx=10, pady=(0, 15))


if __name__ == "__main__":
    app = App()
    app.mainloop()

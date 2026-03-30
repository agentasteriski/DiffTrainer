import zipfile, shutil, csv, json, yaml, random, subprocess, os, requests, re, webbrowser, sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk
from tqdm import tqdm
from CTkToolTip import CTkToolTip
from CTkListbox import CTkListbox
from datetime import datetime
from ezlocalizr import ezlocalizr
from plyer import notification
from dt_modules import onnxexport, basicexport, advexport, liteconvert, corpus_segmenter




main_path = os.path.dirname(__file__)
ds_path = os.path.join(main_path, "DiffSinger")
realpython = sys.executable
ctk.set_default_color_theme(os.path.join(main_path, "assets", "ds_gui.json"))
version = "0.4.0"
releasedate = "10/29/25"

#after the de-Condaing the only one that gets used is the Linux check but I'm leaving the others for now
def is_linux():
    return sys.platform.startswith("linux")
def is_windows():
    return sys.platform.startswith("win")
def is_macos():
    return sys.platform.startswith("darwin")

if is_linux():
    ctk.DrawEngine.preferred_drawing_method = "circle_shapes" #helps de-uglyfy ctk in linux+base conda if not using the real fix

#starts with English before overriding the language with whatever's in the settings
guisettings = {
    'lang': 'en_US',
}
settingspath = os.path.join(main_path, "assets", "guisettings.yaml")
if os.path.exists(settingspath):
    with open(settingspath, 'r', encoding='utf-8') as c:
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

        self.data_folder = r"" #more forces
        self.ckpt_save_dir = r"" #even more forces
        self.trainselect_option = r"" #rawr
        self.vocoder_onnx = r"" #actually this one isn't forcing anything none is fine
        self.aco_folder_dir = r"" 
        self.var_folder_dir = r""
        self.pitch_folder_dir = r""
        self.dur_folder_dir = r""
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
        self.logopath = os.path.join("assets", "difftrainerlogo.png")
        self.logo = ctk.CTkImage(light_image=Image.open(self.logopath),
                                  dark_image=Image.open(self.logopath),
                                  size=(400, 150))

        ##ABOUT
        #to do: audit translations/clear unused strings from en_US
        self.label = ctk.CTkLabel(master=self.tab(self.L('tab_ttl_1')), text = "", image = self.logo)
        self.label.grid(row=0, column=0, ipady=10, columnspan = 3)
        self.label = ctk.CTkLabel(master=self.tab(self.L('tab_ttl_1')), text = f"{self.L('vers')} {version}({releasedate})", font = self.font)
        self.label.grid(row=1, column=1)
        self.button = ctk.CTkButton(master=self.tab(self.L('tab_ttl_1')), text = self.L('changelog'), font = self.font)
        self.button.grid(row=2, column=0, padx=50)
        self.button.bind("<Button-1>", lambda e: self.credit("https://github.com/agentasteriski/DiffTrainer/blob/rewrite/changelog.md")) #why tf is it still opening the one on main. it literally says rewrite. it exists.
        self.button = ctk.CTkButton(master=self.tab(self.L('tab_ttl_1')), text = self.L('update'), command = self.dl_update, font = self.font)
        self.button.grid(row=2, column=2, padx=50)
        self.tooltip = CTkToolTip(self.button, message=(self.L('update2')), font = self.font)
        self.label = ctk.CTkLabel(master=self.tab(self.L('tab_ttl_1')), text = (self.L('cred_lead') + " Aster"), font = self.font_ul)
        self.label.bind("<Button-1>", lambda e: self.credit("https://github.com/agentasteriski"))
        self.label.grid(row=3, column=0, pady=30)
        self.tooltip = CTkToolTip(self.label, message="this is a link", font = self.font)
        self.label = ctk.CTkLabel(master=self.tab(self.L('tab_ttl_1')), text = (self.L('cred_tools')), font = self.font_ul)
        self.label.bind("<Button-1>", lambda e: self.credit("https://github.com/agentasteriski/DiffTrainer/blob/rewrite/extracredits.md"))
        self.label.grid(row=3, column=1, pady=30)
        self.tooltip = CTkToolTip(self.label, message="this is also a link", font = self.font)
        self.label = ctk.CTkLabel(master=self.tab(self.L('tab_ttl_1')), text = self.L('cred_trans'), font = self.font)
        self.label.grid(row=3, column=2, pady=30)
        self.label = ctk.CTkLabel(master=self.tab(self.L('tab_ttl_1')), text = self.L('restart'), font = self.font)
        self.label.grid(row=4, column=2, sticky=tk.W)
        self.langselect = ctk.CTkComboBox(master=self.tab(self.L('tab_ttl_1')), values=self.L.lang_list, command=lambda x: self.refresh(self.lang.get(), master=self), variable=self.lang, font = self.font)
        self.langselect.grid(row=4, column=2, sticky=tk.SE)

        ##SEGMENT
        self.frame1 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_2')))
        self.frame1.grid(padx=(35, 10), pady=(10,0))

        
        self.segvar = tk.BooleanVar()
        self.segtoggle = ctk.CTkCheckBox(master=self.frame1, text=self.L('seg'), variable=self.segvar, font = self.font)
        self.segtoggle.grid(row=0, column=0)
        self.tooltip = CTkToolTip(self.segtoggle, message=self.L('seg2'), font = self.font)
        self.segframe = ctk.CTkFrame(master=self.frame1)
        self.segframe.grid(row=1, column=0, padx=(60,10), pady=10)
        self.seglabel = ctk.CTkLabel(master=self.segframe, text=self.L('length_seg'), font = self.font)
        self.seglabel.grid(row=1, padx=10, pady=5)
        self.tooltip = CTkToolTip(self.seglabel, message=self.L('length_seg2'), font = self.font)
        self.seglength = tk.IntVar()
        self.segbox = ctk.CTkEntry(master=self.segframe, textvariable = self.seglength, width = 60, font = self.font)
        self.segbox.insert(0, "5")
        self.segbox.grid(row=3, pady=(0,5))
        self.batchslider = ctk.CTkSlider(master=self.segframe, from_=1, to=30, number_of_steps=29, variable=self.seglength)
        self.batchslider.set(5)
        self.batchslider.grid(row=2)

        self.estvar = tk.BooleanVar()
        self.estmidi = ctk.CTkCheckBox(master=self.frame1, text=self.L('estmidi'), variable=self.estvar, font = self.font)
        self.estmidi.grid(row=0, column=1, padx=50)
        self.tooltip = CTkToolTip(self.estmidi, message=self.L('estmidi2'), font = self.font)

        self.rawbutton = ctk.CTkButton(master=self.frame1, text=self.L('rawdata'), command=self.grab_raw_data, font = self.font)
        self.rawbutton.grid(row=4, column=0, pady=(10,0))
        self.tooltip = CTkToolTip(self.rawbutton, message=self.L('rawdata2'), font = self.font)
        self.convertbutton = ctk.CTkButton(master=self.frame1, text=self.L('prepdata'), command= self.convert2csv, font = self.font)
        self.convertbutton.grid(row=4, column=1, padx=50, pady=(10,0))
        self.tooltip = CTkToolTip(self.convertbutton, message=self.L('prepdata2'), font = self.font)


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
        global timeaug
        timeaug = tk.BooleanVar()
        self.confbox7 =  ctk.CTkCheckBox(master=self.subframe, text="vel", variable=timeaug, onvalue = True, offvalue = False, state=tk.DISABLED, font = self.font)
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
        self.tooltip = CTkToolTip(self.confbox11, message=(self.L('backbone')), font = self.font)
        global trainstretch
        trainstretch = tk.BooleanVar()
        self.confbox12 = ctk.CTkCheckBox(master=self.subframe, text="stretch", variable=trainstretch, onvalue = True, offvalue = False, state=tk.DISABLED, font=self.font)
        self.confbox12.grid(row=4, column=3, pady=5, padx=(0,3))
        self.tooltip = CTkToolTip(self.confbox12, message=(self.L('stretch')), font = self.font)

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
        self.frame12.grid(column=0, row=0, padx=130, pady=10)
        self.expselect_option = tk.IntVar(value=0)
        self.acobutton = ctk.CTkRadioButton(master=self.frame12, text=(self.L('aco')), variable=self.expselect_option, value=1, font = self.font)
        self.acobutton.grid(row=0, column=0, padx=10)
        self.tooltip = CTkToolTip(self.acobutton, message=(self.L('acotip')), font = self.font)
        self.varbutton = ctk.CTkRadioButton(master=self.frame12, text=(self.L('var')), variable=self.expselect_option, value=2, font = self.font)
        self.varbutton.grid(row=1, column=0, padx=10, pady=(0,10))
        self.tooltip = CTkToolTip(self.varbutton, message=(self.L('vartip')), font = self.font)
        global expselect
        expselect = self.expselect_option
        global drop_on
        drop_on = tk.StringVar()
        self.droptoggle = ctk.CTkSwitch(master=self.frame12, text="OPTIONAL: Drop speakers", variable=drop_on, onvalue="on", offvalue="off", command=self.changeState2, font = self.font)
        self.droptoggle.grid(row=0, column=1, padx=10)
        global dropspk
        dropspk = tk.StringVar(value="speakers_to_drop")
        self.dropbox = ctk.CTkEntry(master=self.frame12, textvariable=dropspk, font=self.font, state=tk.DISABLED)
        self.dropbox.grid(row=1, column=1, padx=10, pady=(0,10))
        self.button = ctk.CTkButton(master=self.frame12, text=(self.L('step2')), command=self.ckpt_folder_save, font = self.font)
        self.button.grid(row=2, column=0, padx=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('step2-2alt')), font = self.font)
        self.button = ctk.CTkButton(master=self.frame12, text=(self.L('onnx')), command=self.run_onnx_export, font = self.font)
        self.button.grid(row=2, column=1, padx=10)
        
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
        global autodsdictvar
        autodsdictvar = tk.BooleanVar()
        self.checkbox = ctk.CTkCheckBox(master=self.frame13, text=f"(Experimental)\nWrite base dsdicts", font = self.font, variable = autodsdictvar)
        self.checkbox.grid(row=2, column=1, padx=10, pady=10)
        self.button = ctk.CTkButton(master=self.frame13, text=(self.L('ouexport')), command=self.run_OU_config, font = self.font)
        self.button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        ##EXPORT 2 ELECTRIC BOOGALOO
        self.frame15 = ctk.CTkFrame(master=self.tab(self.L('tab_ttl_6')))
        self.frame15.grid(column=0, row=0, padx=130, pady=10)
        self.expselect_option2 = tk.IntVar(value=0)
        self.acobutton = ctk.CTkRadioButton(master=self.frame15, text=(self.L('aco')), variable=self.expselect_option2, value=1, font = self.font)
        self.acobutton.grid(row=0, column=0, padx=10)
        self.tooltip = CTkToolTip(self.acobutton, message=(self.L('acotip')), font = self.font)
        self.varbutton = ctk.CTkRadioButton(master=self.frame15, text=(self.L('var')), variable=self.expselect_option2, value=2, font = self.font)
        self.varbutton.grid(row=1, column=0, padx=10, pady=(0,10))
        self.tooltip = CTkToolTip(self.varbutton, message=(self.L('vartip')), font = self.font)
        global expselect2
        expselect2 = self.expselect_option2
        global drop_on2
        drop_on2 = tk.StringVar()
        self.droptoggle2 = ctk.CTkSwitch(master=self.frame15, text="OPTIONAL: Drop speakers", variable=drop_on2, onvalue="on", offvalue="off", command=self.changeState3, font = self.font)
        self.droptoggle2.grid(row=0, column=1, padx=10)
        global dropspk2
        dropspk2 = tk.StringVar(value="speakers_to_drop")
        self.dropbox2 = ctk.CTkEntry(master=self.frame15, textvariable=dropspk2, font=self.font, state=tk.DISABLED)
        self.dropbox2.grid(row=1, column=1, padx=10, pady=(0,10))
        self.button = ctk.CTkButton(master=self.frame15, text=(self.L('step2')), command=self.ckpt_folder_save, font = self.font)
        self.button.grid(row=2, column=0, padx=10)
        self.tooltip = CTkToolTip(self.button, message=(self.L('step2-2alt')), font = self.font)
        self.button = ctk.CTkButton(master=self.frame15, text=(self.L('onnx')), command=self.run_onnx_export2, font = self.font)
        self.button.grid(row=2, column=1, padx=10)
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
        self.tooltip = CTkToolTip(self.button, message=(self.L('getaco2')), font = self.font)
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
        global autodsdictvar2
        autodsdictvar2 = tk.BooleanVar()
        self.checkbox = ctk.CTkCheckBox(master=self.frame16, text=f"(Experimental)\nWrite base dsdicts", font = self.font, variable = autodsdictvar2)
        self.checkbox.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.button = ctk.CTkButton(master=self.frame16, text=(self.L('ouexport')), command=self.run_adv_config, font = self.font)
        self.button.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

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
            self.confbox12.configure(state=tk.NORMAL)
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
            self.confbox12.configure(state=tk.DISABLED)
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
            self.confbox12.configure(state=tk.DISABLED)
            self.confnamebox.configure(state=tk.DISABLED)

#this one's for dropping speakers
    def changeState2(self):
        print("Toggling speaker dropping", drop_on.get())
        if drop_on.get() == "on":
            self.dropbox.configure(state=tk.NORMAL)
        elif drop_on.get() == "off":
            self.dropbox.configure(state=tk.DISABLED)
        else:
            self.dropbox.configure(state=tk.DISABLED)

#same
    def changeState3(self):
        print("Toggling speaker dropping", drop_on2.get())
        if drop_on2.get() == "on":
            self.dropbox2.configure(state=tk.NORMAL)
        elif drop_on2.get() == "off":
            self.dropbox2.configure(state=tk.DISABLED)
        else:
            self.dropbox2.configure(state=tk.DISABLED)

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

###COMMANDS###


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
    
    def show_notification(self, title, message):
        try:
            notification.notify(title=title, message=message, app_name="DiffTrainer") #apparently app_name doesn't even work unless it's compiled. great job team.
        except Exception as e:
            print(f"Notification failed: {e}")

    def last_github_commit(self):
        ds_url = "https://api.github.com/repos/agentasteriski/DiffSinger/commits?sha=mix-LN"
        fallback = datetime(2000, 1, 1, 0, 0, 0).isoformat() + 'Z'
        try:
            response = requests.get(ds_url)
            data = response.json()

            if data and isinstance(data, list) and len(data) > 0:
                last_commit = data[0]
                commit_date_str = last_commit['commit']['author']['date']
                return commit_date_str
            else:
                print("No commits found or unexpected API response.")
                return fallback
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from GitHub: {e}")
            return fallback
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return fallback
        except KeyError as e:
            print(f"KeyError accessing commit data: {e}.  API structure may have changed.")
            return fallback
        
    def ref_file_date(self, file):
        fallback = datetime(2000, 1, 1, 0, 0, 0).isoformat() + 'Z'
        try:
            timestamp = os.path.getmtime(file)
            dt_object = datetime.fromtimestamp(timestamp)
            iso_string = dt_object.isoformat() + 'Z'
            return iso_string
        except FileNotFoundError:
            print(f"Reference file not found")
            return fallback
        except OSError as e:
            print(f"Error accessing file: {e}")
            return fallback

    def dl_update(self):
        ds_commit = self.last_github_commit()
        ref_file = os.path.join(main_path, "DiffSinger/deployment/__init__.py")
        local_date = self.ref_file_date(ref_file)

        diffsinger_url = "https://github.com/agentasteriski/DiffSinger/archive/refs/heads/mix-LN.zip"
        diffsinger_zip = os.path.join(os.getcwd(), diffsinger_url.split("/")[-1])
        diffsinger_script_folder_name = "DiffSinger-mix-LN"

        vocoder_url = "https://github.com/openvpi/vocoders/releases/download/pc-nsf-hifigan-44.1k-hop512-128bin-2025.02/pc_nsf_hifigan_44.1k_hop512_128bin_2025.02.zip"
        vocoder_zip = os.path.join(os.getcwd(), vocoder_url.split("/")[-1])
        vocoder_folder = "DiffSinger/checkpoints"

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

        if os.path.exists(ds_path):
            if ds_commit > local_date:
                user_response = messagebox.askyesno(self.L('update_available1'), self.L('update_available2'))
                if not user_response:
                    return
            else:
                user_response = messagebox.askyesno(self.L('update_not_available1'), self.L('update__not_available2'))
                if not user_response:
                    return

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

        response = requests.get(diffsinger_url, stream = True)
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(total = total_size, unit = "B", unit_scale = True, desc = "downloading DiffSinger") as progress_bar:
            with open("mix-LN.zip", "wb") as f:
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

        try: os.mkdir("raw_data")
        except FileExistsError: pass

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
        with open("DiffSinger/configs/variance.yaml", "w", encoding = "utf-8") as config3:
            yaml.dump(var_config, config3, default_flow_style=False, sort_keys=False)
        new_f0_max=1600
        with open("DiffSinger/utils/binarizer_utils.py", "r", encoding = "utf-8") as f:
            f0_read = f.read()
        up_f0_val = re.sub(r"f0_max\s*=\s*.*", f"f0_max={new_f0_max},", f0_read)
        with open("DiffSinger/utils/binarizer_utils.py", "w", encoding = "utf-8") as f:
            f.write(up_f0_val)

        self.show_notification(self.L('setup_completo1'), self.L('setup_completo2'))

        print("Setup Complete!")


    def grab_raw_data(self):
        self.raw_data = filedialog.askdirectory(title="Select raw data folder", initialdir = "raw_data")
        print("raw data path: " + self.raw_data)

    def convert2csv(self):
        segmenting = self.segvar.get()
        seglength = self.seglength.get()
        if segmenting == True:
            base_name = os.path.basename(self.raw_data)
            segdata_name = base_name + "_segmented"
            segdata_folder = os.path.join("raw_data", segdata_name)
            report_path = os.path.join(segdata_folder, "report.txt")
            corpus_segmenter.process_folder(self.raw_data, segdata_folder, seglength, report_path)
            liteconvert.auto_config(segdata_folder)
            auto_config = os.path.join(segdata_folder, "auto_lang_config.json")
            liteconvert.lab2csv(segdata_folder, auto_config)

            try:
                    estimatemidi = self.estvar.get()
                    if estimatemidi == True:
                        #print("should estimate MIDI")
                        base_dir = Path(segdata_folder)
                        subdirs = [d for d in base_dir.rglob('*') if d.is_dir() and d.name != 'wavs']
                        subdirs.append(base_dir)
                        for speaker in subdirs:
                            transcription = speaker / 'transcriptions.csv'
                            if not transcription.exists(): 
                                continue
                            speaker_path = str(speaker)
                            if os.path.isdir(speaker_path):
                                print(f"running SOME on {speaker}")
                                cmdstage = [realpython, "SOME/batch_infer.py", "--model", "DiffSinger/checkpoints/SOME/0119_continuous256_5spk/model_ckpt_steps_100000_simplified.ckpt", "--dataset", speaker_path, "--overwrite"]
                                command2 = " ".join(cmdstage)
                                subprocess.run(command2, check=True, shell=True)
                    else:
                        pass
            except Exception as e:
                    print(f"Error during SOME pitch generation: {e}")
            self.show_notification(self.L('segdone1'), self.L('segdone2'))

        else:
            liteconvert.auto_config(self.raw_data)
            auto_config = os.path.join(self.raw_data, "auto_lang_config.json")
            liteconvert.lab2csv(self.raw_data, auto_config)
            try:
                    estimatemidi = self.estvar.get()
                    if estimatemidi == True:
                        base_dir = Path(self.raw_data)
                        subdirs = [d for d in base_dir.rglob('*') if d.is_dir() and d.name != 'wavs']
                        subdirs.append(base_dir)
                        for speaker in subdirs:
                            transcription = speaker / 'transcriptions.csv'
                            if not transcription.exists(): 
                                continue
                            speaker_path = str(speaker)
                            if os.path.isdir(speaker_path):
                                print(f"running SOME on {speaker}")
                                cmdstage = [realpython, "SOME/batch_infer.py", "--model", "DiffSinger/checkpoints/SOME/0119_continuous256_5spk/model_ckpt_steps_100000_simplified.ckpt", "--dataset", speaker_path, "--overwrite"]
                                command2 = " ".join(cmdstage)
                                subprocess.run(command2, check=True, shell=True)
                    else:
                        pass
            except Exception as e:
                    print(f"Error during SOME pitch generation: {e}")
            self.show_notification(self.L('segdone1'), self.L('segdone2'))

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
        subdirs = [f for f in sorted(os.listdir(data_folder)) if os.path.isdir(os.path.join(data_folder, f)) and not f.startswith('.')]
        spk_folders = []
        
        if len(subdirs) == 1 and subdirs[0] == "wavs":
            #single speaker, no subfolder
            speaker_name = os.path.basename(data_folder)
            spk_folders.append({
                "raw_dir": data_folder,
                "folder_name": speaker_name,
                "dict_key": speaker_name
            })
        else:
            #speakers in subfolders
            for spk in subdirs:
                spk_folders.append({
                    "raw_dir": os.path.join(data_folder, spk),
                    "folder_name": spk,
                    "dict_key": spk
                })
        
        spk_rows = []
        for i, spk_data in enumerate(spk_folders):
            raw_dir = spk_data["raw_dir"]
            folder_name = spk_data["folder_name"]
            dict_key = spk_data["dict_key"]
            
            spk_rows.append(ctk.CTkFrame(master=self.subframe2, width=340))
            spk_rows[i].grid(row=i, sticky="EW", pady=3)
            
            spk_name_box = ctk.CTkEntry(master=spk_rows[i], width=100, font=self.font)
            spk_name_box.insert(0, folder_name)
            spk_name_box.grid(column=0, row=0, padx=15, pady=3)
            
            #default selectable languages currently match premade dictionaries
            #premade dictionaries are enough to cover the phonemizer defaults(minus a few obscure/rare phonemes in DIFFS JA)
            spk_lang_select = ctk.CTkComboBox(master=spk_rows[i], values=["other", "en", "es", "fr", "ja", "ko", "th", "zh"], font=self.font)
            spk_lang_select.grid(column=1, row=0, padx=10)
            
            spk_id_select = ctk.CTkEntry(master=spk_rows[i], width=20, font=self.font)
            spk_id_select.insert(0, i) 
            spk_id_select.grid(column=2, row=0, padx=15)
            
            self.spk_info[dict_key] = (raw_dir, folder_name, spk_lang_select, spk_id_select)


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
        enable_time_aug = timeaug.get()
        duration = traindur.get()
        breathiness = trainbre.get()
        energy = trainene.get()
        pitch = trainpitch.get()
        tension = trainten.get()
        voicing = trainvoc.get()
        stretch = trainstretch.get()
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

        unique_ids = set()
        for spk_block in allspeakers:
            unique_ids.add(spk_block["spk_id"])
        num_spk = max(unique_ids) +1
        #technically less correct but using the actual number of speakers forces you to fill in the gaps
        #as long as it's higher it somehow works


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
            bitch_ass_config["augmentation_args"]["random_time_stretching"]["enabled"] = enable_time_aug
            bitch_ass_config["use_key_shift_embed"] = enable_random_aug
            bitch_ass_config["use_speed_embed"] = enable_time_aug
            bitch_ass_config["max_batch_size"] = int(batch)
            #ive never tried reaching the limit so ill trust kei's setting for this(MLo7)
            #sounds like a lot of users can go higher but 9 is a good start(Aster)
            bitch_ass_config["val_check_interval"] = int(save_interval)
            bitch_ass_config["use_energy_embed"] = energy
            bitch_ass_config["use_breathiness_embed"] = breathiness
            bitch_ass_config["use_tension_embed"] = tension
            bitch_ass_config["use_voicing_embed"] = voicing
            bitch_ass_config["use_stretch_embed"] = stretch
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
            bitch_ass_config["use_stretch_embed"] = stretch
            bitch_ass_config["use_melody_encoder"] = pitch
            bitch_ass_config["binarization_args"]["prefer_ds"] = ds
            if pre_type==True:
                bitch_ass_config["hnsep"] = "vr"
            else:
                bitch_ass_config["hnsep"] = "world"
            if backbone_type== "wavenet":
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
            editor.geometry("380x360")
        elif is_macos():
            editor.geometry("400x400")
        elif is_linux():
            editor.geometry("445x420")
        editor.title("DiffTrainer Langloader")
        editor.iconpath = ImageTk.PhotoImage(file=os.path.join(main_path, "assets","hard-drive.png"))
        editor.wm_iconbitmap()
        editor.iconphoto(False, editor.iconpath)
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
        dictbox = CTkListbox(dictframe, width=200, font = self.font)
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
        editor.lift()

    def update_dictbox(self):
        dictbox.delete(0, tk.END)
        for key in langloader['dictionaries']:
            dictbox.insert(tk.END, f"{key}: {langloader['dictionaries'][key]}")
    
    def add_entry(self):
        languagebox = ctk.CTkInputDialog(text=(self.L('enterdict1')), title=(self.L('input')), font=self.font)
        language = languagebox.get_input()
        if language:
            phonemebox = ctk.CTkInputDialog(text=(self.L('enterdict2')), title=(self.L('input')), font=self.font)
            phoneme_file = phonemebox.get_input()
            if phoneme_file:
                langloader['dictionaries'][language] = phoneme_file
                self.update_dictbox()
    
    def remove_entry(self):
        try:
            index = dictbox.curselection()
            if index is not None:
                language = list(langloader['dictionaries'].keys())[index]
                del langloader['dictionaries'][language]
                self.update_dictbox()
            else:
                print("No dictionary selected")
        except Exception as e:
            print(f"Error removing dictionary: {e}")
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
                    break
            else:
                print("CUDA version not found")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("CUDA is not available")
        os.chdir(ds_path)
        os.environ["PYTHONPATH"] = ds_path
        sys.path.insert(0, ds_path)
        cmdstage = [realpython, 'scripts/binarize.py', '--config', configpath]
        command = " ".join(cmdstage)
        try: 
            subprocess.run(command, check=True, shell=True)
            self.show_notification(self.L('binarydone1'), self.L('binarydone2'))
        except: 
            print("Binarization stopped due to error.")
            self.show_notification(self.L('binaryerror1'), self.L('generalerror2'))
        os.chdir(main_path)

    def load_config_function(self):
        global configpath
        configpath = filedialog.askopenfilename(title="Select config file", initialdir="DiffSinger/configs/", filetypes=[("Config files", "*.yaml")])
        print(configpath)

    def train_function(self):
            if not configpath or not ckpt_save_dir:
                self.label.config(text="Please select your config and the data you would like to train first!")
                return
            try:
                output = subprocess.check_output(["nvcc", "--version"], stderr=subprocess.STDOUT).decode()
                lines = output.split("\n")
                for line in lines:
                    if "release" in line.lower():
                        version = line.split()[-1]
                        print("CUDA version:", version)
                        break
                else:
                    print("CUDA version not found")
            except (FileNotFoundError, subprocess.CalledProcessError):
                print("CUDA is not available")
            try:
                os.chdir(ds_path)
                os.environ["PYTHONPATH"] = str(ds_path)
                sys.path.insert(0, str(ds_path))
                cmdstage = [realpython, 'scripts/train.py', '--config', configpath, '--exp_name', ckpt_save_dir, '--reset']
                command = " ".join(cmdstage)
                subprocess.run(command, check=True, shell=True)
            except KeyboardInterrupt: #this doesn't even work
                print("Training ended by user.")
            except Exception: print("Training ended.")
            os.chdir(main_path)

    def run_onnx_export(self):
            os.chdir(ds_path)
            os.environ["PYTHONPATH"] = str(ds_path)
            sys.path.insert(0, str(ds_path))
            if drop_on.get() == "on":
                drop_command = onnxexport.drop_speakers(ckpt_save_dir, dropspk)
                print("Dropping speakers", dropspk.get())
                try: subprocess.run(drop_command, check=True, shell=True)
                except: 
                    print("Error dropping speakers")
            onnxexport.prep_onnx_export(ckpt_save_dir)
            command = onnxexport.writecmd(ckpt_save_dir, expselect, drop_on)
            try: subprocess.run(command, check=True, shell=True)
            except: 
                print("Error exporting onnx")
            onnxexport.onnx_cleanup(ckpt_save_dir)
            print("Done!")
            os.chdir(main_path)

    def run_onnx_export2(self):
            os.chdir(ds_path)
            os.environ["PYTHONPATH"] = str(ds_path)
            sys.path.insert(0, str(ds_path))
            if drop_on2.get() == "on":
                drop_command = onnxexport.drop_speakers(ckpt_save_dir, dropspk2)
                print("Dropping speakers", dropspk2.get())
                try: subprocess.run(drop_command, check=True, shell=True)
                except: 
                    print("Error dropping speakers")
            onnxexport.prep_onnx_export(ckpt_save_dir)
            command = onnxexport.writecmd(ckpt_save_dir, expselect2, drop_on2)
            subprocess.run(command, check=True, shell=True)
            onnxexport.onnx_cleanup(ckpt_save_dir)
            print("Done!")
            os.chdir(main_path)


    def get_aco_folder(self):
        self.aco_folder_dir = filedialog.askdirectory(title="Select folder with acoustic checkpoints", initialdir = "DiffSinger/checkpoints/")
        print("Acoustic folder: " + self.aco_folder_dir)

    def get_var_folder(self):
        self.var_folder_dir = filedialog.askdirectory(title="Select folder with variance checkpoints", initialdir = "DiffSinger/checkpoints/")
        print("Variance folder: " + self.var_folder_dir)

    def get_dur_folder(self):
        self.dur_folder_dir = filedialog.askdirectory(title="Select folder with duration checkpoints", initialdir = "DiffSinger/checkpoints/")
        print("Duration folder: " + self.dur_folder_dir)

    def get_pitch_folder(self):
        self.pitch_folder_dir = filedialog.askdirectory(title="Select folder with pitch checkpoints", initialdir = "DiffSinger/checkpoints/")
        print("Pitch folder: " + self.pitch_folder_dir)

    def get_vocoder(self):
        self.vocoder_onnx = filedialog.askopenfilename(title="OPTIONAL: Select custom vocoder onnx", initialdir="DiffSinger/checkpoints/", filetypes=[("ONNX files", "*.onnx")])
        print("Custom vocoder:" + self.vocoder_onnx)

    def get_OU_folder(self):
        self.ou_export_location = filedialog.askdirectory(title="Select save folder")
        print("export path: " + self.ou_export_location)

    def run_OU_config(self):
        os.chdir(main_path)
        os.chdir("DiffSinger")
        os.environ["PYTHONPATH"] = "."

        basicexport.run_OU_config(ou_name_var=ou_name_var, ou_export_location=self.ou_export_location, aco_folder_dir=self.aco_folder_dir, var_folder_dir=self.var_folder_dir, vocoder_onnx=self.vocoder_onnx, autodsdictvar=autodsdictvar)


    def run_adv_config(self): #see basic export for most of the comments
        os.chdir(main_path)
        os.chdir("DiffSinger")
        os.environ["PYTHONPATH"] = "."

        advexport.run_adv_config(ou_name_var2=ou_name_var2, ou_export_location=self.ou_export_location, aco_folder_dir=self.aco_folder_dir, dur_folder_dir=self.dur_folder_dir, var_folder_dir=self.var_folder_dir, pitch_folder_dir=self.pitch_folder_dir, vocoder_onnx=self.vocoder_onnx, autodsdictvar2=autodsdictvar2)



class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DiffTrainer")
        self.iconpath = ImageTk.PhotoImage(file=os.path.join(main_path, "assets","hard-drive.png"))
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

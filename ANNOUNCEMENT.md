# Announcement: Major pending changes ( *[中文（正體）](./ANNOUNCEMENT-zh.md)* )

### Version 0.1.18 will be the last version to support the existing installer and launcher method. Due to directly conflicting package requirements(SOME/training requiring Torch > 2.0, ONNX exporting requiring Torch < 2.0), Conda or self-management of environments will be required. With this in mind, the install and launch .bat files will be replaced with the following steps:
- **(if needed)** run *conda_installer.bat*(formerly *python_installer.bat*) to quickly install a copy of Miniconda3. The resulting program is not exclusive to DiffTrainer and can be used to manage requirements for other Python 3.x projects. Existing Anaconda/Miniconda installs will be detected by the following setup.
- run *setup.bat* to automatically create and configure two environments, DifftrainerA and DifftrainerB. During this process, the *torchdrop* scripts automatically detect any installed CUDA version and selects appropriate versions of Torch for CPU or GPU.
	- to manually configure environments, requirement files are located in /assets/. Run both *torchdrop* scripts  in their respective environments to detect the required Torch version and complete dependency installation.
- Use *Update Tools* on the main tab of DiffTrainer to download the
- For preprocessing, binarization, and training, use *run_guiA.bat* to launch. Use *run_guiB.bat* when exporting ONNX files.

### Due to the extensive changes, it is recommended to remove all older versions of DiffTrainer and accompanying files before configuring DiffTrainer 0.2.0. If *python_installer.bat* was used to install a dedicated copy of Python, use the uninstaller program in the /python folder.

### Users are encouraged to manually upgrade to version 0.2.0 in advance of its release on the main branch by downloading the [SOME branch](https://github.com/agentasteriski/DiffTrainer/tree/SOME). 

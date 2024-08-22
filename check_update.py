import requests, os, zipfile, shutil
from tqdm import tqdm
import re
from tkinter import messagebox

main_path = os.getcwd()

gui_github = requests.get("https://raw.githubusercontent.com/agentasteriski/DiffTrainer/main/difftrainer.py")
github_version = re.search(r'version\s*=\s*[\'"]([^\'"]+)[\'"]', gui_github.text)
github_version = github_version.group(1)

with open("difftrainer.py", "r", encoding = "utf-8") as gui_local:
	gui_local = gui_local.read()
local_version = re.search(r'version\s*=\s*[\'"]([^\'"]+)[\'"]', gui_local)
local_version = local_version.group(1)

if local_version >= github_version:
	pass
else:
	update_prompt = messagebox.askyesno("Notice", f"Latest difftrainer version is {github_version}.\n\nYou currently have {local_version}.\n\nWould you like to update difftrainer?")
	if update_prompt:
		url = "https://github.com/agentasteriski/DiffTrainer/archive/refs/heads/main.zip"
		zip = os.path.join(os.getcwd(), url.split("/")[-1])
		folder = "difftrainer-main"

		if os.path.exists("DiffTrainer-main"):
			try:
				shutil.rmtree("DiffTrainer-main")
			except Exception as e:
				print(f"Error deleting the existing 'DiffTrainer-main' folder: {e}")
		response = requests.get(url, stream = True)
		total_size = int(response.headers.get("content-length", 0))
		with tqdm(total = total_size, unit = "B", unit_scale = True, desc = "downloading DiffTrainer...") as progress_bar:
			with open("main.zip", "wb") as f:
				for chunk in response.iter_content(chunk_size = 1024):
					if chunk:
						f.write(chunk)
						progress_bar.update(len(chunk))

		with zipfile.ZipFile(zip, "r") as zip_ref:
			zip_ref.extractall()
		os.remove(zip)
		if os.path.exists(folder):
			shutil.rmtree("strings")
			shutil.move(f"{folder}/strings", main_path)
			shutil.rmtree("assets")
			shutil.move(f"{folder}/assets", main_path)
			for filename in os.listdir(main_path):
				if filename.endswith(".bat"):
					os.remove(filename)
			for filename in os.listdir(folder):
				if filename.endswith(".bat"):
					shutil.move(os.path.join(folder, filename), main_path)
			for filename in os.listdir(main_path):
				if filename.endswith(".txt"):
					os.remove(filename)
			for filename in os.listdir(main_path):
				if filename.endswith(".txt"):
					shutil.move(os.path.join(folder, filename), main_path)
			os.remove("difftrainer.py")
			os.remove("quickinference.py")
			shutil.move(f"{folder}/difftrainer.py", main_path)
			shutil.move(f"{folder}/quickinference.py", main_path)
			if os.path.isfile("torchdropA.py"):
				os.remove("torchdropA.py")
				if os.path.isfile(f"{folder}/torchdropA.py"):
					shutil.move(f"{folder}/torchdropA.py", main_path)
			if os.path.isfile("torchdropB.py"):
				os.remove("torchdropB.py")
				if os.path.isfile(f"{folder}/torchdropB.py"):
					shutil.move(f"{folder}/torchdropB.py", main_path)

			shutil.rmtree(folder)

	else:
		pass

from difftrainer import App #import later to prevent the app from using the older ver <3
if __name__ == "__main__":
	app = App()
	app.mainloop()

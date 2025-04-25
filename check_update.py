import requests, os, zipfile, shutil, subprocess
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

reqs_url = "https://raw.githubusercontent.com/agentasteriski/DiffTrainer/refs/heads/main/requirements.txt"
reqresponse = requests.get(reqs_url)
with open('requirements_compare.txt', 'wb') as f:
            f.write(reqresponse.content)
reqs_new = "requirements_compare.txt"
reqs = "requirements.txt"
with open(reqs, 'r') as f1:
	with open(reqs_new, 'r') as f2:
		if f1.read() != f2.read():
				update_reqs = True
		else:
				update_reqs = False
try:
	os.remove(reqs_new)
except:
	print("Error removing temporary comparison file")


if local_version >= github_version:
	pass
else:
	update_prompt = messagebox.askyesno("Notice", f"Latest DiffTrainer version is {github_version}.\n\nYou currently have {local_version}.\n\nWould you like to update DiffTrainer?")
	if update_prompt:
		url = "https://github.com/agentasteriski/DiffTrainer/archive/refs/heads/main.zip"
		zip = os.path.join(os.getcwd(), url.split("/")[-1])
		folder = "DiffTrainer-main"




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
			[os.remove(filename)
			for filename in os.listdir(main_path) if filename.endswith(".bat")]
			[shutil.move(os.path.join(folder, filename), main_path)
        	for filename in os.listdir(folder) if filename.endswith(".bat")]
			[os.remove(filename)
			for filename in os.listdir(main_path) if filename.endswith(".txt")]
			[shutil.move(os.path.join(folder, filename), main_path)
        	for filename in os.listdir(folder) if filename.endswith(".txt")]
			[os.remove(filename)
			for filename in os.listdir(main_path) if filename.endswith(".py")]
			[shutil.move(os.path.join(folder, filename), main_path)
        	for filename in os.listdir(folder) if filename.endswith(".py")]
			
			shutil.rmtree(folder)

		if update_reqs == True:
			try:
				subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])
			except subprocess.CalledProcessError as e:
				print(f"Error updating dependencies: {e}")

	else:
		pass

from difftrainer import App #import later to prevent the app from using the older ver <3
if __name__ == "__main__":
	app = App()
	app.mainloop()

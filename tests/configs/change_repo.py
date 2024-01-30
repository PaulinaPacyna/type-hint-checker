import os
import glob

path = os.getenv("config_path", os.path.join("tests", "configs"))
rev = os.getenv("rev", "main")
repo = "https://github.com/PaulinaPacyna/type-hint-checker"
for file_name in glob.glob(os.path.join(path, "*.yaml")):
    with open(file_name, "r", encoding="utf-8") as file:
        file_content = file.read()
        file_content = file_content.replace(
            "repo: local",
            f"repo: {repo}\n    rev: {rev}",
        )
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(file_content)

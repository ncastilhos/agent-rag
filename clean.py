#Delete every .md file in Docs folder and all its subfolders
import os

for root, dirs, files in os.walk("Docs"):
    for file in files:
        if file.endswith(".md"):
            os.remove(os.path.join(root, file))
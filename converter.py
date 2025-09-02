from  markitdown import MarkItDown
import os
import re
import shutil

md = MarkItDown()

origin_folder = "Docs"
new_folder = origin_folder + "_md"

#Convert all docs to markdown
for root, dirs, files in os.walk(origin_folder):
    for file in files:
        filename = os.path.join(root, file)
        result = md.convert(filename)
        # print(result.text_content)
        print(filename)
        output_filename = re.sub(r"\.\w{2,4}$", ".md", filename)
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(result.text_content)

#Make a copy of the origin folder
if not os.path.exists(new_folder):
    shutil.copytree(origin_folder, new_folder)

#Delete every non .md file in the new folder
for root, dirs, files in os.walk(new_folder):
    for file in files:
        if not file.endswith(".md"):
            os.remove(os.path.join(root, file))

#Remove every .md file in the origin folder
for root, dirs, files in os.walk(origin_folder):
    for file in files:
        if file.endswith(".md"):
            os.remove(os.path.join(root, file))
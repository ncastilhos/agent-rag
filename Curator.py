#Go through every file in the Docs_md folder and run a regex replace all
import os
import re
import shutil
from markitdown import MarkItDown, UnsupportedFormatException, FileConversionException
from scrape import Scrape

def convert_documents(origin_folder: str, new_folder: str):
    """
    Converts all documents in the origin folder to markdown, places them in a new
    folder, and cleans up the directory structures.

    Args:
        origin_folder (str): The source folder containing files to convert.
        new_folder (str): The destination folder for the markdown files.
    """
    md = MarkItDown()

    # Convert all docs to markdown
    print(f"Converting files from '{origin_folder}'...")
    for root, _, files in os.walk(origin_folder):
        for file in files:
            filename = os.path.join(root, file)
            try:
                result = md.convert(filename)
                print(f"  Successfully converted: {filename}")
                output_filename = re.sub(r"\.\w{2,4}$", ".md", filename)
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write(result.text_content)
            except (UnsupportedFormatException, FileConversionException) as e:
                print(f"  Skipping conversion for {filename}: {e}")
            except Exception as e:
                print(f"  An unexpected error occurred with {filename}: {e}")

    # Make a copy of the origin folder
    if not os.path.exists(new_folder):
        print(f"\nCreating new folder '{new_folder}' with markdown files...")
        shutil.copytree(origin_folder, new_folder)

    # Delete every non .md file in the new folder
    print(f"Cleaning up non-markdown files in '{new_folder}'...")
    for root, _, files in os.walk(new_folder):
        for file in files:
            if not file.endswith(".md"):
                os.remove(os.path.join(root, file))

    # Remove every .md file in the origin folder
    print(f"Cleaning up generated markdown files in '{origin_folder}'...")
    for root, _, files in os.walk(origin_folder):
        for file in files:
            if file.endswith(".md"):
                os.remove(os.path.join(root, file))
    print("\nConversion and cleanup complete.")


def clean_markdown_files(*directories):
    for directory in directories:
        print(f"Cleaning files in directory: {directory}")
        for root, _, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith(".md"):
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    #Remove repetitive footer/header data
                    content = re.sub(r'PROCEDIMENTO OPERACIONAL PADRÃO SETOR SUPRIMENTOS(\n(.*)){10}', '', content)
                    content = re.sub(r'PROCEDIMENTO OPERACIONAL PADRÃO(\n(.*)){14}', '', content)
                    content = re.sub(r'DGT TECNOLOGIA LTDA(\n(.*)){7}', '', content)
                    content = re.sub(r'DGT TECNOLOGIA LTDA', '', content)
                    content = re.sub(r'R. Evaristo José Fernandes, 121,(\n(.*)){9}', '', content)
                    content = re.sub(r'.*\.\w{2,4}.*', '', content)
                    content = re.sub(r'### Notes:\n(.*)', '', content)
                    content = re.sub(r'.*(\n.*){12}.*PADRÃO\n\n(Elaborador).*(\n.*){6}', '', content)
                    #Sumário
                    content = re.sub(r'.*\.{4}.*\n.*|^\d\.\d$|^SUMÁRIO$|^\d{2}$\n.*', '', content, flags=re.MULTILINE)


                    #### Notes:\n(.*)

                    # Example: Remove lines starting with '---'
                    # content = re.sub(r'^---\s*$', '', content, flags=re.MULTILINE)
                    # Example: Replace multiple newlines with a single newline
                    content = re.sub(r'\n\n+', '\n\n', content)
                    # Example: Remove leading/trailing whitespace from each line
                    content = '\n'.join([line.strip() for line in content.split('\n')])

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Cleaned: {file_path}")

if __name__ == "__main__":
    Scrape()
    
    source_folder = "Docs"
    dest_folder = source_folder + "_md"
    convert_documents(source_folder, dest_folder)

    # You can add more directories to this list
    directories_to_clean = ["Docs_md", "ScrapedData"]
    clean_markdown_files(*directories_to_clean)

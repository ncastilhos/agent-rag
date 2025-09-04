from markitdown import MarkItDown, UnsupportedFormatException, FileConversionException
import os
import re
import shutil


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


if __name__ == "__main__":
    SOURCE_FOLDER = "Docs"
    DEST_FOLDER = SOURCE_FOLDER + "_md"
    convert_documents(SOURCE_FOLDER, DEST_FOLDER)
#Go through every file in the Docs_md folder and run a regex replace all
import os
import re

def clean_markdown_files(directory):
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
    docs_directory = "Docs_md"
    clean_markdown_files(docs_directory)

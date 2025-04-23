import os
import time
import shutil
from codefile import generate_page

def traverse_and_process(source, destination, template_path):
    # Traverse through `source` directory
    for dirpath, _, filenames in os.walk(source):
        for filename in filenames:
            if filename.endswith(".md"):  # Process Markdown files
                input_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(dirpath, source)
                dest_dir = os.path.join(destination, rel_path)
                os.makedirs(dest_dir, exist_ok=True)

                dest_path = os.path.join(dest_dir, filename.replace('.md', '.html'))
                generate_page(input_path, template_path, dest_path)

def main():
    template_path = 'template.html'
    
    if os.path.exists("public"):
        shutil.rmtree('public')
        print("Removing Existing public folder...")
        
    os.makedirs('public', exist_ok=True)
    print('Creating new public folder...')
    copy_directory('static', 'public')
    traverse_and_process('content', 'public', template_path)
        

def copy_directory(source, destination):
    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        dest_path = os.path.join(destination, item)
        
        if os.path.isfile(source_path):
            print(f"Copying file: {source_path} to {dest_path}")
            shutil.copy(source_path, dest_path)
        else:
            print(f"Creating directory: {dest_path}")
            if not os.path.exists(dest_path):
                os.mkdir(dest_path)
            copy_directory(source_path, dest_path)

if __name__ == "__main__":
    main()
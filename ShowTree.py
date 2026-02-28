import os

def print_tree(startpath):
    # Add folders you want to ignore here
    ignore_dirs = {'venv', '__pycache__', '.git', '.idea', '.vscode'}
    ignore_files = {'__init__.py', '.DS_Store'}

    for root, dirs, files in os.walk(startpath):
        # 1. Filter out ignored directories in-place
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        # 2. Calculate indentation
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        
        # 3. Print the folder name
        print(f'{indent}{os.path.basename(root)}/')
        
        # 4. Print the files
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f not in ignore_files:
                print(f'{subindent}{f}')

if __name__ == "__main__":
    print_tree('.')
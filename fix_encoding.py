import os

files_to_fix = [
    "backend/app/__init__.py",
    "backend/app/api/__init__.py",
    "backend/app/services/__init__.py",
    "backend/app/core/__init__.py"
]

def fix_files():
    for file_path in files_to_fix:
        try:
            # Force write empty string or comment with utf-8 encoding
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# -*- coding: utf-8 -*-\n")
            print(f"Fixed: {file_path}")
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")

if __name__ == "__main__":
    fix_files()

import os

def check_for_null_bytes(directory):
    issues = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, 'rb') as f:
                        content = f.read()
                        if b'\x00' in content:
                            print(f"FOUND NULL BYTES: {path}")
                            issues.append(path)
                        else:
                            pass
                            # print(f"OK: {path}")
                except Exception as e:
                    print(f"Error reading {path}: {e}")
    if not issues:
        print("No files with null bytes found.")

if __name__ == "__main__":
    print("Scanning for null bytes...")
    check_for_null_bytes("backend")

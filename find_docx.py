import os
from pathlib import Path

def find_docx_files(start_path="."):
    """Find all .docx files starting from a directory."""
    docx_files = []
    
    try:
        for root, dirs, files in os.walk(start_path):
            for file in files:
                if file.lower().endswith('.docx'):
                    full_path = os.path.join(root, file)
                    docx_files.append(full_path)
    except Exception as e:
        print(f"Error searching: {e}")
    
    return docx_files

print("Searching for .docx files...")
docx_files = find_docx_files(".")

if docx_files:
    print(f"Found {len(docx_files)} .docx files:")
    for file in docx_files:
        print(f"  {file}")
else:
    print("No .docx files found in current directory and subdirectories")
    
    # Check if there are any in common locations
    common_paths = [
        "./data",
        "./documents", 
        "./Downloads",
        "C:/Users/*/Downloads",
        "C:/Users/*/Documents"
    ]
    
    print("\nChecking common locations...")
    for path in common_paths:
        if os.path.exists(path):
            files = find_docx_files(path)
            if files:
                print(f"Found in {path}: {len(files)} files")
                for f in files[:3]:  # Show first 3
                    print(f"  {f}")
import os
from typing import List, Dict

def load_sharepoint_exports(export_dir: str = "./data/sharepoint_exports") -> List[Dict[str, str]]:
    """Load manually exported SharePoint documents."""
    documents = []
    
    if not os.path.exists(export_dir):
        print(f"SharePoint export directory not found: {export_dir}")
        return documents
    
    # Load all text files from export directory
    for root, dirs, files in os.walk(export_dir):
        for file in files:
            if file.lower().endswith(('.txt', '.md')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    documents.append({
                        'content': content,
                        'source': file_path,
                        'filename': file,
                        'type': 'sharepoint_export'
                    })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return documents
import os
from typing import List, Dict
from pathlib import Path
from docx import Document

def load_documents(docs_dir: str) -> List[Dict[str, str]]:
    """Load markdown and text documents from directory."""
    documents = []
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        return documents
    
    for file_path in docs_path.rglob("*"):
        if file_path.suffix.lower() in ['.md', '.txt', '.docx']:
            try:
                if file_path.suffix.lower() == '.docx':
                    # Extract text from Word document
                    doc = Document(file_path)
                    content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                else:
                    # Read text/markdown files
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                
                documents.append({
                    'content': content,
                    'source': str(file_path),
                    'filename': file_path.name,
                    'type': 'document'
                })
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    return documents
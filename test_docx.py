import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

docs_dir = os.getenv('DOCS_DIR', './data/mds')
print(f"Checking directory: {docs_dir}")

docs_path = Path(docs_dir)
if not docs_path.exists():
    print("Directory does not exist!")
else:
    print("Files found:")
    all_files = list(docs_path.rglob("*"))
    
    for file_path in all_files:
        if file_path.is_file():
            print(f"  {file_path.suffix.lower()}: {file_path}")
    
    # Test docx loading
    docx_files = [f for f in all_files if f.suffix.lower() == '.docx']
    print(f"\nFound {len(docx_files)} .docx files:")
    
    for docx_file in docx_files:
        print(f"  {docx_file}")
        try:
            from docx import Document
            doc = Document(docx_file)
            content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            print(f"    Content length: {len(content)} characters")
            print(f"    Preview: {content[:100]}...")
        except Exception as e:
            print(f"    Error: {e}")
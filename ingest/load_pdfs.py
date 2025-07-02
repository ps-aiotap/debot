import os
from typing import List, Dict
from pathlib import Path
import pdfplumber
from cache_utils import cache_crawled_content, get_cached_crawled_content

def load_pdfs(pdf_dir: str) -> List[Dict[str, str]]:
    """Load and parse PDF documents with caching."""
    documents = []
    pdf_path = Path(pdf_dir)
    
    if not pdf_path.exists():
        return documents
    
    for file_path in pdf_path.rglob("*.pdf"):
        try:
            # Check cache first
            cache_key = f"pdf:{file_path.name}:{file_path.stat().st_mtime}"
            cached_content = get_cached_crawled_content(cache_key)
            
            if cached_content:
                content = cached_content
            else:
                # Extract text from PDF
                content = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            content += page_text + "\n"
                
                # Cache the extracted content
                cache_crawled_content(cache_key, content)
            
            if content.strip():
                documents.append({
                    'content': content,
                    'source': str(file_path),
                    'filename': file_path.name,
                    'type': 'pdf'
                })
                
        except Exception as e:
            print(f"Error loading PDF {file_path}: {e}")
    
    return documents
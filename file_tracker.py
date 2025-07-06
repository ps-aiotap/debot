import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

class FileTracker:
    def __init__(self, cache_file: str = ".file_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load file cache from disk."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_cache(self):
        """Save file cache to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except:
            pass
    
    def _get_file_info(self, filepath: str) -> Dict:
        """Get file modification time and size."""
        stat = os.stat(filepath)
        return {
            "mtime": stat.st_mtime,
            "size": stat.st_size,
            "path": filepath
        }
    
    def get_changed_files(self, directories: List[str], extensions: List[str] = None) -> Tuple[List[str], List[str]]:
        """
        Get lists of new/changed files and unchanged files.
        Returns: (changed_files, unchanged_files)
        """
        if extensions is None:
            extensions = ['.pdf', '.docx', '.md', '.txt', '.xlsx']
        
        current_files = []
        for directory in directories:
            if not os.path.exists(directory):
                continue
            for ext in extensions:
                current_files.extend(Path(directory).rglob(f"*{ext}"))
        
        changed_files = []
        unchanged_files = []
        
        for filepath in current_files:
            filepath_str = str(filepath)
            current_info = self._get_file_info(filepath_str)
            cached_info = self.cache.get(filepath_str)
            
            if (not cached_info or 
                cached_info["mtime"] != current_info["mtime"] or 
                cached_info["size"] != current_info["size"]):
                changed_files.append(filepath_str)
                self.cache[filepath_str] = current_info
            else:
                unchanged_files.append(filepath_str)
        
        # Remove deleted files from cache
        existing_files = {str(f) for f in current_files}
        self.cache = {k: v for k, v in self.cache.items() if k in existing_files}
        
        self._save_cache()
        return changed_files, unchanged_files
    
    def mark_processed(self, filepaths: List[str]):
        """Mark files as processed (update cache)."""
        for filepath in filepaths:
            if os.path.exists(filepath):
                self.cache[filepath] = self._get_file_info(filepath)
        self._save_cache()
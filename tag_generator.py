"""
Auto-generate context tags from CSV files and combine with manual tags.
"""

import pandas as pd
from pathlib import Path
from collections import Counter
import re
from context_tags import CONTEXT_TAGS

def extract_keywords_from_csv(csv_file_path: str, min_frequency: int = 2) -> dict:
    """Extract frequent keywords from CSV content to suggest new tags."""
    
    try:
        df = pd.read_csv(csv_file_path)
        
        # Combine all text content
        all_text = ""
        text_columns = ['Title', 'Step Action', 'Step Expected']
        
        for col in text_columns:
            if col in df.columns:
                all_text += " " + df[col].fillna("").astype(str).str.cat(sep=" ")
        
        # Extract meaningful words (3+ characters, not common words)
        words = re.findall(r'\b[A-Za-z]{3,}\b', all_text.lower())
        
        # Comprehensive stop words list
        stop_words = {
            # Common words
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use',
            # Test case specific words
            'test', 'case', 'step', 'verify', 'check', 'should', 'will', 'able', 'need', 'when', 'then', 'with', 'from', 'that', 'this', 'they', 'have', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'would', 'there', 'what', 'about', 'after', 'first', 'never', 'these', 'think', 'where', 'being', 'every', 'great', 'might', 'shall', 'still', 'those', 'under', 'while',
            # UI/Testing words
            'page', 'click', 'button', 'link', 'display', 'show', 'open', 'close', 'select', 'enter', 'field', 'form', 'table', 'list', 'item', 'view', 'window', 'screen', 'menu', 'option', 'value', 'text', 'data', 'information', 'details', 'record', 'records', 'count', 'number', 'total', 'only', 'based', 'selected', 'applied', 'update', 'displayed', 'visible'
        }
        
        # Filter meaningful business/domain words only
        filtered_words = []
        for word in words:
            if (word not in stop_words and 
                len(word) > 4 and  # Longer words are more meaningful
                not word.isdigit() and  # Skip numbers
                word.isalpha()):  # Only alphabetic words
                filtered_words.append(word)
        
        # Count frequency
        word_counts = Counter(filtered_words)
        
        # Get frequent words
        frequent_words = {word: count for word, count in word_counts.items() if count >= min_frequency}
        
        return frequent_words
        
    except Exception as e:
        print(f"Error extracting keywords from {csv_file_path}: {e}")
        return {}

def suggest_new_tags(excel_dir: str) -> dict:
    """Analyze all CSV files and suggest new context tags."""
    
    excel_path = Path(excel_dir)
    suggestions = {}
    
    for csv_file in excel_path.rglob("*.csv"):
        print(f"Analyzing {csv_file.name}...")
        keywords = extract_keywords_from_csv(csv_file)
        
        # Group similar keywords into potential tags
        module_name = csv_file.stem.split('_')[0] if '_' in csv_file.stem else csv_file.stem
        
        # Filter keywords that aren't already covered
        existing_keywords = set()
        for tag_keywords in CONTEXT_TAGS.values():
            existing_keywords.update(tag_keywords)
        
        # Focus on domain-specific, high-frequency keywords
        new_keywords = {}
        for k, v in keywords.items():
            if (k not in existing_keywords and 
                v >= 4 and  # Higher frequency threshold
                len(k) > 5 and  # Longer, more specific terms
                any(domain in k for domain in ['acquisition', 'budget', 'report', 'dashboard', 'filter', 'status', 'management', 'leadership', 'target', 'weekly', 'heatmap', 'trigger', 'pipeline'])):
                new_keywords[k] = v
        
        if new_keywords:
            suggestions[module_name] = new_keywords
    
    return suggestions

def generate_tag_suggestions(excel_dir: str):
    """Generate and display tag suggestions."""
    
    print("🔍 Analyzing CSV files for new tag suggestions...\n")
    suggestions = suggest_new_tags(excel_dir)
    
    if not suggestions:
        print("No new tag suggestions found.")
        return
    
    print("📋 SUGGESTED NEW TAGS:")
    print("=" * 50)
    
    for module, keywords in suggestions.items():
        print(f"\n🏷️  {module.upper()} MODULE:")
        
        # Group keywords by similarity
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        
        suggested_tags = []
        for keyword, count in sorted_keywords[:10]:  # Top 10 keywords
            tag_name = keyword.replace('_', ' ').title()
            suggested_tags.append(f"'{tag_name}': ['{keyword}']")
        
        if suggested_tags:
            print("   Add to context_tags.py:")
            for tag in suggested_tags:
                print(f"   {tag},")
    
    print(f"\n💡 To add these tags:")
    print("1. Copy relevant tags to context_tags.py")
    print("2. Group similar keywords under meaningful tag names")
    print("3. Run convert_csv_to_md.py again")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    excel_dir = os.getenv('EXCEL_DIR', './data/excel')
    generate_tag_suggestions(excel_dir)
import requests
from typing import List, Dict
from cache_utils import cache_crawled_content, get_cached_crawled_content
import re

def load_confluence_wiki(base_url: str, username: str, api_token: str, space_key: str) -> List[Dict[str, str]]:
    """Load pages from Confluence wiki."""
    documents = []
    
    try:
        # Confluence REST API
        api_url = f"{base_url}/rest/api/content"
        auth = (username, api_token)
        
        params = {
            'spaceKey': space_key,
            'expand': 'body.storage,version',
            'limit': 50
        }
        
        response = requests.get(api_url, auth=auth, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            for page in data.get('results', []):
                page_url = f"{base_url}{page['_links']['webui']}"
                
                # Check cache
                cached_content = get_cached_crawled_content(page_url)
                if cached_content:
                    content = cached_content
                else:
                    # Extract content from storage format
                    storage_content = page.get('body', {}).get('storage', {}).get('value', '')
                    # Remove HTML tags for clean text
                    content = re.sub(r'<[^>]+>', '', storage_content)
                    cache_crawled_content(page_url, content)
                
                documents.append({
                    'content': content,
                    'source': page_url,
                    'filename': page.get('title', 'Unknown'),
                    'type': 'wiki'
                })
        
    except Exception as e:
        print(f"Error loading Confluence wiki: {e}")
    
    return documents

def load_mediawiki(base_url: str, pages: List[str]) -> List[Dict[str, str]]:
    """Load pages from MediaWiki (like Wikipedia)."""
    documents = []
    
    try:
        api_url = f"{base_url}/api.php"
        
        for page_title in pages:
            params = {
                'action': 'query',
                'format': 'json',
                'titles': page_title,
                'prop': 'extracts',
                'explaintext': True
            }
            
            response = requests.get(api_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                pages_data = data.get('query', {}).get('pages', {})
                
                for page_id, page_info in pages_data.items():
                    if 'extract' in page_info:
                        page_url = f"{base_url}/wiki/{page_title}"
                        
                        documents.append({
                            'content': page_info['extract'],
                            'source': page_url,
                            'filename': page_title,
                            'type': 'wiki'
                        })
        
    except Exception as e:
        print(f"Error loading MediaWiki pages: {e}")
    
    return documents
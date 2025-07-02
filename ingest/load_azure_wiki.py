import requests
import base64
from typing import List, Dict
from cache_utils import cache_crawled_content, get_cached_crawled_content

def load_azure_devops_wiki(organization: str, project: str, wiki_id: str, pat_token: str) -> List[Dict[str, str]]:
    """Load pages from Azure DevOps Wiki."""
    documents = []
    
    try:
        # Azure DevOps REST API
        base_url = f"https://dev.azure.com/{organization}/{project}/_apis/wiki/wikis/{wiki_id}/pages"
        
        # PAT token authentication
        auth_string = base64.b64encode(f":{pat_token}".encode()).decode()
        headers = {
            'Authorization': f'Basic {auth_string}',
            'Content-Type': 'application/json'
        }
        
        # Get all pages
        response = requests.get(f"{base_url}?api-version=6.0&recursionLevel=full", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            for page in data.get('value', []):
                page_id = page.get('id')
                page_path = page.get('path', '')
                
                if page_id:
                    # Get page content
                    content_url = f"{base_url}/{page_id}?api-version=6.0&includeContent=true"
                    
                    # Check cache first
                    cached_content = get_cached_crawled_content(content_url)
                    if cached_content:
                        content = cached_content
                    else:
                        content_response = requests.get(content_url, headers=headers)
                        if content_response.status_code == 200:
                            page_data = content_response.json()
                            content = page_data.get('content', '')
                            cache_crawled_content(content_url, content)
                        else:
                            continue
                    
                    # Create web URL for the page
                    web_url = f"https://dev.azure.com/{organization}/{project}/_wiki/wikis/{wiki_id}?pagePath={page_path}"
                    
                    documents.append({
                        'content': content,
                        'source': web_url,
                        'filename': page_path.split('/')[-1] or 'Home',
                        'type': 'azure_wiki'
                    })
        
    except Exception as e:
        print(f"Error loading Azure DevOps wiki: {e}")
    
    return documents
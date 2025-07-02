import requests
from typing import List, Dict
from cache_utils import cache_crawled_content, get_cached_crawled_content
import json

def load_sharepoint_documents(site_urls: str, username: str, password: str) -> List[Dict[str, str]]:
    """Load documents from multiple SharePoint sites."""
    documents = []
    
    # Split comma-separated URLs
    urls = [url.strip() for url in site_urls.split(',') if url.strip()]
    
    for site_url in urls:
        print(f"Loading from SharePoint site: {site_url}")
        site_docs = _load_single_sharepoint_site(site_url, username, password)
        documents.extend(site_docs)
    
    return documents

def _load_single_sharepoint_site(site_url: str, username: str, password: str) -> List[Dict[str, str]]:
    """Load documents from a single SharePoint site."""
    documents = []
    
    try:
        # Try multiple SharePoint list names
        list_names = ['Documents', 'Shared Documents', 'Site Pages']
        
        for list_name in list_names:
            print(f"  Trying list: {list_name}")
            
            # SharePoint REST API endpoint
            api_url = f"{site_url}/_api/web/lists/getbytitle('{list_name}')/items"
            
            # Basic authentication with session
            session = requests.Session()
            session.auth = (username, password)
            
            headers = {
                'Accept': 'application/json;odata=nometadata',
                'Content-Type': 'application/json'
            }
            
            try:
                response = session.get(api_url, headers=headers, timeout=30)
                print(f"    Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('value', [])
                    print(f"    Found {len(items)} items")
                    
                    for item in items:
                        # For SharePoint pages/documents
                        title = item.get('Title', item.get('FileLeafRef', 'Unknown'))
                        
                        # Create a simple document entry
                        content = f"Title: {title}\n"
                        
                        # Add any text fields
                        for key, value in item.items():
                            if isinstance(value, str) and len(value) > 10 and key not in ['odata.etag', 'odata.type']:
                                content += f"{key}: {value}\n"
                        
                        if len(content) > 50:  # Only add if there's meaningful content
                            documents.append({
                                'content': content,
                                'source': f"{site_url}/_layouts/15/listform.aspx?PageType=4&ListId={item.get('Id', '')}",
                                'filename': title,
                                'type': 'sharepoint'
                            })
                    
                    if items:  # If we found items in this list, break
                        break
                        
                elif response.status_code == 401:
                    print(f"    Authentication failed for {site_url}")
                    break
                elif response.status_code == 404:
                    print(f"    List '{list_name}' not found")
                    continue
                else:
                    print(f"    Error: {response.status_code} - {response.text[:200]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"    Request error: {e}")
                continue
        
    except Exception as e:
        print(f"  Error loading SharePoint site {site_url}: {e}")
    
    return documents
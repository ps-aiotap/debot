import os
from dotenv import load_dotenv
from ingest.load_sharepoint import load_sharepoint_documents

load_dotenv()

print("Testing SharePoint connection...")

site_urls = os.getenv('SHAREPOINT_SITE_URLS', '')
username = os.getenv('SHAREPOINT_USERNAME', '')
password = os.getenv('SHAREPOINT_PASSWORD', '')

print(f"Site URLs: {site_urls}")
print(f"Username: {username}")
print(f"Password: {'*' * len(password) if password else 'Not set'}")

if site_urls and username and password:
    docs = load_sharepoint_documents(site_urls, username, password)
    print(f"\nTotal documents loaded: {len(docs)}")
    
    for i, doc in enumerate(docs[:3]):  # Show first 3
        print(f"\n{i+1}. {doc['filename']}")
        print(f"   Source: {doc['source']}")
        print(f"   Content preview: {doc['content'][:200]}...")
else:
    print("Missing SharePoint configuration in .env file")
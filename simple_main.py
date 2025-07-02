import os
import asyncio
import yaml
from typing import List, Dict
from dotenv import load_dotenv

from ingest.load_docs import load_documents
from ingest.load_pdfs import load_pdfs
from ingest.crawler import crawl_websites
from ingest.load_sharepoint import load_sharepoint_documents
from ingest.load_azure_wiki import load_azure_devops_wiki
from simple_embedding import SimpleEmbeddingService
from simple_qa import SimpleQAService
from database import create_tables

load_dotenv()
create_tables()

class SimpleChatbotApp:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.embedding_service = SimpleEmbeddingService()
        self.qa_service = SimpleQAService(self.embedding_service)
    
    async def ingest_all_data(self) -> List[Dict[str, str]]:
        """Ingest data from all sources."""
        all_documents = []
        
        # Load documents from DOCS_DIR
        if os.getenv('DOCS_DIR'):
            print("Loading documents from DOCS_DIR...")
            docs = load_documents(os.getenv('DOCS_DIR'))
            all_documents.extend(docs)
            print(f"Loaded {len(docs)} documents from DOCS_DIR")
        
        # Load documents from MDS_DIR
        if os.getenv('MDS_DIR'):
            print("Loading documents from MDS_DIR...")
            mds_docs = load_documents(os.getenv('MDS_DIR'))
            all_documents.extend(mds_docs)
            print(f"Loaded {len(mds_docs)} documents from MDS_DIR")
        
        # Load PDFs
        print("Loading PDFs...")
        pdfs = load_pdfs(os.getenv('PDF_DIR', './data/pdfs'))
        all_documents.extend(pdfs)
        print(f"Loaded {len(pdfs)} PDFs")
        
        # Crawl websites
        print("Crawling websites...")
        web_docs = await crawl_websites(
            self.config['crawling']['urls_to_crawl'],
            max_pages=self.config['crawling']['max_pages'],
            crawl_depth=self.config['crawling']['crawl_depth']
        )
        all_documents.extend(web_docs)
        print(f"Crawled {len(web_docs)} web pages")
        
        # Load SharePoint documents from multiple sites
        if os.getenv('SHAREPOINT_SITE_URLS'):
            print("Loading SharePoint documents...")
            sp_docs = load_sharepoint_documents(
                os.getenv('SHAREPOINT_SITE_URLS'),
                os.getenv('SHAREPOINT_USERNAME'),
                os.getenv('SHAREPOINT_PASSWORD')
            )
            all_documents.extend(sp_docs)
            print(f"Loaded {len(sp_docs)} SharePoint documents")
        
        # Load Azure DevOps Wiki
        if os.getenv('AZURE_DEVOPS_ORGANIZATION'):
            print("Loading Azure DevOps wiki...")
            wiki_docs = load_azure_devops_wiki(
                os.getenv('AZURE_DEVOPS_ORGANIZATION'),
                os.getenv('AZURE_DEVOPS_PROJECT'),
                os.getenv('AZURE_DEVOPS_WIKI_ID'),
                os.getenv('AZURE_DEVOPS_PAT_TOKEN')
            )
            all_documents.extend(wiki_docs)
            print(f"Loaded {len(wiki_docs)} Azure DevOps wiki pages")
        
        return all_documents
    
    async def initialize(self, force_reindex: bool = False):
        """Initialize the chatbot."""
        print("Starting data ingestion...")
        documents = await self.ingest_all_data()
        
        if documents:
            print(f"Adding {len(documents)} documents to vector store...")
            self.embedding_service.add_documents(documents)
            print("Documents added successfully!")
            return True
        else:
            print("No documents found.")
            return False
    
    def ask_question(self, question: str, use_cache: bool = True, source_filter: str = "all") -> Dict[str, any]:
        """Ask a question to the chatbot."""
        return self.qa_service.answer_question(question, use_cache, source_filter)

# CLI interface
def main():
    app = SimpleChatbotApp()
    
    success = asyncio.run(app.initialize())
    if not success:
        print("Failed to initialize chatbot.")
        return
    
    print("\nChatbot ready! Type 'quit' to exit.")
    while True:
        question = input("\nYour question: ")
        if question.lower() in ['quit', 'exit']:
            break
        
        response = app.ask_question(question)
        print(f"\nAnswer: {response['answer']}")
        if response['sources']:
            print(f"\nSources ({len(response['sources'])}):")
            for i, source in enumerate(response['sources'][:3], 1):
                print(f"{i}. {source['filename']} ({source['type']})")

if __name__ == "__main__":
    main()
import os
import asyncio
import yaml
from typing import List, Dict
from dotenv import load_dotenv

from ingest.load_docs import load_documents
from ingest.load_pdfs import load_pdfs
from ingest.crawler import crawl_websites
from ingest.load_excel import load_excel_testcases
from ingest.load_sharepoint import load_sharepoint_documents
from ingest.load_azure_wiki import load_azure_devops_wiki
from simple_embedding import SimpleEmbeddingService
from simple_qa import SimpleQAService
from database import create_tables
from persona_manager import PersonaManager

load_dotenv()
create_tables()

class SimpleChatbotApp:
    def __init__(self, config_path: str = "config.yaml", persona_manager: PersonaManager = None):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize persona manager
        self.persona_manager = persona_manager or PersonaManager()
        
        # Initialize services with persona manager
        self.embedding_service = SimpleEmbeddingService(config_path=config_path, persona_manager=self.persona_manager)
        self.qa_service = SimpleQAService(self.embedding_service)
        
    def set_persona(self, persona_name: str) -> bool:
        """Set the active persona."""
        success = self.persona_manager.set_persona(persona_name)
        if success:
            # Reinitialize collections for the new persona
            self.embedding_service._initialize_collections()
        return success
        
    def get_current_persona(self) -> str:
        """Get the name of the current persona."""
        return self.persona_manager.get_current_persona()
        
    def get_available_personas(self) -> List[str]:
        """Get list of available personas."""
        return self.persona_manager.get_available_personas()
    
    async def ingest_all_data(self) -> List[Dict[str, str]]:
        """Ingest data from persona-specific sources."""
        all_documents = []
        
        # Get persona-specific data directory
        persona_data_dir = self.persona_manager.get_data_dir()
        print(f"Loading data for persona '{self.persona_manager.get_current_persona()}' from {persona_data_dir}")
        

        # Load documents from persona docs directory
        docs_dir = os.path.join(persona_data_dir, 'docs')
        if os.path.exists(docs_dir):
            print(f"Loading documents from {docs_dir}...")
            docs = load_documents(docs_dir)
            all_documents.extend(docs)
            print(f"Loaded {len(docs)} documents from docs directory")
        
        # Load documents from persona mds directory
        mds_dir = os.path.join(persona_data_dir, 'mds')
        if os.path.exists(mds_dir):
            print(f"Loading markdown documents from {mds_dir}...")
            mds_docs = load_documents(mds_dir)
            all_documents.extend(mds_docs)
            print(f"Loaded {len(mds_docs)} markdown documents")
        
        # Load PDFs from persona pdfs directory
        pdfs_dir = os.path.join(persona_data_dir, 'pdfs')
        if os.path.exists(pdfs_dir):
            print(f"Loading PDFs from {pdfs_dir}...")
            pdfs = load_pdfs(pdfs_dir)
            all_documents.extend(pdfs)
            print(f"Loaded {len(pdfs)} PDFs")
        
        # Load Excel/CSV test cases from persona directory
        excel_dir = os.path.join(persona_data_dir, 'excel')
        if os.path.exists(excel_dir):
            print(f"Loading Excel/CSV test cases from {excel_dir}...")
            excel_docs = load_excel_testcases(excel_dir)
            all_documents.extend(excel_docs)
            print(f"Loaded {len(excel_docs)} test case documents")
        
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
    
    async def ask_question(self, question: str, use_cache: bool = True, source_filter: str = "all") -> Dict[str, any]:
        """Ask a question to the chatbot."""
        return await self.qa_service.answer_question(question, use_cache, source_filter)

# CLI interface
def main():
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="DeBot CLI")
    parser.add_argument("--persona", help="Persona to use", default=None)
    args = parser.parse_args()
    
    # Initialize persona manager
    persona_manager = PersonaManager()
    
    # Set persona if specified
    if args.persona:
        if not persona_manager.set_persona(args.persona):
            print(f"Warning: Persona '{args.persona}' not found. Using {persona_manager.get_current_persona()}.")
        else:
            print(f"Using persona: {args.persona}")
    
    # Initialize app with persona manager
    app = SimpleChatbotApp(persona_manager=persona_manager)
    
    # Show active collections
    print(f"Active collections: {persona_manager.get_collections()}")
    print(f"Prompt style: {persona_manager.get_prompt_style()}")
    
    success = asyncio.run(app.initialize())
    if not success:
        print("Failed to initialize chatbot.")
        return
    
    print("\nChatbot ready! Type 'quit' to exit.")
    while True:
        question = input("\nYour question: ")
        if question.lower() in ['quit', 'exit']:
            break
        
        response = asyncio.run(app.ask_question(question))
        print(f"\nAnswer: {response['answer']}")
        if response['sources']:
            print(f"\nSources ({len(response['sources'])}):")
            for i, source in enumerate(response['sources'][:3], 1):
                print(f"{i}. {source['filename']} ({source['type']})")

if __name__ == "__main__":
    main()
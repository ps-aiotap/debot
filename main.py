import os
import asyncio
import yaml
import json
from typing import List, Dict
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from ingest.load_docs import load_documents
from ingest.load_pdfs import load_pdfs
from ingest.crawler import crawl_websites
from embedding_service import EmbeddingService
from qa_service import QAService
from database import create_tables, get_db, Document, ChatHistory
from cache_utils import generate_content_hash

load_dotenv()
create_tables()

class ChatbotApp:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.embedding_service = EmbeddingService(config_path)
        self.qa_service = None
        self.index = None
    
    async def ingest_all_data(self) -> List[Dict[str, str]]:
        """Ingest data from all sources."""
        all_documents = []
        
        # Load documents
        print("Loading documents...")
        docs = load_documents(os.getenv('DOCS_DIR', './data/docs'))
        all_documents.extend(docs)
        print(f"Loaded {len(docs)} documents")
        
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
        
        # Save documents to PostgreSQL
        self._save_documents_to_db(all_documents)
        
        return all_documents
    
    def _save_documents_to_db(self, documents: List[Dict[str, str]]):
        """Save documents to PostgreSQL."""
        try:
            db = next(get_db())
            for doc in documents:
                content_hash = generate_content_hash(doc['content'])
                existing = db.query(Document).filter(Document.content_hash == content_hash).first()
                
                if not existing:
                    db_doc = Document(
                        content_hash=content_hash,
                        filename=doc['filename'],
                        source=doc['source'],
                        doc_type=doc['type'],
                        content=doc['content']
                    )
                    db.add(db_doc)
            
            db.commit()
            print("Documents saved to PostgreSQL")
        except Exception as e:
            print(f"Error saving documents to DB: {e}")
    
    async def initialize(self, force_reindex: bool = False):
        """Initialize the chatbot with data ingestion and indexing."""
        if force_reindex:
            print("Starting data ingestion...")
            documents = await self.ingest_all_data()
            
            if documents:
                print(f"Creating index from {len(documents)} documents...")
                self.index = self.embedding_service.create_index(documents)
                print("Index created successfully!")
            else:
                print("No documents found to index.")
                return False
        else:
            try:
                print("Loading existing index...")
                self.index = self.embedding_service.load_existing_index()
                print("Existing index loaded successfully!")
            except Exception as e:
                print(f"Could not load existing index: {e}")
                print("Creating new index...")
                return await self.initialize(force_reindex=True)
        
        # Initialize QA service
        self.qa_service = QAService(self.index)
        return True
    
    def ask_question(self, question: str, use_cache: bool = True, source_filter: str = "all") -> Dict[str, any]:
        """Ask a question to the chatbot."""
        if not self.qa_service:
            return {"error": "Chatbot not initialized. Please run initialize() first."}
        
        response = self.qa_service.answer_question(question, use_cache, source_filter)
        
        # Save to chat history
        try:
            db = next(get_db())
            chat_record = ChatHistory(
                question=question,
                answer=response.get('answer', ''),
                sources=json.dumps(response.get('sources', []))
            )
            db.add(chat_record)
            db.commit()
        except Exception as e:
            print(f"Error saving chat history: {e}")
        
        return response

# CLI interface for testing
async def main():
    app = ChatbotApp()
    
    # Initialize the app
    success = await app.initialize()
    if not success:
        print("Failed to initialize chatbot.")
        return
    
    print("\nChatbot ready! Type 'quit' to exit.")
    while True:
        question = input("\nYour question: ")
        if question.lower() in ['quit', 'exit']:
            break
        
        response = app.ask_question(question)
        if "error" in response:
            print(f"Error: {response['error']}")
        else:
            print(f"\nAnswer: {response['answer']}")
            if response['sources']:
                print(f"\nSources ({len(response['sources'])}):")
                for i, source in enumerate(response['sources'][:3], 1):
                    print(f"{i}. {source['filename']} ({source['type']})")

if __name__ == "__main__":
    asyncio.run(main())
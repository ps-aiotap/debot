import os
import yaml
from typing import List, Dict, Optional
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from cache_utils import get_cached_response, cache_response

class QAService:
    def __init__(self, index: VectorStoreIndex, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.index = index
        
        # Initialize Groq LLM
        from providers.groq_provider import GroqProvider
        self.llm_provider = GroqProvider(
            api_key=os.getenv('GROQ_API_KEY'),
            model=os.getenv('GROQ_MODEL')
        )
        
        # Create retriever
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=self.config['retrieval']['top_k']
        )
        
        # Note: Using simple retrieval without LlamaIndex query engine
        # Will generate answers using Groq provider directly
    
    def answer_question(self, question: str, use_cache: bool = True, source_filter: str = "all") -> Dict[str, any]:
        """Answer question using RAG with optional caching."""
        
        # Check cache if enabled
        if use_cache:
            cached_response = get_cached_response(
                question, 
                {"source_filter": source_filter}, 
                self.config['llm']['model']
            )
            if cached_response:
                return {
                    "answer": cached_response,
                    "sources": [],
                    "cached": True
                }
        
        # Retrieve relevant documents
        retrieved_nodes = self.retriever.retrieve(question)
        
        # Filter sources if specified
        if source_filter != "all":
            filtered_nodes = []
            for node in retrieved_nodes:
                node_type = node.metadata.get('type', '')
                if source_filter == "docs" and node_type in ['document', 'pdf']:
                    filtered_nodes.append(node)
                elif source_filter == "web" and node_type == 'web':
                    filtered_nodes.append(node)
            retrieved_nodes = filtered_nodes
        
        if not retrieved_nodes:
            return {
                "answer": "I couldn't find relevant information to answer your question.",
                "sources": [],
                "cached": False
            }
        
        # Generate answer using Groq
        context = "\n\n".join([node.text for node in retrieved_nodes[:3]])
        system_prompt = "You are a helpful assistant. Answer the question based on the provided context."
        user_prompt = f"Context: {context}\n\nQuestion: {question}"
        
        import asyncio
        answer = asyncio.run(self.llm_provider.generate_response(system_prompt, user_prompt))
        
        # Extract sources
        sources = []
        for node in retrieved_nodes:
            sources.append({
                "filename": node.metadata.get('filename', 'Unknown'),
                "source": node.metadata.get('source', 'Unknown'),
                "type": node.metadata.get('type', 'Unknown'),
                "content_preview": node.text[:200] + "..." if len(node.text) > 200 else node.text
            })
        
        # Cache the response
        if use_cache:
            cache_response(
                question,
                {"source_filter": source_filter},
                self.config['llm']['model'],
                answer,
                ttl=int(os.getenv('RESPONSE_CACHE_TTL', 3600))
            )
        
        return {
            "answer": answer,
            "sources": sources,
            "cached": False
        }
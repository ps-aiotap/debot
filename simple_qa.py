import os
import asyncio
from typing import Dict, List
from providers.groq_provider import GroqProvider
from simple_embedding import SimpleEmbeddingService
from cache_utils import get_cached_response, cache_response
from dotenv import load_dotenv

load_dotenv()

class SimpleQAService:
    def __init__(self, embedding_service: SimpleEmbeddingService):
        self.embedding_service = embedding_service
        self.llm_provider = GroqProvider(
            api_key=os.getenv('GROQ_API_KEY'),
            model=os.getenv('GROQ_MODEL'),
            config_path="config.yaml"
        )
    
    def answer_question(self, question: str, use_cache: bool = True, source_filter: str = "all") -> Dict[str, any]:
        """Answer question using RAG with Groq."""
        
        # Get current persona info
        persona = self.embedding_service.persona_manager.get_current_persona()
        prompt_style = self.embedding_service.persona_manager.get_prompt_style()
        
        # Check cache with persona info
        if use_cache:
            cached_response = get_cached_response(question, {"source_filter": source_filter, "persona": persona}, "groq")
            if cached_response:
                return {"answer": cached_response, "sources": [], "cached": True}
        
        # Search for relevant documents
        results = self.embedding_service.search(question, n_results=5)
        
        # Filter by source type
        if source_filter != "all":
            filtered_results = []
            for result in results:
                doc_type = result['metadata'].get('type', '')
                if source_filter == "docs" and doc_type in ['document', 'pdf']:
                    filtered_results.append(result)
                elif source_filter == "web" and doc_type == 'web':
                    filtered_results.append(result)
            results = filtered_results
        
        if not results:
            return {"answer": "I couldn't find relevant information to answer your question.", "sources": [], "cached": False}
        
        # Generate answer using Groq with persona-specific prompt style
        context = "\n\n".join([result['content'][:500] for result in results[:3]])
        
        # Adjust system prompt based on persona style
        if prompt_style == "gentle":
            system_prompt = "You are a helpful and empathetic assistant. Answer the question based on the provided context using a warm, supportive tone."
        elif prompt_style == "direct":
            system_prompt = "You are a direct and concise assistant. Answer the question based on the provided context with clear, straightforward information."
        else:  # balanced
            system_prompt = "You are a helpful assistant. Answer the question based on the provided context."
            
        user_prompt = f"Context: {context}\n\nQuestion: {question}"
        
        try:
            answer = asyncio.run(self.llm_provider.generate_response(system_prompt, user_prompt))
        except Exception as e:
            answer = f"Error generating response: {str(e)}"
        
        # Extract sources
        sources = []
        for result in results:
            sources.append({
                "filename": result['metadata'].get('filename', 'Unknown'),
                "source": result['metadata'].get('source', 'Unknown'),
                "type": result['metadata'].get('type', 'Unknown'),
                "content_preview": result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            })
        
        # Cache response with persona info
        if use_cache:
            cache_response(question, {"source_filter": source_filter, "persona": persona}, "groq", answer)
        
        return {"answer": answer, "sources": sources, "cached": False}
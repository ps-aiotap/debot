"""Explainability features for DeBot RAG system."""

import re
from typing import List, Dict, Any
from sentence_transformers import util
import numpy as np

class ExplainabilityService:
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
    
    def explain_retrieval(self, query: str, retrieved_docs: List[Dict], query_embedding: np.ndarray) -> Dict[str, Any]:
        """Explain why documents were retrieved for a query."""
        explanations = []
        
        for doc in retrieved_docs:
            explanation = self._explain_single_doc(query, doc, query_embedding)
            explanations.append(explanation)
        
        return {
            "query": query,
            "total_docs_retrieved": len(retrieved_docs),
            "explanations": explanations,
            "potential_issues": self._identify_issues(query, explanations)
        }
    
    def _explain_single_doc(self, query: str, doc: Dict, query_embedding: np.ndarray) -> Dict[str, Any]:
        """Explain why a single document was retrieved."""
        doc_text = doc.get('text', '')
        doc_embedding = doc.get('embedding')
        
        # Calculate similarity score
        similarity = float(util.cos_sim(query_embedding, doc_embedding)[0][0]) if doc_embedding is not None else 0.0
        
        # Find keyword matches
        query_words = set(query.lower().split())
        doc_words = set(doc_text.lower().split())
        keyword_matches = query_words.intersection(doc_words)
        
        # Extract location mentions
        query_locations = self._extract_locations(query)
        doc_locations = self._extract_locations(doc_text)
        location_mismatch = bool(query_locations and doc_locations and not query_locations.intersection(doc_locations))
        
        return {
            "document": doc.get('source', 'Unknown'),
            "similarity_score": round(similarity, 3),
            "keyword_matches": list(keyword_matches),
            "query_locations": list(query_locations),
            "doc_locations": list(doc_locations),
            "location_mismatch": location_mismatch,
            "relevance_reason": self._generate_relevance_reason(keyword_matches, similarity, location_mismatch)
        }
    
    def _extract_locations(self, text: str) -> set:
        """Extract location names from text."""
        # Simple location extraction - can be enhanced with NER
        location_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized words (potential place names)
        ]
        
        locations = set()
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            # Filter common non-location words
            non_locations = {'Floor', 'Space', 'Index', 'Policy', 'Phase', 'Authority', 'Airport', 'Fire', 'Green', 'Zone', 'Heritage', 'Premium', 'Effective', 'Date', 'June', 'MIDC', 'SPA', 'UDCPR', 'TDR', 'FSI', 'NOC', 'AAI', 'IT', 'ITES'}
            locations.update([m for m in matches if m not in non_locations and len(m) > 2])
        
        return locations
    
    def _generate_relevance_reason(self, keyword_matches: List[str], similarity: float, location_mismatch: bool) -> str:
        """Generate human-readable explanation for document relevance."""
        reasons = []
        
        if similarity > 0.7:
            reasons.append(f"High semantic similarity ({similarity:.2f})")
        elif similarity > 0.5:
            reasons.append(f"Moderate semantic similarity ({similarity:.2f})")
        else:
            reasons.append(f"Low semantic similarity ({similarity:.2f})")
        
        if keyword_matches:
            reasons.append(f"Keyword matches: {', '.join(keyword_matches[:3])}")
        
        if location_mismatch:
            reasons.append("⚠️ Location mismatch detected")
        
        return "; ".join(reasons)
    
    def _identify_issues(self, query: str, explanations: List[Dict]) -> List[str]:
        """Identify potential retrieval issues."""
        issues = []
        
        # Check for location mismatches
        location_mismatches = [exp for exp in explanations if exp.get('location_mismatch')]
        if location_mismatches:
            issues.append(f"Location mismatch in {len(location_mismatches)} documents")
        
        # Check for low similarity scores
        low_similarity = [exp for exp in explanations if exp.get('similarity_score', 0) < 0.3]
        if low_similarity:
            issues.append(f"{len(low_similarity)} documents have very low relevance")
        
        return issues
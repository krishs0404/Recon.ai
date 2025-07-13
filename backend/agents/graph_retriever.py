from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json

class GraphRetriever:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.content_chunks = []
        self.chunk_embeddings = None
        
    def retrieve_relevant_context(
        self, 
        content: List[Dict[str, Any]], 
        graph: Dict[str, Any],
        query: Optional[str] = None,
        max_chunks: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context using GraphRAG-style approach.
        
        Args:
            content: List of content updates
            graph: Entity graph with nodes and edges
            query: Optional query to focus retrieval
            max_chunks: Maximum number of chunks to return
            
        Returns:
            Dict with relevant chunks and graph paths
        """
        # Prepare content chunks
        self._prepare_chunks(content)
        
        # Get graph-based relevance
        graph_relevant = self._get_graph_relevant_content(graph, query)
        
        # Get semantic relevance
        semantic_relevant = self._get_semantic_relevant_content(query, max_chunks)
        
        # Combine and rank results
        combined_context = self._combine_contexts(graph_relevant, semantic_relevant)
        
        return {
            "relevant_chunks": combined_context["chunks"],
            "graph_paths": combined_context["graph_paths"],
            "relevance_scores": combined_context["scores"],
            "retrieval_method": "graphrag_hybrid"
        }
    
    def _prepare_chunks(self, content: List[Dict[str, Any]]):
        """Prepare content into searchable chunks."""
        self.content_chunks = []
        
        for item in content:
            # Create chunks from title and snippet
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            source = item.get('source', '')
            date = item.get('date', '')
            
            # Split into smaller chunks if needed
            chunks = self._split_text(f"{title} {snippet}")
            
            for i, chunk in enumerate(chunks):
                self.content_chunks.append({
                    "text": chunk,
                    "source": source,
                    "date": date,
                    "title": title,
                    "chunk_id": f"{source}_{i}",
                    "metadata": {
                        "source": source,
                        "date": date,
                        "title": title
                    }
                })
        
        # Create TF-IDF embeddings
        if self.content_chunks:
            texts = [chunk["text"] for chunk in self.content_chunks]
            self.chunk_embeddings = self.vectorizer.fit_transform(texts)
    
    def _split_text(self, text: str, max_length: int = 200) -> List[str]:
        """Split text into chunks of reasonable size."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_length and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks if chunks else [text]
    
    def _get_graph_relevant_content(
        self, 
        graph: Dict[str, Any], 
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get content relevant based on graph structure."""
        relevant_chunks = []
        graph_paths = []
        
        # Extract entities from query if provided
        query_entities = []
        if query:
            query_entities = self._extract_entities_from_query(query)
        
        # Find content mentioning graph entities
        graph_entities = [node["id"] for node in graph.get("nodes", [])]
        
        for chunk in self.content_chunks:
            chunk_text = chunk["text"].lower()
            relevance_score = 0
            
            # Check for graph entities in chunk
            for entity in graph_entities:
                if entity.lower() in chunk_text:
                    relevance_score += 1
            
            # Check for query entities
            for entity in query_entities:
                if entity.lower() in chunk_text:
                    relevance_score += 2  # Higher weight for query entities
            
            if relevance_score > 0:
                relevant_chunks.append({
                    **chunk,
                    "relevance_score": relevance_score,
                    "relevance_type": "graph_entity"
                })
        
        # Sort by relevance score
        relevant_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return {
            "chunks": relevant_chunks[:10],  # Top 10 graph-relevant chunks
            "graph_paths": graph_paths
        }
    
    def _get_semantic_relevant_content(self, query: Optional[str], max_chunks: int) -> Dict[str, Any]:
        """Get content relevant based on semantic similarity."""
        if not query or not self.chunk_embeddings is not None:
            return {"chunks": [], "scores": []}
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.chunk_embeddings).flatten()
        
        # Get top chunks
        top_indices = np.argsort(similarities)[::-1][:max_chunks]
        
        relevant_chunks = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                chunk = self.content_chunks[idx].copy()
                chunk["relevance_score"] = float(similarities[idx])
                chunk["relevance_type"] = "semantic"
                relevant_chunks.append(chunk)
        
        return {
            "chunks": relevant_chunks,
            "scores": similarities[top_indices].tolist()
        }
    
    def _combine_contexts(
        self, 
        graph_relevant: Dict[str, Any], 
        semantic_relevant: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine graph-based and semantic retrieval results."""
        combined_chunks = []
        seen_chunk_ids = set()
        
        # Add graph-relevant chunks first (higher priority)
        for chunk in graph_relevant["chunks"]:
            if chunk["chunk_id"] not in seen_chunk_ids:
                combined_chunks.append(chunk)
                seen_chunk_ids.add(chunk["chunk_id"])
        
        # Add semantic-relevant chunks
        for chunk in semantic_relevant["chunks"]:
            if chunk["chunk_id"] not in seen_chunk_ids:
                combined_chunks.append(chunk)
                seen_chunk_ids.add(chunk["chunk_id"])
        
        # Sort by relevance score
        combined_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return {
            "chunks": combined_chunks[:10],  # Top 10 combined chunks
            "graph_paths": graph_relevant["graph_paths"],
            "scores": [chunk["relevance_score"] for chunk in combined_chunks[:10]]
        }
    
    def _extract_entities_from_query(self, query: str) -> List[str]:
        """Extract potential entities from query text."""
        # Simple entity extraction using capitalization and common patterns
        entities = []
        
        # Capitalized words (potential proper nouns)
        words = query.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                entities.append(word)
        
        # Company patterns
        company_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company|Co)\b',
            r'\b[A-Z][A-Z]+\b',  # Acronyms
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, query)
            entities.extend(matches)
        
        return list(set(entities))  # Remove duplicates
    
    def get_context_summary(self, relevant_chunks: List[Dict[str, Any]]) -> str:
        """Create a summary of the retrieved context."""
        if not relevant_chunks:
            return "No relevant context found."
        
        # Extract key information from top chunks
        sources = set()
        dates = set()
        key_phrases = []
        
        for chunk in relevant_chunks[:5]:  # Top 5 chunks
            sources.add(chunk.get("source", "Unknown"))
            if chunk.get("date"):
                dates.add(chunk["date"])
            
            # Extract key phrases (simple approach)
            text = chunk["text"]
            words = text.split()
            if len(words) > 5:
                key_phrases.append(" ".join(words[:10]) + "...")
        
        summary_parts = []
        
        if sources:
            summary_parts.append(f"Sources: {', '.join(sources)}")
        
        if dates:
            summary_parts.append(f"Time period: {', '.join(sorted(dates))}")
        
        if key_phrases:
            summary_parts.append(f"Key updates: {' '.join(key_phrases[:3])}")
        
        return " | ".join(summary_parts)

# Convenience function for easy import
async def retrieve_relevant_context(
    content: List[Dict[str, Any]], 
    graph: Dict[str, Any],
    query: Optional[str] = None,
    max_chunks: int = 5
) -> Dict[str, Any]:
    """Retrieve relevant context using GraphRAG approach."""
    retriever = GraphRetriever()
    return retriever.retrieve_relevant_context(content, graph, query, max_chunks) 
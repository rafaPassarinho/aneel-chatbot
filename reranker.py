# reranker.py
from sentence_transformers import CrossEncoder
from typing import List, Tuple, Dict, Any

class PortugueseReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize Portuguese reranker.
        
        Available models:
        - "cross-encoder/ms-marco-MiniLM-L-6-v2" (multilingual, good performance)
        - "cross-encoder/ms-marco-MiniLM-L-12-v2" (larger, better performance)
        - "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1" (specifically trained on multilingual data)
        """
        print(f"Carregando modelo de reranking: {model_name}...")
        self.model = CrossEncoder(model_name)
        print("Modelo de reranking carregado com sucesso!")
    
    def rerank(
        self, 
        query: str, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]] = None,
        top_k: int = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Rerank documents based on query relevance.
        
        Args:
            query: User query
            documents: List of retrieved documents
            metadatas: List of metadata dictionaries corresponding to documents
            top_k: Number of top results to return (if None, returns all ranked)
        
        Returns:
            List of tuples (document, score, metadata) sorted by relevance score
        """
        if not documents:
            return []
        
        # Create query-document pairs for cross encoder
        pairs = [(query, doc) for doc in documents]
        
        # Get relevance scores
        scores = self.model.predict(pairs)
        
        # Combine documents with scores and metadata
        results = []
        for i, (doc, score) in enumerate(zip(documents, scores)):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            results.append((doc, float(score), metadata))
        
        # Sort by relevance score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results if specified
        if top_k:
            results = results[:top_k]
        
        return results

# Global reranker instance (lazy loading)
_reranker_instance = None

def get_reranker() -> PortugueseReranker:
    """Get or create global reranker instance."""
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = PortugueseReranker()
    return _reranker_instance

def rerank_documents(
    query: str,
    documents: List[str],
    metadatas: List[Dict[str, Any]] = None,
    top_k: int = 5
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Convenience function to rerank documents and return separate lists.
    
    Returns:
        Tuple of (reranked_documents, reranked_metadatas)
    """
    reranker = get_reranker()
    reranked_results = reranker.rerank(query, documents, metadatas, top_k)
    
    reranked_docs = [result[0] for result in reranked_results]
    reranked_metas = [result[2] for result in reranked_results]
    
    return reranked_docs, reranked_metas
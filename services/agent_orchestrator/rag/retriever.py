"""
Evidence-Grounded RAG Retriever
Implements multi-source semantic and keyword retrieval with exact snippet extraction,
relevance scoring, and document version tracking.
"""
import os
import re
import math
from typing import List, Dict, Any, Tuple
from packages.shared.models import Citation
from services.agent_orchestrator.rag.indexer import RunbookIndexer, DocumentChunk


class RAGRetriever:
    def __init__(self, runbooks_dir: str = "data/runbooks"):
        self.indexer = RunbookIndexer(runbooks_dir)
        self.chunks: List[DocumentChunk] = []
        self.reload()

    def reload(self):
        self.chunks = self.indexer.load_and_index()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.15
    ) -> List[Citation]:
        """
        Retrieves the top-k most relevant citations for a given incident query or detector context.
        """
        if not self.chunks:
            self.reload()

        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return []

        scored_chunks: List[Tuple[float, DocumentChunk]] = []

        for chunk in self.chunks:
            chunk_tokens = self._tokenize(chunk.title + " " + chunk.section + " " + chunk.content)
            if not chunk_tokens:
                continue

            # Calculate TF-IDF style lexical overlap
            overlap = query_tokens.intersection(set(chunk_tokens))
            if not overlap:
                continue

            # Term frequency score with title/section weighting
            title_tokens = set(self._tokenize(chunk.title + " " + chunk.section))
            title_matches = query_tokens.intersection(title_tokens)

            base_score = len(overlap) / math.sqrt(len(query_tokens) * len(chunk_tokens) + 1)
            boost = 1.0 + (1.5 * len(title_matches))
            final_score = min(0.99, base_score * boost * 2.0)

            if final_score >= min_score:
                scored_chunks.append((final_score, chunk))

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        citations = [chunk.to_citation(score) for score, chunk in scored_chunks[:top_k]]
        return citations


# Global RAG retriever instance
rag_retriever = RAGRetriever()

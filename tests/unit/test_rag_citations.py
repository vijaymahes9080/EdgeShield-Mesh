"""
Unit Tests for RAG Ingestion, Chunking, Citations, and Document Hashes
"""
import pytest
from services.agent_orchestrator.rag.indexer import RunbookIndexer
from services.agent_orchestrator.rag.retriever import RAGRetriever


def test_runbook_chunking_and_metadata():
    indexer = RunbookIndexer(runbooks_dir="data/runbooks")
    chunks = indexer.load_and_index()
    assert len(chunks) > 0

    doc_ids = {c.document_id for c in chunks}
    assert "RB-001" in doc_ids
    assert "RB-002" in doc_ids
    assert "RB-003" in doc_ids
    assert "RB-004" in doc_ids
    assert "RB-005" in doc_ids

    # Verify each chunk has non-empty hash, section, title, and version
    for c in chunks:
        assert len(c.chunk_hash) == 64
        assert c.version != ""
        assert c.title != ""
        assert c.section != ""


def test_rag_citation_retrieval():
    retriever = RAGRetriever(runbooks_dir="data/runbooks")
    
    # Query for unauthorized MQTT topic access
    citations = retriever.retrieve("unauthorized topic publish actuator command", top_k=2)
    assert len(citations) > 0
    top_citation = citations[0]
    assert "RB-001" in top_citation.document_id or "RB-005" in top_citation.document_id
    assert top_citation.relevance_score > 0.0
    assert len(top_citation.snippet) > 10
    assert top_citation.version != ""
    assert len(top_citation.doc_hash) == 64


def test_impossible_value_citation_retrieval():
    retriever = RAGRetriever(runbooks_dir="data/runbooks")
    citations = retriever.retrieve("impossible value soil moisture probe recalibration", top_k=2)
    assert len(citations) > 0
    assert any(c.document_id == "RB-002" for c in citations)
